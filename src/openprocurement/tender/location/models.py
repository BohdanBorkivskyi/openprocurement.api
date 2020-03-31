from schematics.transforms import whitelist
from schematics.types import StringType, URLType, BooleanType, IntType, ValidationError
from schematics.types.compound import ModelType, ListType
from zope.interface import implementer

from openprocurement.agreement.core.models.agreement import Agreement
from openprocurement.api.models import Period, Guarantee, Item, Value, IsoDurationType, Model
from openprocurement.api.validation import validate_items_uniq, validate_classification_id
from openprocurement.tender.cfaua.validation import validate_max_awards_number
from openprocurement.tender.core.models import Tender as BaseTender, ITender, TenderAuctionPeriod, Award, Bid, \
    Cancellation, ComplaintModelType, Complaint, EUDocument, EnquiryPeriod, Feature, validate_features_uniq, Lot, \
    ProcuringEntity, PeriodStartEndRequired, validate_lots_uniq, Question


class Location(Model):
    longitude = StringType(required=True)
    latitude = StringType(required=True)

    def validate_coord(self, data, value):
        if not value.replace(".", "").isdigit():
            raise ValidationError(u"Should be proper geographic coordinate system value")

    validate_longitude = validate_coord
    validate_latitude = validate_coord


class ILocationTender(ITender):
    """ Marker interface for location tenders """


