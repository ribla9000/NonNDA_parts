import numpy as np
from core.config import BOT_CONTEXT_MESSAGE
from core.response import response_error, response_success
from fastapi import APIRouter, Depends
from typing import Annotated
from repository.tools import bordering_text
from repository.database.business_data import BusinessDataRepository
from repository.assistant_api import AssistantAPI
from repository.assistant import AIChatBot
from repository.dependecies import auth_required
from models.business_data import BusinessDataModel, ChatModel


router = APIRouter()


@router.post("")
async def save_content_embedding(data: BusinessDataModel, token: Annotated[dict, Depends(auth_required)]):
    is_valid, payload = token
    if not is_valid:
        return response_error(payload)

    _data = data.model_dump()
    paragraphs = bordering_text(text=_data["content"])
    _data["embedding"] = []

    for paragraph in paragraphs:
        embedding = AIChatBot.tokenize_data(data=paragraph)
        _data["embedding"] = embedding

        business_data_id = await BusinessDataRepository.create(_data)

    return response_success()


@router.post("/")
async def create_chat(chat: ChatModel, token: Annotated[dict, Depends(auth_required)]):
    is_valid, payload = token
    if not is_valid:
        return response_error(payload)

    _chat = chat.model_dump()
    embedding = AIChatBot.tokenize_data(data=_chat["content"])
    content = _chat["content"].replace("\n", " ")
    articles = ""
    business_data = await BusinessDataRepository.get_by_closest_l2_distance(
        embedding=embedding,
        user_id=_chat["user_id"]
    )

    ind = 0
    for item in business_data:
        ind += 1
        articles += f"{item['content']}\n"

    bot_context = BOT_CONTEXT_MESSAGE.replace("{articleText}", articles)
    bot_context = bot_context.replace("{userQuery}", content)
    bot_context = bot_context.replace("{userName}", str(_chat['user_name']))
    data_gpt, prompt = AIChatBot.create_message(bot_context=bot_context, content=articles, user_query=content)
    data_gpt = data_gpt.model_dump()
    return response_success(data_gpt)


@router.post("g")
async def create_chat_message(chat: ChatModel, token: Annotated[str, Depends(auth_required)]):
    is_valid, payload = token
    if not is_valid:
        return response_error(payload)

    _chat = chat.model_dump()
    content = _chat["content"].replace("\n", " ")
    assistant = AssistantAPI.assistant_chat(user_query=content)

    return response_success(assistant)
