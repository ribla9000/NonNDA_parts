import os
import requests
from core.config import MONOBANK_HEADERS, MONOBANK_PUBKEY, MONOBANK_SIGNATURE_TOKEN
from core.response import response_success, response_error
from repository.tools import validate_pub_key, rewrite_env
from fastapi import APIRouter, Request
from models.payments import Invoices


router = APIRouter()


@router.post("/create-invoice/")
async def create_invoice(invoices: Invoices):
    responses = []
    _invoices = invoices.to_dict()

    for invoice in _invoices:
        req = requests.post(url=invoice["url"], json=invoice["data"], headers=invoice["headers"])
        responses.append(req.json())

    return response_success(responses)


@router.get("/get-invoice/")
async def get_invoice(invoice_id: str, full_info: bool = False):
    if full_info:
        url = f"https://api.monobank.ua/api/merchant/invoice/payment-info?invoiceId={invoice_id}"
        req = requests.get(url=url, headers=MONOBANK_HEADERS)
    elif not full_info:
        url = f"https://api.monobank.ua/api/merchant/invoice/status?invoiceId={invoice_id}"
        req = requests.get(url=url, headers=MONOBANK_HEADERS)
    return req.json()


@router.post("/web")
async def get_request(request: Request):
    global MONOBANK_PUBKEY
    response = await request.json()
    body = await request.body()
    headers = request.headers
    is_valid = validate_pub_key(pub_key=MONOBANK_PUBKEY, x_sign=headers["x-sign"], body=body)

    if not is_valid:
        req = requests.get(url="https://api.monobank.ua/api/merchant/pubkey", headers=MONOBANK_HEADERS)
        new_pub_key = req.json().get("key")
        MONOBANK_PUBKEY = new_pub_key
        rewrite_env("ENV_MONOBANK_PUBKEY", new_pub_key)
        is_valid = validate_pub_key(pub_key=MONOBANK_PUBKEY, x_sign=headers["x-sign"], body=body)

        if not is_valid:
            return response_error({"code": 403, "message": "NOT VALID HOOK REQEUST"})

    return response_success(response)
