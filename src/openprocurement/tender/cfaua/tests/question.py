# -*- coding: utf-8 -*-
import unittest

from openprocurement.api.tests.base import snitch
from openprocurement.tender.cfaua.tests.question_blanks import (
    lot_create_tender_question,
    lot_patch_tender_question,
    lot_create_tender_cancellations_and_questions
)

from openprocurement.tender.belowthreshold.tests.base import test_organization
from openprocurement.tender.belowthreshold.tests.question import TenderQuestionResourceTestMixin

from openprocurement.tender.openua.tests.question_blanks import (
    # TenderQuestionResourceTest
    create_tender_question,
)

from openprocurement.tender.cfaua.tests.base import (
    BaseTenderContentWebTest,
    test_bids,
    test_lots,
)
from openprocurement.tender.openeu.tests.question_blanks import (
    # TenderQuestionResourceTest
    patch_tender_question,
    answering_question,
)


class TenderQuestionResourceTest(BaseTenderContentWebTest, TenderQuestionResourceTestMixin):

    initial_auth = ('Basic', ('broker', ''))
    test_bids_data = test_bids

    test_create_tender_question = snitch(create_tender_question)
    test_patch_tender_question = snitch(patch_tender_question)
    test_answering_question = snitch(answering_question)


class TenderLotQuestionResourceTest(BaseTenderContentWebTest):
    initial_lots = test_lots
    initial_auth = ('Basic', ('broker', ''))
    test_bids_data = test_bids
    author_data = test_organization

    test_create_tender_question = snitch(lot_create_tender_question)
    test_patch_tender_question = snitch(lot_patch_tender_question)
    test_lot_create_tender_cancellations_and_questions = snitch(lot_create_tender_cancellations_and_questions)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderQuestionResourceTest))
    suite.addTest(unittest.makeSuite(TenderLotQuestionResourceTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
