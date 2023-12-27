from fastapi import APIRouter
from core.response import response_success, response_error


router = APIRouter()


@router.post("/contact-form/")
async def create_contact_form():
    guest_id = ...
