# -*- coding: utf-8 -*-
import unittest

from esculator import npv, escp
from openprocurement.api.utils import get_now
from openprocurement.api.tests.base import snitch

from openprocurement.tender.belowthreshold.tests.base import test_organization
from openprocurement.tender.belowthreshold.tests.lot import (
    TenderLotProcessTestMixin
)
from openprocurement.tender.belowthreshold.tests.lot_blanks import (
    create_tender_lot,
    patch_tender_lot,
    delete_tender_lot,
    tender_lot_guarantee,
    tender_lot_document,
)

from openprocurement.tender.openeu.tests.lot import TenderLotEdgeCasesTestMixin
from openprocurement.tender.openeu.tests.lot_blanks import (
    # TenderLotProcessTest
    one_lot_1bid,
    one_lot_2bid_1unqualified,
    one_lot_2bid,
    two_lot_2bid_1lot_del,
    one_lot_3bid_1del,
    one_lot_3bid_1un,
    two_lot_1can,
    two_lot_2bid_0com_1can,
    two_lot_2bid_2com_2win,
    two_lot_3bid_1win_bug,
)

from openprocurement.tender.esco.tests.base import (
    BaseESCOContentWebTest,
    test_tender_data,
    test_lots,
    test_bids,
    NBU_DISCOUNT_RATE,
)

from openprocurement.tender.esco.tests.lot_blanks import (
    create_tender_lot_invalid,
    patch_tender_lot_minValue,
    get_tender_lot,
    get_tender_lots,
    tender_min_value,
    lot_minimal_step_invalid,
    tender_minimal_step_percentage,
    tender_lot_funding_kind,
    tender_1lot_fundingKind_default,
    tender_2lot_fundingKind_default,
    tender_lot_yearlyPaymentsPercentageRange,
    tender_lot_fundingKind_yppr,
    tender_lot_Administrator_change_yppr,
    # TenderLotFeatureBidderResourceTest
    create_tender_feature_bid_invalid,
    create_tender_feature_bid,
    tender_features_invalid,
    # TenderLotBidResourceTest
    create_tender_bid_invalid,
    patch_tender_bid,
    bids_invalidation_on_lot_change,
)
from openprocurement.tender.esco.utils import to_decimal


lot_bid_amountPerformance = round(to_decimal(npv(
    test_bids[0]['value']['contractDuration']['years'],
    test_bids[0]['value']['contractDuration']['days'],
    test_bids[0]['value']['yearlyPaymentsPercentage'],
    test_bids[0]['value']['annualCostsReduction'],
    get_now(),
    NBU_DISCOUNT_RATE)), 2)

lot_bid_amount = round(to_decimal(escp(
    test_bids[0]['value']['contractDuration']['years'],
    test_bids[0]['value']['contractDuration']['days'],
    test_bids[0]['value']['yearlyPaymentsPercentage'],
    test_bids[0]['value']['annualCostsReduction'],
    get_now())), 2)


class TenderLotResourceTest(BaseESCOContentWebTest):

    initial_auth = ('Basic', ('broker', ''))
    test_lots_data = test_lots  # TODO: change attribute identifier
    initial_data = test_tender_data

    test_create_tender_lot_invalid = snitch(create_tender_lot_invalid)
    test_create_tender_lot = snitch(create_tender_lot)
    test_patch_tender_lot = snitch(patch_tender_lot)
    test_patch_tender_lot_minValue = snitch(patch_tender_lot_minValue)
    test_delete_tender_lot = snitch(delete_tender_lot)

    test_tender_lot_guarantee = snitch(tender_lot_guarantee)

    test_get_tender_lot = snitch(get_tender_lot)
    test_get_tender_lots = snitch(get_tender_lots)
    test_lot_minimal_step_invalid = snitch(lot_minimal_step_invalid)
    test_tender_minimal_step_percentage = snitch(tender_minimal_step_percentage)
    test_tender_lot_funding_kind = snitch(tender_lot_funding_kind)
    test_tender_1lot_fundingKind_default = snitch(tender_1lot_fundingKind_default)
    test_tender_2lot_fundingKind_default = snitch(tender_2lot_fundingKind_default)
    test_tender_lot_yearlyPaymentsPercentageRange = snitch(tender_lot_yearlyPaymentsPercentageRange)
    test_tender_lot_fundingKind_yppr = snitch(tender_lot_fundingKind_yppr)
    test_tender_lot_Administrator_change_yppr = snitch(tender_lot_Administrator_change_yppr)


class TenderLotEdgeCasesTest(BaseESCOContentWebTest, TenderLotEdgeCasesTestMixin):
    initial_auth = ('Basic', ('broker', ''))
    initial_lots = test_lots * 2
    initial_bids = test_bids
    test_author = test_organization


