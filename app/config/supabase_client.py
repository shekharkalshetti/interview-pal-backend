import os
from supabase import create_client, Client

# Get Supabase credentials from environment variables
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_KEY or not SUPABASE_URL:
    raise NameError("SUPABASE credentials not added to environment variables")

# Initialize the Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Export the Supabase client for reuse


def get_supabase_client() -> Client:
    return supabase
