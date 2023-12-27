from pydantic import BaseModel, Field
from typing import List
from core.config import WEBHOOK_URL, MONOBANK_HEADERS


class MonoBankInvoiceCreate(BaseModel):
    data: dict = {
      "amount": 0,
      "ccy": 980,
      "merchantPaymInfo": {
        "reference": "",
        "destination": "",
        "comment": "",
        "customerEmails": [],
        "basketOrder": []
      },
      "redirectUrl": "",
      "webHookUrl": WEBHOOK_URL,
      "validity": 3600,
    }

    def add_fields(self):
        values = {
            "url": "https://api.monobank.ua/api/merchant/invoice/create",
            "headers": MONOBANK_HEADERS
        }
        this = self.model_dump()
        this.update(values)
        return this


class Invoices(BaseModel):
    invoices: List[MonoBankInvoiceCreate]

    def to_dict(self):
        for item in range(0, len(self.invoices)):
            self.invoices[item] = self.invoices[item].add_fields()
        return self.invoices

