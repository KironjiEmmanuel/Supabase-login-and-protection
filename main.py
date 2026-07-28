import os
from typing import Optional
from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI,Header,Depends,Request
from fastapi.exceptions import HTTPException as FastAPIHTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from supabase import create_client, Client
from supabase_auth.errors import AuthError
from auth import get_current_user,supabase_admin

supabase_url: str = os.environ.get("SUPABASE_URL")
supabase_key: str = os.environ.get("SUPABASE_KEY")

if not supabase_url or not supabase_key:
    raise RuntimeError("SUPABASE_URL and SUPABASE_KEY must be set in the environment variables.")
supabase: Client = create_client(supabase_url, supabase_key)
class AuthRequest(BaseModel):
    email: Optional[str] = None
    password: Optional[str] = None

app=FastAPI()

@app.exception_handler(FastAPIHTTPException)
def http_exception_handler(request: Request, exc: FastAPIHTTPException):
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})



@app.on_event("startup")
def startup_check():
    print("Server running and connected to Supabase")


@app.post("/auth/signup")
def signup(payload: AuthRequest):
    if not payload.email or not payload.password:
        return JSONResponse(status_code=400, content={"error": "email and password are required"})

    try:
        result = supabase.auth.sign_up({"email": payload.email, "password": payload.password})
    except AuthError as e:
        return JSONResponse(status_code=400, content={"error": e.message})

    return JSONResponse(status_code=201, content={"user": result.user.model_dump(mode="json")})


@app.post("/auth/login")
def login(payload: AuthRequest):
    if not payload.email or not payload.password:
        return JSONResponse(status_code=400, content={"error": "email and password are required"})

    try:
        result = supabase.auth.sign_in_with_password({"email": payload.email, "password": payload.password})
    except AuthError:
        return JSONResponse(status_code=401, content={"error": "Invalid login credentials"})

    return JSONResponse(status_code=200, content={
        "access_token": result.session.access_token,
        "refresh_token": result.session.refresh_token
    })
@app.get("/public/info")
def public_info():
    return {"message": "Welcome stranger! This info is public."}

@app.get("/protected/profile")
def protected_profile(user_token=Depends(get_current_user)):
   user,_=user_token
   return {
        "id": user.id,
        "email": user.email,
        "created_at": user.created_at.isoformat() if hasattr(user.created_at, "isoformat") else str(user.created_at)
    }
@app.get('/protected/dashboard')
def protected_dashboard(user_token=Depends(get_current_user)):
    user,_=user_token
    return {"message": f"Welcome to your dashboard, {user.email}"}
@app.post('/auth/logout')
def logout(user_token=Depends(get_current_user)):
    user,token=user_token
    supabase_admin.auth.admin.sign_out(token, scope="global")
    return JSONResponse(status_code=204,content=None)