class TenderLotFeatureResourceTest(BaseESCOContentWebTest):
    initial_lots = 2 * test_lots
    # for passing test_tender_min_value while min value = 0
    initial_lots[0]['minValue'] = {"amount": 0}
    initial_lots[1]['minValue'] = {"amount": 0}
    initial_auth = ('Basic', ('broker', ''))
    initial_data = test_tender_data
    test_lots_data = test_lots
    invalid_feature_value = 0.4
    max_feature_value = 0.25
    sum_of_max_value_of_all_features = 0.25

    test_tender_min_value = snitch(tender_min_value)
    test_tender_features_invalid = snitch(tender_features_invalid)
    test_tender_features_invalid = snitch(tender_features_invalid)
    test_tender_lot_document = snitch(tender_lot_document)


class TenderLotBidResourceTest(BaseESCOContentWebTest):
    initial_lots = test_lots
    initial_auth = ('Basic', ('broker', ''))
    test_bids_data = test_bids  # TODO: change attribute identifier
    expected_bid_amountPerformance = lot_bid_amountPerformance
    expected_bid_amount = lot_bid_amount

    test_create_tender_bid_invalid = snitch(create_tender_bid_invalid)
    test_patch_tender_bid = snitch(patch_tender_bid)
    test_bids_invalidation_on_lot_change = snitch(bids_invalidation_on_lot_change)


class TenderLotFeatureBidResourceTest(BaseESCOContentWebTest):
    initial_lots = test_lots
    initial_auth = ('Basic', ('broker', ''))
    initial_data = test_tender_data
    test_bids_data = test_bids  # TODO: change attribute identifier

    def setUp(self):
        super(TenderLotFeatureBidResourceTest, self).setUp()
        self.lot_id = self.initial_lots[0]['id']
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(
            self.tender_id, self.tender_token), {"data": {
                "items": [
                    {
                        'relatedLot': self.lot_id,
                        'id': '1'
                    }
                ],
                "features": [
                    {
                        "code": "code_item",
                        "featureOf": "item",
                        "relatedItem": "1",
                        "title": u"item feature",
                        "enum": [
                            {
                                "value": 0.01,
                                "title": u"good"
                            },
                            {
                                "value": 0.02,
                                "title": u"best"
                            }
                        ]
                    },
                    {
                        "code": "code_lot",
                        "featureOf": "lot",
                        "relatedItem": self.lot_id,
                        "title": u"lot feature",
                        "enum": [
                            {
                                "value": 0.01,
                                "title": u"good"
                            },
                            {
                                "value": 0.02,
                                "title": u"best"
                            }
                        ]
                    },
                    {
                        "code": "code_tenderer",
                        "featureOf": "tenderer",
                        "title": u"tenderer feature",
                        "enum": [
                            {
                                "value": 0.01,
                                "title": u"good"
                            },
                            {
                                "value": 0.02,
                                "title": u"best"
                            }
                        ]
                    }
                ]
            }})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['items'][0]['relatedLot'], self.lot_id)

    test_create_tender_bid_invalid = snitch(create_tender_feature_bid_invalid)
    test_create_tender_bid = snitch(create_tender_feature_bid)


class TenderLotProcessTest(BaseESCOContentWebTest, TenderLotProcessTestMixin):
    setUp = BaseESCOContentWebTest.setUp
    test_lots_data = test_lots  # TODO: change attribute identifier
    test_bids_data = test_bids
    initial_data = test_tender_data

    days_till_auction_starts = 16

    test_1lot_1bid = snitch(one_lot_1bid)
    test_1lot_2bid_1unqualified = snitch(one_lot_2bid_1unqualified)
    test_1lot_2bid = snitch(one_lot_2bid)
    test_2lot_2bid_1lot_del = snitch(two_lot_2bid_1lot_del)
    test_1lot_3bid_1del = snitch(one_lot_3bid_1del)
    test_1lot_3bid_1un = snitch(one_lot_3bid_1un)
    test_2lot_1can = snitch(two_lot_1can)
    test_2lot_2bid_0com_1can = snitch(two_lot_2bid_0com_1can)
    test_2lot_2bid_2com_2win = snitch(two_lot_2bid_2com_2win)
    test_2lot_3bid_1win_bug = snitch(two_lot_3bid_1win_bug)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderLotResourceTest))
    suite.addTest(unittest.makeSuite(TenderLotEdgeCasesTest))
    suite.addTest(unittest.makeSuite(TenderLotFeatureResourceTest))
    suite.addTest(unittest.makeSuite(TenderLotBidResourceTest))
    suite.addTest(unittest.makeSuite(TenderLotFeatureBidResourceTest))
    suite.addTest(unittest.makeSuite(TenderLotProcessTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
