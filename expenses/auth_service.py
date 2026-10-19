from decouple import config
from supabase import create_client

def get_auth_client():
    return create_client(
        config("SUPABASE_URL"),
        config("SUPABASE_KEY")
    )

def register_user(email, password):
    client = get_auth_client()

    return client.auth.sign_up({
            'email': email,
            'password': password
        })

def login_user(email, password):
    client = get_auth_client()

    return client.auth.sign_in_with_password({
        'email': email,
        'password': password
    })

def logout_user(access_token, refresh_token):
    client = get_auth_client()
    client.auth.set_session(access_token, refresh_token)
    return client.auth.sign_out()

