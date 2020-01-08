# -*- coding: utf-8 -*-
from iso8601 import parse_date
from datetime import timedelta

from openprocurement.tender.core.views.cancellation_complaint import TenderCancellationComplaintResource
from openprocurement.tender.core.utils import optendersresource, calculate_tender_business_date


@optendersresource(
    name="aboveThresholdUA.defense:Tender Cancellation Complaints",
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}",
    procurementMethodType="aboveThresholdUA.defense",
    description="Tender cancellation complaints",
)
class TenderAboveThresholdUADefenseCancellationComplaintResource(TenderCancellationComplaintResource):
    """Tender AboveThresholdUA Defense Cancellation Complaints """

    def recalculate_tender_periods(self):
        tender = self.request.validated["tender"]
        cancellation = self.request.validated["cancellation"]
        tenderer_action_date = self.context.tendererActionDate

        enquiry_period = tender.enquiryPeriod
        complaint_period = tender.complaintPeriod
        tender_period = tender.tenderPeriod
        auction_period = tender.auctionPeriod

        date = cancellation.complaintPeriod.startDate
        delta = timedelta(days=1 if not (tenderer_action_date - date).days else (tenderer_action_date - date).days)

        if tender.status == "active.tendering" and tender.enquiryPeriod:

            if enquiry_period.startDate < date <= tender_period.endDate:
                enquiry_period.endDate = calculate_tender_business_date(
                    enquiry_period.endDate, delta, tender, True)

                enquiry_period.clarificationsUntil = calculate_tender_business_date(
                    enquiry_period.clarificationsUntil, delta, tender, True)

                tender_period.endDate = calculate_tender_business_date(
                    tender_period.endDate, delta, tender, True)

                complaint_period.endDate = calculate_tender_business_date(
                    complaint_period.endDate, delta, tender, True)

                if auction_period.shouldStartAfter:
                    auction_period.shouldStartAfter = calculate_tender_business_date(
                        parse_date(auction_period.shouldStartAfter), delta, tender, True).isoformat()

                if auction_period.startDate:
                    auction_period.startDate = calculate_tender_business_date(
                        auction_period.startDate, delta, tender, True)

            elif auction_period and tender_period.endDate and auction_period.shouldStartAfter\
                    and tender_period.endDate < date <= parse_date(auction_period.shouldStartAfter):

                auction_period.shouldStartAfter = calculate_tender_business_date(
                    auction_period.shouldStartAfter, delta, tender, True)
                auction_period.startDate = calculate_tender_business_date(
                    auction_period.startDate, delta, tender, True)
        elif tender.status in ["active.qualification", "active.awarded"]:
            for award in tender.awards:
                complaint_period = award.complaintPeriod
                if complaint_period and complaint_period.startDate and complaint_period.endDate \
                        and award.complaintPeriod.startDate < date < award.complaintPeriod.endDate:
                    award.complaintPeriod.endDate = calculate_tender_business_date(
                        award.complaintPeriod.endDate, delta, tender, True)

