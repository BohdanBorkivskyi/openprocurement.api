# -*- coding: utf-8 -*-
from logging import getLogger
from pyramid.interfaces import IRequest
from openprocurement.api.interfaces import IContentConfigurator
from openprocurement.tender.location.models import Tender, ILocationTender
from openprocurement.tender.location.adapters import TenderLocationConfigurator

LOGGER = getLogger("openprocurement.tender.location")


def includeme(config):
    LOGGER.info("Init tender.location plugin.")

    config.add_tender_procurementMethodType(Tender)
    config.scan("openprocurement.tender.location.views")
    #config.scan("openprocurement.tender.location.subscribers")
    config.registry.registerAdapter(
        TenderLocationConfigurator, (ILocationTender, IRequest), IContentConfigurator
    )
