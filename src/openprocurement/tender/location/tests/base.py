import json
import os

from openprocurement.tender.core.tests.base import BaseWebTest

here = os.path.dirname(os.path.abspath(__file__))


with open(os.path.join(here, "data/tender_data.json")) as _in:
    test_tender_data = json.load(_in)


class BaseApiWebTest(BaseWebTest):
    relative_to = os.path.dirname(__file__)
