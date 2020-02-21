from openprocurement.api.tests.base import snitch
from openprocurement.tender.belowthreshold.tests.base import test_organization, test_author
from openprocurement.tender.limited.tests.base import (
    BaseTenderContentWebTest,
    test_tender_negotiation_data,
    test_tender_negotiation_quick_data,
)
from openprocurement.tender.openua.tests.post import (
    TenderAwardComplaintPostResourceMixin,
)
from openprocurement.tender.openua.tests.post_blanks import (
    create_complaint_post_status_forbidden,
    create_complaint_post_complaint_owner,
    create_complaint_post_tender_owner,
    create_complaint_post_validate_recipient,
    create_complaint_post_validate_related_post,
    patch_complaint_post,
    get_complaint_post,
    get_complaint_posts,
)


class ComplaintPostResourceMixin(object):
    test_create_complaint_post_status_forbidden = snitch(create_complaint_post_status_forbidden)
    test_create_complaint_post_complaint_owner = snitch(create_complaint_post_complaint_owner)
    test_create_complaint_post_tender_owner = snitch(create_complaint_post_tender_owner)
    test_create_complaint_post_validate_recipient = snitch(create_complaint_post_validate_recipient)
    test_create_complaint_post_validate_related_post = snitch(create_complaint_post_validate_related_post)
    test_patch_complaint_post = snitch(patch_complaint_post)
    test_get_complaint_post = snitch(get_complaint_post)
    test_get_complaint_posts = snitch(get_complaint_posts)


class TenderNegotiationAwardComplaintPostResourceTest(
    BaseTenderContentWebTest,
    ComplaintPostResourceMixin,
    TenderAwardComplaintPostResourceMixin
):
    initial_data = test_tender_negotiation_data

    def setUp(self):
        super(TenderNegotiationAwardComplaintPostResourceTest, self).setUp()
        # Create award
        response = self.app.post_json(
            "/tenders/{}/awards?acc_token={}".format(self.tender_id, self.tender_token),
            {"data": {
                "suppliers": [test_organization],
                "status": "pending",
                "qualified": True,
            }}
        )

        award = response.json["data"]
        self.award_id = award["id"]

        # Create complaint for award
        response = self.app.post_json(
            "/tenders/{}/awards/{}/complaints".format(
                self.tender_id, self.award_id
            ),
            {"data": {
                "title": "complaint title",
                "description": "complaint description",
                "author": test_author
            }},
        )
        self.complaint_id = response.json["data"]["id"]
        self.complaint_owner_token = response.json["access"]["token"]
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")


class TenderNegotiationQuickAwardComplaintPostResourceTest(TenderNegotiationAwardComplaintPostResourceTest):
    initial_data = test_tender_negotiation_quick_data
