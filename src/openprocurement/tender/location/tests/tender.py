import unittest

from copy import deepcopy
from openprocurement.api.tests.base import snitch
from openprocurement.contracting.api.tests.base import BaseApiWebTest
from openprocurement.tender.belowthreshold.tests.tender_blanks import simple_add_tender
from openprocurement.tender.location.tests.base import test_tender_data
from openprocurement.tender.location.tests.tender_blanks import create_tender

tender_data = deepcopy(test_tender_data)


class TenderResourceTestMixin(object):
    test_create_tender = snitch(create_tender)


class TenderTest(BaseApiWebTest):
    initial_data = tender_data
    initial_auth = ("Basic", ("broker", ""))

    test_create_tender = snitch(create_tender)


def suite():
    suite = unittest.TestSuite()
    #suite.addTest(unittest.makeSuite(TenderProcessTest))
    #suite.addTest(unittest.makeSuite(TenderResourceTest))
    suite.addTest(unittest.makeSuite(TenderTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")