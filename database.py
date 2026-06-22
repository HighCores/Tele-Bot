import os 
from dotenv import load_dotenv 
from supabase import create_client ,Client 

load_dotenv ()

class BetaDatabase :
    def __init__ (self ):
        url =os .getenv ("SUPABASE_URL")
        key =os .getenv ("SUPABASE_KEY")
        self .client :Client =create_client (url ,key )

    def get_all_services (self ):
        return self .client .table ("services").select ("*").execute ().data 

    def get_all_employees (self ):
        return self .client .table ("employees").select ("*").execute ().data 

    def get_auto_reply (self ,text ):

        res =self .client .table ("auto_responses").select ("response").ilike ("keyword",f"%{text }%").execute ()
        return res .data [0 ]['response']if res .data else None 

db =BetaDatabase ()