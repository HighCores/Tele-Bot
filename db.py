from supabase import create_client ,Client 
from config import SUPABASE_URL ,SUPABASE_KEY 

supabase :Client =create_client (SUPABASE_URL ,SUPABASE_KEY )

def create_ticket (ticket_id :str ,user_id :int ,user_name :str ,subject :str ,type_val :str ,topic_id :int ):
    supabase .table ("tg_tickets").insert ({
    "ticket_id":ticket_id ,
    "user_id":user_id ,
    "user_name":user_name ,
    "subject":subject ,
    "type":type_val ,
    "topic_id":topic_id ,
    "status":"open"
    }).execute ()

def get_ticket_by_topic (topic_id :int ):
    res =supabase .table ("tg_tickets").select ("*").eq ("topic_id",topic_id ).limit (1 ).execute ()
    return res .data [0 ]if res .data else None 

def get_ticket_by_user (user_id :int ):
    res =supabase .table ("tg_tickets").select ("*").eq ("user_id",user_id ).eq ("status","open").limit (1 ).execute ()
    return res .data [0 ]if res .data else None 

def close_ticket (ticket_id :str ,closed_by :str ):
    supabase .table ("tg_tickets").update ({"status":"closed","closed_by":closed_by }).eq ("ticket_id",ticket_id ).execute ()

def save_ticket_message (ticket_id :str ,user_id :int ,user_name :str ,content :str ,message_id :int ):
    supabase .table ("tg_ticket_messages").insert ({
    "ticket_id":ticket_id ,
    "user_id":user_id ,
    "user_name":user_name ,
    "content":content ,
    "message_id":message_id 
    }).execute ()

def create_order (order_num :str ,user_id :int ,user_name :str ,project :str ,contact :str ,eta :str ,topic_id :int ):

    supabase .table ("tg_tickets").insert ({
    "ticket_id":order_num ,
    "user_id":user_id ,
    "user_name":user_name ,
    "status":"open",
    "topic_id":topic_id ,
    "subject":project ,
    "type":"Order"
    }).execute ()

    supabase .table ("tg_orders").insert ({
    "order_num":order_num ,
    "user_id":user_id ,
    "user_name":user_name ,
    "project":project ,
    "contact":contact ,
    "eta":eta ,
    "topic_id":topic_id ,
    "status":"pending"
    }).execute ()

def save_order_items (order_num :str ,items :list ):
    data =[{"order_num":order_num ,"item_id":i ['id'],"item_name":i ['name'],"price":i ['price']}for i in items ]
    if data :
        supabase .table ("tg_order_items").insert (data ).execute ()

def get_order_by_topic (topic_id :int ):
    res =supabase .table ("tg_orders").select ("*").eq ("topic_id",topic_id ).limit (1 ).execute ()
    return res .data [0 ]if res .data else None 

def get_order_by_user (user_id :int ):
    res =supabase .table ("tg_orders").select ("*").eq ("user_id",user_id ).eq ("status","pending").limit (1 ).execute ()
    return res .data [0 ]if res .data else None 

def get_voucher (code :str ):
    res =supabase .table ("tg_vouchers").select ("*").ilike ("code",code ).eq ("is_used",False ).limit (1 ).execute ()
    return res .data [0 ]if res .data else None 

def mark_voucher_used (code :str ,user_id :int ):
    supabase .table ("tg_vouchers").update ({"is_used":True ,"user_id":user_id }).ilike ("code",code ).execute ()

def get_next_id (prefix :str ):
    res =supabase .table ("tg_settings").select ("value").eq ("key",f"next_id_{prefix }").limit (1 ).execute ()
    nxt =1 
    if res .data :
        nxt =int (res .data [0 ]['value'])
    supabase .table ("tg_settings").upsert ({"key":f"next_id_{prefix }","value":str (nxt +1 )}).execute ()
    return f"{prefix }-{nxt :04d}"

def add_user_for_broadcast (user_id :int ):
    try :
        supabase .table ("tg_settings").upsert ({"key":f"user_{user_id }","value":str (user_id )}).execute ()
    except Exception :
        pass 

def get_all_users ():
    res =supabase .table ("tg_settings").select ("value").like ("key","user_%").execute ()
    return [int (u ['value'])for u in res .data ]

def get_ticket_messages (ticket_id :str ):
    res =supabase .table ("tg_ticket_messages").select ("*").eq ("ticket_id",ticket_id ).order ("created_at").execute ()
    return res .data 
