import os

from fastapi import APIRouter
from fastapi.responses import FileResponse


router = APIRouter(prefix="", tags=["statics"])


@router.get("/login")
async def serve_login_page():
    return FileResponse(os.path.join("static", "login.html"))


@router.get("/register")
async def serve_register_page():
    return FileResponse(os.path.join("static", "register.html"))


@router.get("/profile")
async def serve_profile_page():
    return FileResponse(os.path.join("static", "profile.html"))


@router.get("/edit-profile")
async def serve_edit_profile_page():
    return FileResponse(os.path.join("static", "edit-profile.html"))
