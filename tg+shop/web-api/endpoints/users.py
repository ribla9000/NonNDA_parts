# from fastapi import APIRouter
# from models.users import UserModel
# from repository.database.web_users import UsersRepository
# from core.response import response_success, response_error
# from db.web_users import WebRoles
#
# router = APIRouter()
#
#
# @router.post("/create/")
# async def create_user(user: UserModel):
#     values = user.model_dump()
#     values["role"] = WebRoles.GUEST
#     user_id = await UsersRepository.create(values)
#     payload = {"user_id": user_id}
#     return response_success(payload)
#
#
# @router.get("/{user_id}/info")
# async def get_user(user_id: int):
#     user = await UsersRepository.get_by_id(user_id)
#
#     if user is None:
#         err = {"code": 404, "message": "USER DOESN'T EXIST"}
#         return response_error(err)
#
#     user.pop("role"), user.pop("tg_user_id")
#     payload = {"user": user, "user_info": ""}
#     return response_success(payload)