@implementer(ILocationTender)
class Tender(BaseTender):

    class Options:
        namespace = "Tender"
        _core_roles = BaseTender.Options.roles
        _procurement_method_details = whitelist("procurementMethodDetails")
        _edit_fields = _core_roles["edit"] + whitelist(
            "tenderPeriod",
            "features",
            "complaintPeriod",
            "agreementDuration",
            "next_check",
            "procuringEntity",
            "guarantee",
            "serializable_enquiryPeriod",
            "minimalStep",
            "items",
            "qualificationPeriod",
            "value",
            "maxAwardsCount",
            "agreements",
            "numberOfBidders",
            "hasEnquiries",
            "serializable_guarantee",
            "serializable_value",
            "serializable_minimalStep",
            "location"
        )
        _edit_role = _edit_fields + whitelist("numberOfBids")
        _edit_qualification = whitelist("status") + _procurement_method_details
        _tendering_view_role = (
            _core_roles["view"]
            + _edit_fields
            + whitelist(
                "auctionPeriod",
                "lots",
                "enquiryPeriod",
                "complaints",
                "auctionUrl",
                "awardPeriod",
                "qualifications",
                "questions",
                "cancellations",
                "awards",
            )
        )
        _view_role = _tendering_view_role + whitelist("numberOfBids", "bids")
        _complete_view_role = _view_role + whitelist("contractPeriod")
        roles = {
            "create": _edit_role + whitelist("mode", "procurementMethodType", "lots", "coords"),
            "edit_draft": _edit_role,
            "edit": _edit_role,
            "edit_active.tendering": _edit_role + whitelist("coords"),
            "edit_active.pre-qualification": _edit_qualification,
            "edit_active.qualification": _edit_qualification,
            "edit_cancelled": _procurement_method_details,
            "edit_complete": _procurement_method_details,
            "edit_unsuccessful": _procurement_method_details,
            "edit_active.awarded": _procurement_method_details,
            "edit_active.auction": _procurement_method_details,
            "edit_active.pre-qualification.stand-still": _procurement_method_details,
            "draft": _tendering_view_role + whitelist("contractPeriod"),
            "active.tendering": _tendering_view_role,
            "cancelled": _view_role,
            "active.auction": _view_role,
            "active.pre-qualification.stand-still": _view_role,
            "active.qualification.stand-still": _view_role,
            "view": _complete_view_role,
            "active.qualification": _complete_view_role,
            "active.pre-qualification": _complete_view_role,
            "complete": _complete_view_role,
            "active.awarded": _complete_view_role,
            "unsuccessful": _complete_view_role,
            "contracting": _core_roles["contracting"] + _procurement_method_details,
            "chronograph": _core_roles["chronograph"] + _procurement_method_details,
            "chronograph_view": _core_roles["chronograph_view"] + _procurement_method_details,
            "auction_view": _core_roles["auction_view"]
            + _procurement_method_details
            + whitelist("milestones", "mainProcurementCategory"),
            "Administrator": _core_roles["Administrator"] + _procurement_method_details,
            "auction_post": _core_roles["auction_post"] + _procurement_method_details,
            "auction_patch": _core_roles["auction_patch"] + _procurement_method_details,
            "listing": _core_roles["listing"] + _procurement_method_details,
            "embedded": _core_roles["embedded"],
            "plain": _core_roles["plain"],
            "default": _core_roles["default"],
        }

    procurementMethodType = StringType(default="location")

    procuring_entity_kinds = ["general", "special", "defense", "central"]
    block_tender_complaint_status = ["claim", "pending", "accepted", "satisfied", "stopping"]
    block_complaint_status = ["pending", "accepted", "satisfied", "stopping"]

    auctionPeriod = ModelType(TenderAuctionPeriod, default={})
    auctionUrl = URLType()
    awards = ListType(ModelType(Award, required=True), default=list())
    awardPeriod = ModelType(Period)  # The dat e or period on which an award is anticipated to be made.
    bids = ListType(
        ModelType(Bid, required=True), default=list()
    )  # A list of all the companies who entered submissions for the tender.
    cancellations = ListType(ModelType(Cancellation, required=True), default=list())
    complaints = ListType(ComplaintModelType(Complaint, required=True), default=list())
    #contractPeriod = ModelType(ContractPeriod, required=False)
    agreements = ListType(ModelType(Agreement, required=True), default=list())
    documents = ListType(
        ModelType(EUDocument, required=True), default=list()
    )  # All documents and attachments related to the tender.
    enquiryPeriod = ModelType(EnquiryPeriod, required=False)
    guarantee = ModelType(Guarantee)
    hasEnquiries = BooleanType()  # A Yes/No field as to whether enquiries were part of tender process.
    items = ListType(
        ModelType(Item, required=True),
        required=True,
        min_size=1,
        validators=[validate_items_uniq, validate_classification_id],
    )  # The goods and services to be purchased, broken into line items wherever possible. Items should not be duplicated, but a quantity of 2 specified instead.
    features = ListType(ModelType(Feature, required=True), validators=[validate_features_uniq])
    minimalStep = ModelType(Value, required=True)
    numberOfBidders = IntType()  # The number of unique tenderers who participated in the tender
    maxAwardsCount = IntType(required=True, validators=[validate_max_awards_number])
    lots = ListType(
        ModelType(Lot, required=True), min_size=1, max_size=1, default=list(), validators=[validate_lots_uniq]
    )
    #procurementMethodType = StringType(default="closeFrameworkAgreementUA")
    procuringEntity = ModelType(
        ProcuringEntity, required=True
    )  # The entity managing the procurement, which may be different from the buyer who is paying / using the items being procured.
    qualificationPeriod = ModelType(Period)
    #qualifications = ListType(ModelType(Qualification, required=True), default=list())
    questions = ListType(ModelType(Question, required=True), default=list())
    status = StringType(
        choices=[
            "draft",
            "active.tendering",
            "active.pre-qualification",
            "active.pre-qualification.stand-still",
            "active.auction",
            "active.qualification",
            "active.qualification.stand-still",
            "active.awarded",
            "complete",
            "cancelled",
            "unsuccessful",
        ],
        default="active.tendering",
    )
    tenderPeriod = ModelType(PeriodStartEndRequired, required=True)
    title_en = StringType(required=True, min_length=1)
    value = ModelType(Value, required=True)  # The total estimated value of the procurement.
    #agreementDuration = IsoDurationType(required=True, validators=[validate_max_agreement_duration_period])
    mainProcurementCategory = StringType(choices=["goods", "services"])

    location = ModelType(Location, required=True)
