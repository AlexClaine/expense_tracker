from decouple import config
from supabase import create_client

def get_supabase_client():
    supabase_url = config('SUPABASE_URL')
    supabase_key = config('SUPABASE_KEY')
    supabase = create_client(supabase_url, supabase_key)
    return supabase