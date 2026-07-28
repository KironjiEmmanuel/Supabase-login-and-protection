import os
from fastapi import HTTPException,Depends
from fastapi import Depends, Header, HTTPException
from fastapi.security import HTTPBearer,HTTPAuthorizationCredentials
from supabase import create_client, Client
from supabase_auth.errors import AuthError

supabase_url: str = os.environ.get("SUPABASE_URL")
supabase_key: str = os.environ.get("SUPABASE_KEY")
supabase_service_key=os.environ.get('SUPABASE_SERVICE_KEY')
supabase: Client = create_client(supabase_url, supabase_key)
supabase_admin: Client=create_client(supabase_url,supabase_service_key)

bearer_scheme= HTTPBearer(auto_error=False)
def get_current_user(credentials:HTTPAuthorizationCredentials=Depends(bearer_scheme)):
    if credentials is None:
        raise HTTPException(status_code=401, detail="Access token required")

    token = credentials.credentials

    try:
        result = supabase.auth.get_user(token)
    except AuthError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return result.user, token