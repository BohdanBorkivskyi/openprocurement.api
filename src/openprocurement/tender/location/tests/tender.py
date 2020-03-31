import unittest

from copy import deepcopy
from openprocurement.api.tests.base import snitch
from openprocurement.tender.location.tests.base import test_tender_data, BaseApiWebTest
from openprocurement.tender.location.tests.tender_blanks import create_tender

tender_data = deepcopy(test_tender_data)


class TenderTest(BaseApiWebTest):
    initial_data = tender_data
    initial_auth = ("Basic", ("broker", ""))

    test_create_tender = snitch(create_tender)
