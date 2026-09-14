import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_ANON_KEY = os.environ["SUPABASE_ANON_KEY"]


def get_anon_client() -> Client:
    """A client with no user session — used only for signup/login."""
    return create_client(SUPABASE_URL, SUPABASE_ANON_KEY)


def get_user_client(access_token: str) -> Client:
    """A client scoped to one specific logged-in user's token.
    Created fresh per request so different users' data never mixes."""
    client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    client.postgrest.auth(access_token)
    return client


def sign_up(email: str, password: str):
    client = get_anon_client()
    result = client.auth.sign_up({"email": email, "password": password})
    return result


def sign_in(email: str, password: str):
    client = get_anon_client()
    result = client.auth.sign_in_with_password({"email": email, "password": password})
    return {
        "access_token": result.session.access_token,
        "refresh_token": result.session.refresh_token,
        "user_id": result.user.id,
        "email": result.user.email,
    }