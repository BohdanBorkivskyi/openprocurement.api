# -*- coding: utf-8 -*-
from openprocurement.tender.core.events import TenderInitializeEvent
from openprocurement.tender.core.design import (
    FIELDS,
    tenders_by_dateModified_view,
    tenders_real_by_dateModified_view,
    tenders_test_by_dateModified_view,
    tenders_by_local_seq_view,
    tenders_real_by_local_seq_view,
    tenders_test_by_local_seq_view,
)

from openprocurement.api.utils import get_now, generate_id, json_view, set_ownership, context_unpack, APIResourceListing

from openprocurement.tender.core.utils import save_tender, tender_serialize, optendersresource, generate_tender_id, \
    apply_patch

from openprocurement.tender.core.validation import validate_tender_data, validate_patch_tender_data, \
    validate_tender_not_in_terminated_status, validate_tender_change_status_permission
from openprocurement.tender.location.utils import check_status

VIEW_MAP = {
    u"": tenders_real_by_dateModified_view,
    u"test": tenders_test_by_dateModified_view,
    u"_all_": tenders_by_dateModified_view,
}
CHANGES_VIEW_MAP = {
    u"": tenders_real_by_local_seq_view,
    u"test": tenders_test_by_local_seq_view,
    u"_all_": tenders_by_local_seq_view,
}
FEED = {u"dateModified": VIEW_MAP, u"changes": CHANGES_VIEW_MAP}


@optendersresource(
    name="location:Tender",
    collection_path="/tenders",
    path="/tenders/{tender_id}",
    description="Open Contracting compatible data exchange format",
    procurementMethodType="location"
)
class TendersResource(APIResourceListing):
    def __init__(self, request, context):
        super(TendersResource, self).__init__(request, context)
        # params for listing
        self.VIEW_MAP = VIEW_MAP
        self.CHANGES_VIEW_MAP = CHANGES_VIEW_MAP
        self.FEED = FEED
        self.FIELDS = FIELDS
        self.serialize_func = tender_serialize
        self.object_name_for_listing = "Tenders"
        self.log_message_id = "tender_list_custom"

    @json_view(
        content_type="application/json",
        permission="create_tender",
        validators=(
            validate_tender_data,
        )
    )
    def collection_post(self):
        print("hello from new type")
        tender_id = generate_id()
        tender = self.request.validated["tender"]
        tender.id = tender_id
        if not tender.get("tenderID"):
            tender.tenderID = generate_tender_id(get_now(), self.db, self.server_id)
        self.request.registry.notify(TenderInitializeEvent(tender))
        if self.request.json_body["data"].get("status") == "draft":
            tender.status = "draft"
        access = set_ownership(tender, self.request)
        self.request.validated["tender"] = tender
        self.request.validated["tender_src"] = {}
        if save_tender(self.request):
            self.LOGGER.info(
                "Created tender {} ({})".format(tender_id, tender.tenderID),
                extra=context_unpack(
                    self.request,
                    {"MESSAGE_ID": "tender_create"},
                    {"tender_id": tender_id, "tenderID": tender.tenderID, "tender_mode": tender.mode},
                ),
            )
            self.request.response.status = 201
            self.request.response.headers["Location"] = self.request.route_url(
                "{}:Tender".format(tender.procurementMethodType), tender_id=tender_id
            )
            return {"data": tender.serialize(tender.status), "access": access}

    @json_view(
        permission="view_tender"
    )
    def get(self):
        if self.request.authenticated_role == "chronograph":
            tender_data = self.context.serialize("chronograph_view")
        else:
            tender_data = self.context.serialize(self.context.status)
        return {"data": tender_data}

    @json_view(
        content_type="application/json",
        validators=(
                validate_patch_tender_data,
                validate_tender_not_in_terminated_status,
                validate_tender_change_status_permission,
        ),
        permission="edit_tender",
    )
    def patch(self):

        tender = self.context
        if self.request.authenticated_role == "chronograph":
            apply_patch(self.request, save=False, src=self.request.validated["tender_src"])
            check_status(self.request)
            save_tender(self.request)
        else:
            apply_patch(self.request, src=self.request.validated["tender_src"])
        self.LOGGER.info(
            "Updated tender {}".format(tender.id), extra=context_unpack(self.request, {"MESSAGE_ID": "tender_patch"})
        )
        return {"data": tender.serialize(tender.status)}