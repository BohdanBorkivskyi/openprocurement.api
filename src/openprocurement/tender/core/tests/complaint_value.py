# -*- coding: utf-8 -*-
from openprocurement.api.tests.base import singleton_app, app
from openprocurement.tender.belowthreshold.tests.base import test_author, test_draft_complaint
from openprocurement.tender.openua.tests.base import test_tender_data
from openprocurement.tender.core.models import Complaint
from openprocurement.tender.core.constants import (
    COMPLAINT_MIN_AMOUNT, COMPLAINT_MAX_AMOUNT,
    COMPLAINT_ENHANCED_MIN_AMOUNT, COMPLAINT_ENHANCED_MAX_AMOUNT
)
from copy import deepcopy
from mock import patch, Mock
import pytest

test_tender_data = deepcopy(test_tender_data)
complaint_data = deepcopy(test_draft_complaint)


def create_tender(app, tender_data):
    app.authorization = ("Basic", ("broker", "broker"))
    response = app.post_json("/tenders", dict(data=tender_data))
    assert response.status == "201 Created"
    return response.json


def test_complaint_value_change(app):
    """
    value should be calculated only once for a complaint
    """
    test_tender_data["value"]["amount"] = 1000  # we want minimum complaint value
    tender = create_tender(app, test_tender_data)
    response = app.post_json(
        "/tenders/{}/complaints".format(tender["data"]["id"]),
        {"data": complaint_data},
    )
    response_data = response.json["data"]
    assert "value" in response_data
    expected_value = {"currency": "UAH", "amount": COMPLAINT_MIN_AMOUNT}
    assert response_data["value"] == expected_value

    # if we deploy new constant values the value shouldn't change
    with patch("openprocurement.tender.core.models.COMPLAINT_MIN_AMOUNT", 40):
        response = app.get("/tenders/{}".format(tender["data"]["id"]))
        complaint = response.json["data"].get("complaints")[0]
        assert complaint["value"] == expected_value


def test_post_pending_complaint():
    """
    only draft complaints have value
    """
    complaint = Complaint(
        {
            "title": "complaint title",
            "status": "pending",
            "description": "complaint description",
            "author": test_author
        }
    )
    root = Mock(__parent__=None)
    root.request.validated = {"tender": {
        "status": "active.tendering",
        "procurementMethodType": "anything but esco",
        "value": {"amount": 1000}
    }}
    complaint["__parent__"] = root
    result = complaint.serialize()
    assert "value" not in result


def test_post_draft_claim():
    """
    claims don't have value
    """
    complaint = Complaint(
        {
            "title": "complaint title",
            "status": "draft",
            "description": "complaint description",
            "author": test_author
        }
    )
    root = Mock(__parent__=None)
    root.request.validated = {"tender": {
        "status": "active.tendering",
        "procurementMethodType": "anything but esco",
        "value": {"amount": 1000}
    }}
    complaint["__parent__"] = root
    result = complaint.serialize()
    assert "value" not in result


def test_post_not_uah_complaint():
    """
    applying currency rates
    """
    complaint = Complaint(
        {
            "title": "complaint title",
            "status": "draft",
            "type": "complaint",
            "description": "complaint description",
            "author": test_author
        }
    )
    root = Mock(__parent__=None)
    root.request.validated = {"tender": {
        "status": "active.tendering",
        "procurementMethodType": "anything but esco",
        "value": {"amount": 30001, "currency": "EUR"}
    }}
    root.request.currency_rates = [
        {
            "cc": "USD",
            "rate": 8.0
        },
        {
            "cc": "EUR",
            "rate": 30.0
        }
    ]
    complaint["__parent__"] = root
    result = complaint.serialize()
    assert "value" in result
    # 30001 * 30 = 900030
    # 900030 * 0.3 / 100 = 2700.09 => 2710
    assert result["value"] == {'currency': 'UAH', 'amount': 2710}


