import os 
from dotenv import load_dotenv 

load_dotenv ()

BOT_TOKEN =os .getenv ("BOT_TOKEN")
SUPABASE_URL =os .getenv ("SUPABASE_URL")
SUPABASE_KEY =os .getenv ("SUPABASE_KEY")

ADMIN_GROUP_ID =os .getenv ("ADMIN_GROUP_ID")
TRANSCRIPT_GROUP_ID =os .getenv ("TRANSCRIPT_GROUP_ID")
TRANSCRIPT_TOPIC_ID =os .getenv ("TRANSCRIPT_TOPIC_ID")
PUBLIC_GROUP_ID =os .getenv ("PUBLIC_GROUP_ID")
WELCOME_TOPIC_ID =os .getenv ("WELCOME_TOPIC_ID")

if not all ([BOT_TOKEN ,SUPABASE_URL ,SUPABASE_KEY ,ADMIN_GROUP_ID ]):
    raise ValueError ("Missing essential environment variables (BOT_TOKEN, SUPABASE_URL, SUPABASE_KEY, ADMIN_GROUP_ID).")
