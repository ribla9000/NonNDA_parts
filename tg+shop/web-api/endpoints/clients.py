import requests
from fastapi import APIRouter, Request, Response
from models.clients import ClientsModel
from repository.clients import ClientsRepository
from core.response import response_success, response_error

router = APIRouter()


@router.post("/create/")
async def create_client(client: ClientsModel):
    values = client.model_dump()
    client_id = await ClientsRepository.create(values)
    payload = {"client_id": client_id}
    return response_success(payload)


@router.get("/{client_id}/info")
async def get_client(client_id: int):
    client = await ClientsRepository.get_by_id(client_id)

    if client is None:
        err = {"code": 404, "message": "CLIENT DOESN'T EXIST"}
        return response_error(err)

    payload = {"user": client, "user_info": ""}
    return response_success(payload)
