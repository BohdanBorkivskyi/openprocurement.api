# -*- coding: utf-8 -*-
from decimal import Decimal
from datetime import timedelta
from zope.interface import implementer
from iso8601 import parse_date
from pyramid.security import Allow
from schematics.types import StringType, FloatType, IntType, URLType, BooleanType
from schematics.types.compound import ModelType
from schematics.types.serializable import serializable
from schematics.exceptions import ValidationError
from schematics.transforms import whitelist, blacklist
from barbecue import vnmax
from esculator import npv, escp
from openprocurement.api.utils import get_now
from openprocurement.api.constants import TZ
from openprocurement.api.validation import (
    validate_cpv_group, validate_items_uniq
)
from openprocurement.api.models import (
    Value, Model, SifterListType,
    ListType, Period, Address, PeriodEndRequired,
    IsoDateTimeType, DecimalType
)
from openprocurement.api.models import (
    plain_role, listing_role,
    schematics_default_role
)
from openprocurement.tender.core.models import (
    Tender as BaseTender, EnquiryPeriod, PeriodStartEndRequired,
    Question, Feature as BaseFeature, Guarantee, BaseLot,
    FeatureValue as BaseFeatureValue
)
from openprocurement.tender.core.models import (
    get_tender, view_role, auction_view_role, auction_post_role,
    auction_patch_role, enquiries_role, chronograph_role,
    chronograph_view_role, Administrator_role,
    embedded_lot_role, default_lot_role,
    validate_features_uniq, validate_lots_uniq,
    bids_validation_wrapper, validate_values_uniq
)
from openprocurement.tender.core.utils import (
    calc_auction_end_time,
    calculate_business_date,
    has_unanswered_questions,
    has_unanswered_complaints
)
from openprocurement.tender.core.constants import (
    CPV_ITEMS_CLASS_FROM
)
from openprocurement.tender.openua.models import (
    Tender as OpenUATender
)
from openprocurement.tender.openua.utils import (
    calculate_normalized_date
)
from openprocurement.tender.openua.constants import (
    COMPLAINT_SUBMIT_TIME,
    ENQUIRY_STAND_STILL_TIME,
    AUCTION_PERIOD_TIME,
)
from openprocurement.tender.openeu.models import (
    IAboveThresholdEUTender, Bid as BaseEUBid,
    LotValue as BaseLotValue,
    ComplaintModelType, Item as BaseItem, TenderAuctionPeriod,
    ProcuringEntity, Award as BaseEUAward, Complaint,
    Cancellation, OpenEUDocument as Document,
    Qualification, LotAuctionPeriod,
    Contract as BaseEUContract, BidModelType
)
from openprocurement.tender.openeu.models import (
    edit_role_eu, create_role_eu, pre_qualifications_role
)
from openprocurement.tender.openeu.constants import (
    TENDERING_DURATION, QUESTIONS_STAND_STILL, TENDERING_DAYS
)
from openprocurement.tender.esco.utils import to_decimal


view_value_role_esco = whitelist('amount', 'amountPerformance', 'yearlyPaymentsPercentage',
                                 'annualCostsReduction', 'contractDuration',
                                 'currency', 'valueAddedTaxIncluded')


class IESCOTender(IAboveThresholdEUTender):
    """ Marker interface for ESCO tenders """


