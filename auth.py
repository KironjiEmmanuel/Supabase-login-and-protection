import os
from fastapi import Header, HTTPException
from supabase import create_client, Client
from supabase_auth.errors import AuthError

supabase_url: str = os.environ.get("SUPABASE_URL")
supabase_key: str = os.environ.get("SUPABASE_KEY")
supabase_service_key=os.environ.get('SUPABASE_SERVICE_KEY')
supabase: Client = create_client(supabase_url, supabase_key)
supabase_admin: Client=create_client(supabase_url,supabase_service_key)


def get_current_user(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Access token required")

    parts = authorization.split(" ", 1)
    if len(parts) != 2 or parts[0] != "Bearer" or not parts[1]:
        raise HTTPException(status_code=401, detail="Access token required")

    token = parts[1]

    try:
        result = supabase.auth.get_user(token)
    except AuthError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return result.user, token