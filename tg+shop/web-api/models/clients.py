from pydantic import BaseModel


class ClientsModel(BaseModel):
    first_name: str = "Siman"
    last_name: str = "Nowal"
    email: str = None
    phone_number: str = None
    delivery_type: str = "courier"
    courier_street: str = "Biver, st."
    courier_apt: str = "13A"
    courier_home: str = "1E/2"
    courier_floor: str = ""
    city: str = "Erthevina"
    post_office_number: str = ""
    payment: str = "cash"