def test_post_not_uah_complaint_esco():
    """
    Esco with currency rates
    """
    complaint = Complaint(
        {
            "title": "complaint title",
            "status": "draft",
            "type": "complaint",
            "description": "complaint description",
            "author": test_author
        }
    )
    root = Mock(__parent__=None)
    root.request.validated = {
        "tender": {
            "status": "awarding",
            "procurementMethodType": "esco",
        },
        "award": {
            "value": {"amount": 70002, "currency": "USD"}
        }
    }
    root.request.currency_rates = [
        {
            "cc": "USD",
            "rate": 8.0
        },
        {
            "cc": "EUR",
            "rate": 12.0
        }
    ]
    complaint["__parent__"] = root
    result = complaint.serialize()
    assert "value" in result
    # Converting 70002 USD into 560016.0 UAH using rate 8.0
    # 560016.0 * 0.6/100 = 3360.096 => 3370
    assert result["value"] == {'currency': 'UAH', 'amount': 3370}


@pytest.mark.parametrize("test_data", [
    (1000, COMPLAINT_MIN_AMOUNT),
    (999999999999, COMPLAINT_MAX_AMOUNT),
    (901000, 2710),  # 901000 * 0.3 / 100 = 2703.0 => 2710
])
def test_complaint_non_esco_tendering_rates(test_data):
    tender_amount, expected_complaint_amount = test_data
    complaint = Complaint(complaint_data)
    root = Mock(__parent__=None)
    root.request.validated = {"tender": {
        "status": "active.tendering",
        "procurementMethodType": "anything but esco",
        "value": {
            "amount": tender_amount,
            "currency": "UAH"
        }
    }}
    complaint["__parent__"] = root

    result = complaint.serialize()
    assert "value" in result
    assert result["value"] == {"currency": "UAH", "amount": expected_complaint_amount}


@pytest.mark.parametrize("test_data", [
    (1000, COMPLAINT_ENHANCED_MIN_AMOUNT),
    (999999999999, COMPLAINT_ENHANCED_MAX_AMOUNT),
    (901000, 5410),  # 901000 * 0.6 / 100 = 5406.0 => 5410
])
def test_non_esco_enhanced_rates(test_data):
    tender_amount, expected_complaint_amount = test_data

    complaint = Complaint(complaint_data)
    root = Mock(__parent__=None)
    root.request.validated = {"tender": {
        "status": "active.qualification",
        "procurementMethodType": "anything but esco",
        "value": {
            "amount": tender_amount,
            "currency": "UAH"
        }
    }}
    complaint["__parent__"] = root

    result = complaint.serialize()
    assert "value" in result
    assert result["value"] == {"currency": "UAH", "amount": expected_complaint_amount}


@pytest.mark.parametrize("status", ["active.tendering", "active.pre-qualification.stand-still"])
def test_esco_tendering(status):
    complaint = Complaint(complaint_data)
    root = Mock(__parent__=None)
    root.request.validated = {"tender": {
        "status": status,
        "procurementMethodType": "esco"
    }}
    complaint["__parent__"] = root

    result = complaint.serialize()
    assert "value" in result
    assert result["value"] == {"currency": "UAH", "amount": COMPLAINT_MIN_AMOUNT}


@pytest.mark.parametrize("test_data", [
    (1000, COMPLAINT_ENHANCED_MIN_AMOUNT),
    (999999999999, COMPLAINT_ENHANCED_MAX_AMOUNT),
    (901000, 5410),  # 901000 * 0.6 / 100 = 5406.0 => 5410
])
def test_esco_not_tendering_rates(test_data):
    award_amount, expected_complaint_amount = test_data
    complaint = Complaint(complaint_data)
    root = Mock(__parent__=None)
    root.request.validated = {
        "tender": {
            "status": "any but tendering and pre-qualification.stand-still",
            "procurementMethodType": "esco"
        },
        "award": {
            "value": {
                "amount": award_amount,
                "currency": "UAH"
            }
        },
    }
    complaint["__parent__"] = root
    result = complaint.serialize()
    assert "value" in result
    assert result["value"] == {"currency": "UAH", "amount": expected_complaint_amount}