class Lot(BaseLot):
    class Options:
        roles = {
            'create': whitelist('id', 'title', 'title_en', 'title_ru', 'description',
                                'description_en', 'description_ru', 'guarantee',
                                'minimalStepPercentage', 'fundingKind',
                                'yearlyPaymentsPercentageRange'),
            'edit': whitelist('title', 'title_en', 'title_ru', 'description', 'description_en',
                              'description_ru', 'guarantee', 'minimalStepPercentage', 'fundingKind',
                              'yearlyPaymentsPercentageRange'),
            'embedded': embedded_lot_role,
            'view': default_lot_role,
            'default': default_lot_role,
            'auction_view': default_lot_role,
            'auction_patch': whitelist('id', 'auctionUrl'),
            'chronograph': whitelist('id', 'auctionPeriod'),
            'chronograph_view': whitelist('id', 'auctionPeriod', 'numberOfBids', 'status'),
        }

    minValue = ModelType(Value, required=False, default={'amount': 0, 'currency': 'UAH',
                                                         'valueAddedTaxIncluded': True})
    minimalStep = ModelType(Value, required=False)  # Not required, blocked for create/edit, since we have minimalStepPercentage in esco
    minimalStepPercentage = DecimalType(required=True,
                                        min_value=Decimal('0.005'), max_value=Decimal('0.03'))
    auctionPeriod = ModelType(LotAuctionPeriod, default={})
    auctionUrl = URLType()
    guarantee = ModelType(Guarantee)
    fundingKind = StringType(choices=['budget', 'other'], required=True, default='other')
    yearlyPaymentsPercentageRange = DecimalType(required=True, default=Decimal('0.8'),
                                                min_value=Decimal('0'), max_value=Decimal('1'))

    @serializable
    def numberOfBids(self):
        """A property that is serialized by schematics exports."""
        bids = [
            bid
            for bid in self.__parent__.bids
            if self.id in [i.relatedLot for i in bid.lotValues if i.status in ["active", "pending"]] and bid.status in ["active", "pending"]
        ]
        return len(bids)

    @serializable(serialized_name="guarantee", serialize_when_none=False, type=ModelType(Guarantee))
    def lot_guarantee(self):
        if self.guarantee:
            currency = self.__parent__.guarantee.currency if self.__parent__.guarantee else self.guarantee.currency
            return Guarantee(dict(amount=self.guarantee.amount, currency=currency))

    @serializable(serialized_name="fundingKind")
    def lot_fundingKind(self):
        return self.__parent__.fundingKind  # if self.__parent__.fundingKind else self.fundingKind

    @serializable(serialized_name="minimalStep", type=ModelType(Value), serialize_when_none=False)
    def lot_minimalStep(self):
        pass
        # return Value(dict(amount=self.minimalStep.amount,
        #                   currency=self.__parent__.minimalStep.currency,
        #                   valueAddedTaxIncluded=self.__parent__.minimalStep.valueAddedTaxIncluded))

    @serializable(serialized_name="minValue", type=ModelType(Value))
    def lot_minValue(self):
        return Value(dict(amount=self.minValue.amount,
                          currency=self.__parent__.minValue.currency,
                          valueAddedTaxIncluded=self.__parent__.minValue.valueAddedTaxIncluded))

    def validate_yearlyPaymentsPercentageRange(self, data, value):
        if data['fundingKind'] == 'other' and value != Decimal('0.8'):
            raise ValidationError('when fundingKind is other, yearlyPaymentsPercentageRange should be equal 0.8')
        if data['fundingKind'] == 'budget' and (value > Decimal('0.8') or value < Decimal('0')):
            raise ValidationError('when fundingKind is budget, yearlyPaymentsPercentageRange should be less or equal 0.8, and more or equal 0')


class ContractDuration(Model):
    years = IntType(required=True, min_value=0, max_value=15)
    days = IntType(required=False, min_value=0, max_value=364, default=0)

    def validate_days(self, data, days):
        if data['years'] == 15 and days > 0:
            raise ValidationError('max contract duration 15 years')
        if data['years'] == 0 and days < 1:
            raise ValidationError('min contract duration 1 day')


