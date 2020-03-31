# -*- coding: utf-8 -*-
from openprocurement.tender.core.adapters import TenderConfigurator
from openprocurement.tender.location.constants import STATUS4ROLE


class TenderLocationConfigurator(TenderConfigurator):
    """ BelowThreshold Tender configuration adapter """

    name = "Location configurator"

    # Dictionary with allowed complaint statuses for operations for each role
    allowed_statuses_for_complaint_operations_for_roles = STATUS4ROLE
