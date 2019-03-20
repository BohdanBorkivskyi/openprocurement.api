# -*- coding: utf-8 -*-
import unittest

from openprocurement.api.tests.base import snitch

from openprocurement.tender.belowthreshold.tests.base import test_organization
from openprocurement.tender.belowthreshold.tests.contract import (
    TenderContractResourceTestMixin,
    TenderContractDocumentResourceTestMixin
)

from openprocurement.tender.openua.tests.base import test_bids
from openprocurement.tender.openua.tests.contract_blanks import (
    # TenderContractResourceTest
    create_tender_contract,
    patch_tender_contract,
    patch_tender_contract_vat_not_included)

from openprocurement.tender.openuadefense.tests.base import (
    BaseTenderUAContentWebTest
)


class TenderContractResourceTest(BaseTenderUAContentWebTest, TenderContractResourceTestMixin):
    initial_status = 'active.qualification'
    initial_bids = test_bids

    def setUp(self):
        super(TenderContractResourceTest, self).setUp()
        # Create award
        authorization = self.app.authorization
        self.app.authorization = ('Basic', ('token', ''))
        response = self.app.post_json('/tenders/{}/awards'.format(
            self.tender_id),
            {'data': {'suppliers': [test_organization], 'status': 'pending', 'bid_id': self.initial_bids[0]['id'],
                      'value': self.initial_bids[0]['value']}})
        award = response.json['data']
        self.award_id = award['id']
        self.award_value = award['value']
        self.app.authorization = authorization
        self.app.patch_json(
            '/tenders/{}/awards/{}?acc_token={}'.format(self.tender_id, self.award_id, self.tender_token),
            {"data": {"status": "active", "qualified": True, "eligible": True}})

    test_create_tender_contract = snitch(create_tender_contract)
    test_patch_tender_contract = snitch(patch_tender_contract)


class TenderContractVATNotIncludedResourceTest(BaseTenderUAContentWebTest, TenderContractResourceTestMixin):
    initial_status = 'active.qualification'
    initial_bids = test_bids

    def create_award(self):
        authorization = self.app.authorization
        self.app.authorization = ('Basic', ('token', ''))
        response = self.app.post_json('/tenders/{}/awards'.format(
            self.tender_id),
            {'data': {
                'suppliers': [test_organization],
                'status': 'pending',
                'bid_id': self.initial_bids[0]['id'],
                'value': {
                    'amount': self.initial_bids[0]["value"]["amount"],
                    'currency': self.initial_bids[0]["value"]["currency"],
                    'valueAddedTaxIncluded': False
                }}})
        award = response.json['data']
        self.award_id = award['id']
        self.award_value = award['value']
        self.app.authorization = authorization
        self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(
            self.tender_id, self.award_id, self.tender_token),
            {"data": {"status": "active", "qualified": True, "eligible": True}})

    def setUp(self):
        super(TenderContractVATNotIncludedResourceTest, self).setUp()
        self.create_award()

    test_patch_tender_contract_vat_not_included = snitch(patch_tender_contract_vat_not_included)


class TenderContractDocumentResourceTest(BaseTenderUAContentWebTest, TenderContractDocumentResourceTestMixin):
    initial_status = 'active.qualification'
    initial_bids = test_bids

    def setUp(self):
        super(TenderContractDocumentResourceTest, self).setUp()
        # Create award
        auth = self.app.authorization
        self.app.authorization = ('Basic', ('token', ''))
        response = self.app.post_json('/tenders/{}/awards'.format(
            self.tender_id), {'data': {'suppliers': [test_organization], 'status': 'pending', 'bid_id': self.initial_bids[0]['id']}})
        award = response.json['data']
        self.award_id = award['id']
        response = self.app.patch_json('/tenders/{}/awards/{}'.format(self.tender_id, self.award_id), {"data": {"status": "active", "qualified": True, "eligible": True}})
        # Create contract for award
        response = self.app.post_json('/tenders/{}/contracts'.format(self.tender_id), {'data': {'title': 'contract title', 'description': 'contract description', 'awardID': self.award_id}})
        contract = response.json['data']
        self.contract_id = contract['id']
        self.app.authorization = auth


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderContractResourceTest))
    suite.addTest(unittest.makeSuite(TenderContractDocumentResourceTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