class BaseESCOValue(Value):
    class Options:
        roles = {
            'embedded': view_value_role_esco,
            'view': view_value_role_esco,
            'create': whitelist('amount', 'amount_escp', 'amountPerformance',
                                'amountPerformance_npv', 'yearlyPaymentsPercentage',
                                'annualCostsReduction', 'contractDuration',
                                'currency', 'valueAddedTaxIncluded'),
            'edit': whitelist('amount', 'amount_escp', 'amountPerformance', 'amountPerformance_npv',
                              'yearlyPaymentsPercentage', 'annualCostsReduction', 'contractDuration',
                              'currency', 'valueAddedTaxIncluded'),
            'auction_view': whitelist('amountPerformance', 'yearlyPaymentsPercentage',
                                      'annualCostsReduction', 'contractDuration',
                                      'currency', 'valueAddedTaxIncluded'),
            'auction_post': whitelist('amount_escp', 'amountPerformance_npv',
                                      'yearlyPaymentsPercentage', 'contractDuration'),
            'active.qualification': view_value_role_esco,
            'active.awarded': view_value_role_esco,
            'complete': view_value_role_esco,
            'unsuccessful': view_value_role_esco,
            'cancelled': view_value_role_esco,
        }

    amount = DecimalType(min_value=Decimal('0'), required=False, precision=-2)  # Calculated energy service contract value.
    amountPerformance = DecimalType(required=False, precision=-2)  # Calculated energy service contract performance indicator
    yearlyPaymentsPercentage = DecimalType(required=True)  # The percentage of annual payments in favor of Bidder
    annualCostsReduction = ListType(DecimalType(), required=True)  # Buyer's annual costs reduction
    contractDuration = ModelType(ContractDuration, required=True)


class ESCOValue(BaseESCOValue):

    @serializable(serialized_name='amountPerformance', type=DecimalType(precision=-2))
    def amountPerformance_npv(self):
        """ Calculated energy service contract performance indicator """
        return to_decimal(npv(
            self.contractDuration.years,
            self.contractDuration.days,
            self.yearlyPaymentsPercentage,
            self.annualCostsReduction,
            get_tender(self).noticePublicationDate,
            get_tender(self).NBUdiscountRate))

    @serializable(serialized_name='amount', type=DecimalType(precision=-2))
    def amount_escp(self):
        return to_decimal(escp(
            self.contractDuration.years,
            self.contractDuration.days,
            self.yearlyPaymentsPercentage,
            self.annualCostsReduction,
            get_tender(self).noticePublicationDate))

    def validate_annualCostsReduction(self, data, value):
        if len(value) != 21:
            raise ValidationError('annual costs reduction should be set for 21 period')

    def validate_yearlyPaymentsPercentage(self, data, value):
        if get_tender(data['__parent__']).fundingKind == 'other' and (value < Decimal('0.8') or value > Decimal('1')):
            raise ValidationError('yearlyPaymentsPercentage should be greater than 0.8 and less than 1')
        if get_tender(data['__parent__']).fundingKind == 'budget'and (value < Decimal('0') or value > get_tender(data['__parent__']).yearlyPaymentsPercentageRange):
            raise ValidationError('yearlyPaymentsPercentage should be greater than 0 and less than {}'.format(get_tender(data['__parent__']).yearlyPaymentsPercentageRange))


class LotValue(BaseLotValue):

    value = ModelType(ESCOValue, required=True)

    def validate_value(self, data, value):
        if value and isinstance(data['__parent__'], Model) and (data['__parent__'].status not in ('invalid', 'deleted', 'draft')) and data['relatedLot']:
            lots = [i for i in get_tender(data['__parent__']).lots if i.id == data['relatedLot']]
            if not lots:
                return
            lot = lots[0]
            if lot.get('minValue').currency != value.currency:
                raise ValidationError(u"currency of bid should be identical to currency of minValue of lot")
            if lot.get('minValue').valueAddedTaxIncluded != value.valueAddedTaxIncluded:
                raise ValidationError(u"valueAddedTaxIncluded of bid should be identical to valueAddedTaxIncluded of minValue of lot")


class Item(BaseItem):
    """A good, service, or work to be contracted."""
    class Options:
        roles = {
            'edit': blacklist("quantity", "deliveryDate"),
            'edit_draft': blacklist("quantity", "deliveryDate"),
            'edit_active.tendering': blacklist("quantity", "deliveryDate"),
            "create": blacklist("quantity", "deliveryDate")
        }
    deliveryAddress = ModelType(Address, required=False)
    deliveryDate = ModelType(PeriodEndRequired, required=False)
    quantity = IntType(required=False)


class Contract(BaseEUContract):
    """ESCO contract model"""
    class Options:
        roles = {
            'edit': blacklist('id', 'documents', 'date', 'awardID', 'suppliers',
                              'items', 'contractID', 'value'),
        }

    value = ModelType(BaseESCOValue)
    items = ListType(ModelType(Item))


