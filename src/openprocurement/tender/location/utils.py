from logging import getLogger

from openprocurement.api.constants import TZ
from openprocurement.api.utils import error_handler, context_unpack, get_now
from openprocurement.tender.belowthreshold.utils import add_contract, check_bids
from openprocurement.tender.core.utils import remove_draft_bids

LOGGER = getLogger("openprocurement.tender.location")


def check_status(request):
    tender = request.validated["tender"]
    now = get_now()

    after_enquiryPeriod_endDate = (
        not tender.tenderPeriod.startDate and tender.enquiryPeriod.endDate.astimezone(TZ) <= now
    )
    after_tenderPeriod_startDate = tender.tenderPeriod.startDate and tender.tenderPeriod.startDate.astimezone(TZ) <= now
    if tender.status == "active.enquiries" and (after_enquiryPeriod_endDate or after_tenderPeriod_startDate):
        LOGGER.info(
            "Switched tender {} to {}".format(tender.id, "active.tendering"),
            extra=context_unpack(request, {"MESSAGE_ID": "switched_tender_active.tendering"}),
        )
        tender.status = "active.tendering"
        return

    elif tender.status == "active.tendering" and tender.tenderPeriod.endDate <= now:
        LOGGER.info(
            "Switched tender {} to {}".format(tender["id"], "active.auction"),
            extra=context_unpack(request, {"MESSAGE_ID": "switched_tender_active.auction"}),
        )
        tender.status = "active.auction"
        #remove_draft_bids(request)
        #check_bids(request)
        #if tender.numberOfBids < 2 and tender.auctionPeriod:
        #    tender.auctionPeriod.startDate = None
        return
    elif tender.lots and tender.status == "active.tendering" and tender.tenderPeriod.endDate <= now:
        LOGGER.info(
            "Switched tender {} to {}".format(tender["id"], "active.auction"),
            extra=context_unpack(request, {"MESSAGE_ID": "switched_tender_active.auction"}),
        )
        tender.status = "active.auction"
        remove_draft_bids(request)
        check_bids(request)
        [setattr(i.auctionPeriod, "startDate", None) for i in tender.lots if i.numberOfBids < 2 and i.auctionPeriod]
        return