class Award(BaseEUAward):
    """ESCO award model"""

    value = ModelType(BaseESCOValue)
    items = ListType(ModelType(Item))


class Bid(BaseEUBid):
    """ ESCO bid model """

    value = ModelType(ESCOValue)
    lotValues = ListType(ModelType(LotValue), default=list())
    selfQualified = BooleanType(required=False)
    selfEligible = BooleanType(required=False)

    @bids_validation_wrapper
    def validate_value(self, data, value):
        if isinstance(data['__parent__'], Model):
            tender = data['__parent__']
            if tender.lots:
                if value:
                    raise ValidationError(u'value should be posted for each lot of bid')
            else:
                if not value:
                    raise ValidationError(u'This field is required.')
                if tender.get('minValue').currency != value.currency:
                    raise ValidationError(u"currency of bid should be identical to currency of minValue of tender")
                if tender.get('minValue').valueAddedTaxIncluded != value.valueAddedTaxIncluded:
                    raise ValidationError(u"valueAddedTaxIncluded of bid should be identical to valueAddedTaxIncluded of minValue of tender")


class FeatureValue(BaseFeatureValue):
    value = FloatType(required=True, min_value=0.0, max_value=0.25)


class Feature(BaseFeature):
    enum = ListType(ModelType(FeatureValue), default=list(), min_size=1,
                    validators=[validate_values_uniq])


@implementer(IESCOTender)
class Tender(BaseTender):
    """ ESCO Tender model """
    class Options:
        roles = {
            'plain': plain_role,
            'create': create_role_eu + blacklist('minValue', 'tender_minValue', 'minimalStep',
                                                 'tender_minimalStep', 'noticePublicationDate',
                                                 'tender_noticePublicationDate'),
            'edit': edit_role_eu + blacklist('minValue', 'tender_minValue', 'minimalStep',
                                             'tender_minimalStep', 'noticePublicationDate',
                                             'tender_noticePublicationDate'),
            'edit_draft': edit_role_eu + blacklist('minValue', 'tender_minValue', 'minimalStep',
                                                   'tender_minimalStep', 'noticePublicationDate',
                                                   'tender_noticePublicationDate'),
            'edit_active.tendering': edit_role_eu + blacklist('minValue', 'tender_minValue',
                                                              'minimalStep', 'tender_minimalStep',
                                                              'noticePublicationDate',
                                                              'tender_noticePublicationDate'),
            'edit_active.pre-qualification': whitelist('status'),
            'edit_active.pre-qualification.stand-still': whitelist(),
            'edit_active.auction': whitelist(),
            'edit_active.qualification': whitelist(),
            'edit_active.awarded': whitelist(),
            'edit_complete': whitelist(),
            'edit_unsuccessful': whitelist(),
            'edit_cancelled': whitelist(),
            'view': view_role,
            'listing': listing_role,
            'auction_view': auction_view_role + whitelist('NBUdiscountRate', 'minimalStepPercentage',
                                                          'yearlyPaymentsPercentageRange',
                                                          'fundingKind', 'procurementMethodType',
                                                          'noticePublicationDate'),
            'auction_post': auction_post_role,
            'auction_patch': auction_patch_role,
            'draft': enquiries_role,
            'active.tendering': enquiries_role,
            'active.pre-qualification': pre_qualifications_role,
            'active.pre-qualification.stand-still': pre_qualifications_role,
            'active.auction': pre_qualifications_role,
            'active.qualification': view_role,
            'active.awarded': view_role,
            'complete': view_role,
            'unsuccessful': view_role,
            'cancelled': view_role,
            'chronograph': chronograph_role,
            'chronograph_view': chronograph_view_role,
            'Administrator': Administrator_role,
            'default': schematics_default_role,
            'contracting': whitelist('doc_id', 'owner'),
        }

    procurementMethodType = StringType(default="esco")
    title_en = StringType(required=True, min_length=1)

    items = ListType(ModelType(Item), required=True, min_size=1,
                     validators=[validate_cpv_group, validate_items_uniq])  # The goods and services to be purchased, broken into line items wherever possible. Items should not be duplicated, but a quantity of 2 specified instead.
    minValue = ModelType(Value, required=False, default={'amount': 0, 'currency': 'UAH',
                                                         'valueAddedTaxIncluded': True})  # The total estimated value of the procurement.

    enquiryPeriod = ModelType(EnquiryPeriod, required=False)
    tenderPeriod = ModelType(PeriodStartEndRequired, required=True)
    auctionPeriod = ModelType(TenderAuctionPeriod, default={})
    hasEnquiries = BooleanType()  # A Yes/No field as to whether enquiries were part of tender process.
    awardCriteria = StringType(default='ratedCriteria')
    awardPeriod = ModelType(Period)  # The date or period on which an award is anticipated to be made.
    numberOfBidders = IntType()  # The number of unique tenderers who participated in the tender
    bids = SifterListType(BidModelType(Bid), default=list(), filter_by='status',
                          filter_in_values=['invalid', 'invalid.pre-qualification', 'deleted'])  # A list of all the companies who entered submissions for the tender.
    procuringEntity = ModelType(ProcuringEntity, required=True)  # The entity managing the procurement, which may be different from the buyer who is paying / using the items being procured.
    awards = ListType(ModelType(Award), default=list())
    contracts = ListType(ModelType(Contract), default=list())
    minimalStep = ModelType(Value, required=False)  # Not required, blocked for create/edit, since we have minimalStepPercentage in esco
    minimalStepPercentage = DecimalType(required=True,
                                        min_value=Decimal('0.005'), max_value=Decimal('0.03'))
    questions = ListType(ModelType(Question), default=list())
    complaints = ListType(ComplaintModelType(Complaint), default=list())
    auctionUrl = URLType()
    cancellations = ListType(ModelType(Cancellation), default=list())
    features = ListType(ModelType(Feature), validators=[validate_features_uniq])
    lots = ListType(ModelType(Lot), default=list(), validators=[validate_lots_uniq])
    guarantee = ModelType(Guarantee)
    documents = ListType(ModelType(Document), default=list())  # All documents and attachments related to the tender.
    qualifications = ListType(ModelType(Qualification), default=list())
    qualificationPeriod = ModelType(Period)
    status = StringType(choices=['draft', 'active.tendering', 'active.pre-qualification',
                                 'active.pre-qualification.stand-still', 'active.auction',
                                 'active.qualification', 'active.awarded', 'complete',
                                 'cancelled', 'unsuccessful'], default='active.tendering')
    NBUdiscountRate = DecimalType(required=True, min_value=Decimal('0'), max_value=Decimal('0.99'),
                                  precision=-5)
    fundingKind = StringType(choices=['budget', 'other'], required=True, default='other')
    yearlyPaymentsPercentageRange = DecimalType(required=True, default=Decimal('0.8'),
                                                min_value=Decimal('0'), max_value=Decimal('1'))
    noticePublicationDate = IsoDateTimeType()

    create_accreditation = 3
    edit_accreditation = 4
    special_fields = ['fundingKind', 'yearlyPaymentsPercentageRange']
    procuring_entity_kinds = ['general', 'special', 'defense']
    block_tender_complaint_status = OpenUATender.block_tender_complaint_status
    block_complaint_status = OpenUATender.block_complaint_status

    def import_data(self, raw_data, **kw):
        """
        Converts and imports the raw data into the instance of the model
        according to the fields in the model.
        :param raw_data:
            The data to be imported.
        """
        data = self.convert(raw_data, **kw)
        del_keys = [k for k in data.keys() if data[k] == self.__class__.fields[k].default or data[k] == getattr(self, k)]
        for k in del_keys:
            if k in self.special_fields:
                # skip special fields :)
                continue
            del data[k]
        self._data.update(data)
        return self

    def __local_roles__(self):
        roles = dict([('{}_{}'.format(self.owner, self.owner_token), 'tender_owner')])
        for i in self.bids:
            roles['{}_{}'.format(i.owner, i.owner_token)] = 'bid_owner'
        return roles

    def __acl__(self):
        acl = [
            (Allow, '{}_{}'.format(i.owner, i.owner_token), 'create_qualification_complaint')
            for i in self.bids
            if i.status in ['active', 'unsuccessful']
        ]
        acl.extend([
            (Allow, '{}_{}'.format(i.owner, i.owner_token), 'create_award_complaint')
            for i in self.bids
            if i.status == 'active'
        ])
        acl.extend([
            (Allow, '{}_{}'.format(self.owner, self.owner_token), 'edit_tender'),
            (Allow, '{}_{}'.format(self.owner, self.owner_token), 'upload_tender_documents'),
            (Allow, '{}_{}'.format(self.owner, self.owner_token), 'edit_complaint'),
        ])
        return acl

    @serializable(serialized_name="enquiryPeriod", type=ModelType(EnquiryPeriod))
    def tender_enquiryPeriod(self):
        endDate = calculate_business_date(self.tenderPeriod.endDate, -QUESTIONS_STAND_STILL, self)
        return EnquiryPeriod(dict(
            startDate=self.tenderPeriod.startDate,
            endDate=endDate,
            invalidationDate=self.enquiryPeriod and self.enquiryPeriod.invalidationDate,
            clarificationsUntil=calculate_business_date(endDate, ENQUIRY_STAND_STILL_TIME, self, True)))

    @serializable(type=ModelType(Period))
    def complaintPeriod(self):
        normalized_end = calculate_normalized_date(self.tenderPeriod.endDate, self)
        return Period(dict(
            startDate=self.tenderPeriod.startDate,
            endDate=calculate_business_date(normalized_end, -COMPLAINT_SUBMIT_TIME, self)))

    @serializable(serialize_when_none=False)
    def next_check(self):
        now = get_now()
        checks = []
        if self.status == 'active.tendering' and self.tenderPeriod.endDate and \
                not has_unanswered_complaints(self) and not has_unanswered_questions(self):
            checks.append(self.tenderPeriod.endDate.astimezone(TZ))
        elif self.status == 'active.pre-qualification.stand-still' and self.qualificationPeriod and self.qualificationPeriod.endDate:
            active_lots = [lot.id for lot in self.lots if lot.status == 'active'] if self.lots else [None]
            if not any([
                i.status in self.block_complaint_status
                for q in self.qualifications
                for i in q.complaints
                if q.lotID in active_lots
            ]):
                checks.append(self.qualificationPeriod.endDate.astimezone(TZ))
        elif not self.lots and self.status == 'active.auction' and self.auctionPeriod and self.auctionPeriod.startDate and not self.auctionPeriod.endDate:
            if now < self.auctionPeriod.startDate:
                checks.append(self.auctionPeriod.startDate.astimezone(TZ))
            elif now < calc_auction_end_time(self.numberOfBids, self.auctionPeriod.startDate).astimezone(TZ):
                checks.append(calc_auction_end_time(self.numberOfBids, self.auctionPeriod.startDate).astimezone(TZ))
        elif self.lots and self.status == 'active.auction':
            for lot in self.lots:
                if lot.status != 'active' or not lot.auctionPeriod or not lot.auctionPeriod.startDate or lot.auctionPeriod.endDate:
                    continue
                if now < lot.auctionPeriod.startDate:
                    checks.append(lot.auctionPeriod.startDate.astimezone(TZ))
                elif now < calc_auction_end_time(lot.numberOfBids, lot.auctionPeriod.startDate).astimezone(TZ):
                    checks.append(calc_auction_end_time(lot.numberOfBids, lot.auctionPeriod.startDate).astimezone(TZ))
        elif not self.lots and self.status == 'active.awarded' and not any([
                i.status in self.block_complaint_status
                for i in self.complaints
            ]) and not any([
                i.status in self.block_complaint_status
                for a in self.awards
                for i in a.complaints
            ]):
            standStillEnds = [
                a.complaintPeriod.endDate.astimezone(TZ)
                for a in self.awards
                if a.complaintPeriod.endDate
            ]
            last_award_status = self.awards[-1].status if self.awards else ''
            if standStillEnds and last_award_status == 'unsuccessful':
                checks.append(max(standStillEnds))
        elif self.lots and self.status in ['active.qualification', 'active.awarded'] and not any([
                i.status in self.block_complaint_status and i.relatedLot is None
                for i in self.complaints
            ]):
            for lot in self.lots:
                if lot['status'] != 'active':
                    continue
                lot_awards = [i for i in self.awards if i.lotID == lot.id]
                pending_complaints = any([
                    i['status'] in self.block_complaint_status and i.relatedLot == lot.id
                    for i in self.complaints
                ])
                pending_awards_complaints = any([
                    i.status in self.block_complaint_status
                    for a in lot_awards
                    for i in a.complaints
                ])
                standStillEnds = [
                    a.complaintPeriod.endDate.astimezone(TZ)
                    for a in lot_awards
                    if a.complaintPeriod.endDate
                ]
                last_award_status = lot_awards[-1].status if lot_awards else ''
                if not pending_complaints and not pending_awards_complaints and standStillEnds and last_award_status == 'unsuccessful':
                    checks.append(max(standStillEnds))
        if self.status.startswith('active'):
            for award in self.awards:
                if award.status == 'active' and not any([i.awardID == award.id for i in self.contracts]):
                    checks.append(award.date)
        return min(checks).isoformat() if checks else None

    @serializable
    def numberOfBids(self):
        """A property that is serialized by schematics exports."""
        return len([bid for bid in self.bids if bid.status in ("active", "pending",)])

    @serializable(serialized_name="minValue", type=ModelType(Value))
    def tender_minValue(self):
        return Value(dict(
            amount=sum([i.minValue.amount for i in self.lots]),
            currency=self.minValue.currency,
            valueAddedTaxIncluded=self.minValue.valueAddedTaxIncluded)) if self.lots else self.minValue

    @serializable(serialized_name="guarantee", serialize_when_none=False, type=ModelType(Guarantee))
    def tender_guarantee(self):
        if self.lots:
            lots_amount = [i.guarantee.amount for i in self.lots if i.guarantee]
            if not lots_amount:
                return self.guarantee
            guarantee = {'amount': sum(lots_amount)}
            lots_currency = [i.guarantee.currency for i in self.lots if i.guarantee]
            guarantee['currency'] = lots_currency[0] if lots_currency else None
            if self.guarantee:
                guarantee['currency'] = self.guarantee.currency
            return Guarantee(guarantee)
        else:
            return self.guarantee

    @serializable(serialized_name="minimalStep", type=ModelType(Value), serialize_when_none=False)
    def tender_minimalStep(self):
        pass
        # return Value(dict(
        #     amount=min([i.minimalStep.amount for i in self.lots]),
        #     currency=self.minimalStep.currency,
        #     valueAddedTaxIncluded=self.minimalStep.valueAddedTaxIncluded)) if self.lots else self.minimalStep

    @serializable(serialized_name="minimalStepPercentage")
    def tender_minimalStepPercentage(self):
        return min([i.minimalStepPercentage for i in self.lots]) if self.lots else self.minimalStepPercentage

    @serializable(serialized_name="yearlyPaymentsPercentageRange")
    def tender_yearlyPaymentsPercentageRange(self):
        return min([i.yearlyPaymentsPercentageRange for i in self.lots]) if self.lots else self.yearlyPaymentsPercentageRange

    @serializable(serialized_name="noticePublicationDate", serialize_when_none=False, type=IsoDateTimeType())
    def tender_noticePublicationDate(self):
        if not self.noticePublicationDate and self.status == 'active.tendering':
            return self.__parent__.request.now
        else:
            return self.noticePublicationDate

    def validate_items(self, data, items):
        cpv_336_group = items[0].classification.id[:3] == '336' if items else False
        if not cpv_336_group and (data.get('revisions')[0].date if data.get('revisions') else get_now()) > CPV_ITEMS_CLASS_FROM and items and len(set([i.classification.id[:4] for i in items])) != 1:
            raise ValidationError(u"CPV class of items should be identical")
        else:
            validate_cpv_group(items)

    def validate_features(self, data, features):
        if features and data['lots'] and any([
            round(vnmax([
                i
                for i in features
                if i.featureOf == 'tenderer' or i.featureOf == 'lot' and i.relatedItem == lot['id'] or i.featureOf == 'item' and i.relatedItem in [j.id for j in data['items'] if j.relatedLot == lot['id']]
            ]), 15) > 0.25
            for lot in data['lots']
        ]):
            raise ValidationError(u"Sum of max value of all features for lot should be less then or equal to 25%")
        elif features and not data['lots'] and round(vnmax(features), 15) > 0.25:
            raise ValidationError(u"Sum of max value of all features should be less then or equal to 25%")

    def validate_auctionUrl(self, data, url):
        if url and data['lots']:
            raise ValidationError(u"url should be posted for each lot")

    def validate_minimalStep(self, data, value):
        pass
    #     if value and value.amount and data.get('minValue'):
    #         if data.get('minValue').currency != value.currency:
    #             raise ValidationError(u"currency should be identical to currency of minValue of tender")
    #         if data.get('minValue').valueAddedTaxIncluded != value.valueAddedTaxIncluded:
    #             raise ValidationError(u"valueAddedTaxIncluded should be identical to valueAddedTaxIncluded of minValue of tender")

    def validate_tenderPeriod(self, data, period):
        # if data['_rev'] is None when tender was created just now
        if not data['_rev'] and calculate_business_date(get_now(), -timedelta(minutes=10)) >= period.startDate:
            raise ValidationError(u"tenderPeriod.startDate should be in greater than current date")
        if period and calculate_business_date(period.startDate, TENDERING_DURATION, data) > period.endDate:
            raise ValidationError(u"tenderPeriod should be greater than {} days".format(TENDERING_DAYS))

    def validate_awardPeriod(self, data, period):
        if period and period.startDate and data.get('auctionPeriod') and data.get('auctionPeriod').endDate and period.startDate < data.get('auctionPeriod').endDate:
            raise ValidationError(u"period should begin after auctionPeriod")
        if period and period.startDate and data.get('tenderPeriod') and data.get('tenderPeriod').endDate and period.startDate < data.get('tenderPeriod').endDate:
            raise ValidationError(u"period should begin after tenderPeriod")

    def validate_lots(self, data, value):
        if len(set([lot.guarantee.currency for lot in value if lot.guarantee])) > 1:
            raise ValidationError(u"lot guarantee currency should be identical to tender guarantee currency")
        if len(set([lot.fundingKind for lot in value])) > 1:
            raise ValidationError(u"lot funding kind should be identical to tender funding kind")

    def validate_yearlyPaymentsPercentageRange(self, data, value):
        if data['fundingKind'] == 'other' and value != Decimal('0.8'):
            raise ValidationError('when fundingKind is other, yearlyPaymentsPercentageRange should be equal 0.8')
        if data['fundingKind'] == 'budget' and (value > Decimal('0.8') or value < Decimal('0')):
            raise ValidationError('when fundingKind is budget, yearlyPaymentsPercentageRange should be less or equal 0.8, and more or equal 0')

    def check_auction_time(self):
        if self.auctionPeriod and self.auctionPeriod.startDate and self.auctionPeriod.shouldStartAfter \
                and self.auctionPeriod.startDate > calculate_business_date(parse_date(self.auctionPeriod.shouldStartAfter), AUCTION_PERIOD_TIME, self, True):
            self.auctionPeriod.startDate = None
        for lot in self.lots:
            if lot.auctionPeriod and lot.auctionPeriod.startDate and lot.auctionPeriod.shouldStartAfter \
                    and lot.auctionPeriod.startDate > calculate_business_date(parse_date(lot.auctionPeriod.shouldStartAfter), AUCTION_PERIOD_TIME, self, True):
                lot.auctionPeriod.startDate = None

    def invalidate_bids_data(self):
        self.check_auction_time()
        self.enquiryPeriod.invalidationDate = get_now()
        for bid in self.bids:
            if bid.status not in ["deleted", "draft"]:
                bid.status = "invalid"


TenderESCO = Tender
