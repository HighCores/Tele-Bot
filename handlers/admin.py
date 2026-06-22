from aiogram import Router ,F ,Bot 
from aiogram .filters import Command ,CommandObject 
from aiogram .types import Message ,FSInputFile ,InlineKeyboardButton ,CallbackQuery 
from aiogram .utils .keyboard import InlineKeyboardBuilder 
from config import ADMIN_GROUP_ID ,TRANSCRIPT_GROUP_ID ,TRANSCRIPT_TOPIC_ID 
import db 
import os 

router =Router ()

@router .message (Command ("clear"))
async def clear_command (message :Message ,command :CommandObject ,bot :Bot ):
    if message .chat .type =="private":
        return 

    try :
        member =await bot .get_chat_member (message .chat .id ,message .from_user .id )
        if member .status not in ["administrator","creator"]:
            await message .answer ("❌ You must be an admin to use this command.")
            return 
    except Exception as e :
        await message .answer (f"❌ Error verifying admin status: {e }")
        return 

    try :
        amount =int (command .args )if command .args else 10 
    except ValueError :
        amount =10 

    deleted =0 
    for i in range (amount +1 ):
        try :
            await bot .delete_message (chat_id =message .chat .id ,message_id =message .message_id -i )
            deleted +=1 
        except Exception :
            pass 

    if deleted <=1 :
        await message .answer (f"⚠️ Note: Could only delete {deleted } messages. Telegram bots cannot delete messages older than 48h.")

@router .message (Command ("close"))
async def close_ticket_command (message :Message ,bot :Bot ):
    if message .chat .type =="private"or not message .message_thread_id :
        return 

    member =await bot .get_chat_member (message .chat .id ,message .from_user .id )
    if member .status not in ["administrator","creator"]:
        return 

    topic_id =message .message_thread_id 
    ticket =db .get_ticket_by_topic (topic_id )

    if ticket :
        db .close_ticket (ticket ['ticket_id'],message .from_user .full_name )

        messages =db .get_ticket_messages (ticket ['ticket_id'])
        transcript_path =f"transcript_{ticket ['ticket_id']}.txt"
        with open (transcript_path ,"w",encoding ="utf-8")as f :
            f .write (f"Transcript for Ticket {ticket ['ticket_id']}\n")
            f .write ("="*40 +"\n")
            for msg in messages :
                f .write (f"[{msg ['created_at'][:19 ]}] {msg ['user_name']}: {msg ['content']}\n")

        doc =FSInputFile (transcript_path )

from aiogram .fsm .context import FSMContext 
from aiogram .fsm .state import State ,StatesGroup 

class AdminState (StatesGroup ):
    waiting_for_rename =State ()

@router .callback_query (F .data .startswith ("admin_claim_"))
async def admin_claim_ticket (query :CallbackQuery ,bot :Bot ):

    await query .message .answer (f"🙋‍♂️ <b>Ticket Claimed</b>\nThis ticket will be handled by <b>{query .from_user .full_name }</b>.")
    await query .answer ("Claimed successfully!")

@router .callback_query (F .data .startswith ("admin_rename_"))
async def admin_rename_ticket (query :CallbackQuery ,state :FSMContext ):
    ticket_id =query .data .split ("_")[2 ]
    await state .update_data (rename_topic_id =query .message .message_thread_id )
    await state .set_state (AdminState .waiting_for_rename )
    await query .message .answer ("📝 Please type the new name for this ticket:")
    await query .answer ()

@router .message (AdminState .waiting_for_rename )
async def process_rename (message :Message ,state :FSMContext ,bot :Bot ):
    data =await state .get_data ()
    topic_id =data .get ("rename_topic_id")

    if message .message_thread_id ==topic_id :
        try :
            await bot .edit_forum_topic (chat_id =message .chat .id ,message_thread_id =topic_id ,name =message .text )
            await message .answer ("✅ Topic renamed successfully!")
        except Exception as e :
            await message .answer (f"❌ Failed to rename: {e }")

        await state .clear ()

@router .callback_query (F .data .startswith ("admin_reopen_"))
async def admin_reopen_ticket (query :CallbackQuery ,bot :Bot ):
    try :
        await bot .reopen_forum_topic (chat_id =ADMIN_GROUP_ID ,message_thread_id =query .message .message_thread_id )
        await query .message .edit_text ("🔓 <b>TICKET REOPENED</b>\nAccess restored.")
    except Exception as e :
        await query .answer (f"Failed: {e }",show_alert =True )
    await query .answer ()

@router .callback_query (F .data .startswith ("admin_delete_"))
async def admin_delete_ticket (query :CallbackQuery ,bot :Bot ):
    try :
        await bot .delete_forum_topic (chat_id =ADMIN_GROUP_ID ,message_thread_id =query .message .message_thread_id )
    except Exception as e :
        await query .answer (f"Failed: {e }",show_alert =True )

@router .callback_query (F .data .startswith ("admin_transcript_"))
async def admin_transcript_ticket (query :CallbackQuery ,bot :Bot ):
    ticket_id =query .data .split ("_")[2 ]
    url =f"https://high-core-dc-bot-production.up.railway.app/view/transcript/{ticket_id }"

    b =InlineKeyboardBuilder ()
    b .row (InlineKeyboardButton (text ="View Web Transcript",url =url ))

    await bot .send_message (
    chat_id =ADMIN_GROUP_ID ,
    message_thread_id =query .message .message_thread_id ,
    text =f"📜 <b>Transcript for {ticket_id }</b>\nRequested by {query .from_user .full_name }",
    reply_markup =b .as_markup ()
    )
    await query .answer ()

@router .callback_query (F .data .startswith ("admin_close_"))
async def admin_close_ticket (query :CallbackQuery ,bot :Bot ):
    ticket_id =query .data .split ("_")[2 ]

    table ="tg_orders"if ticket_id .startswith ("ORD-")else "tg_tickets"
    id_col ="order_num"if ticket_id .startswith ("ORD-")else "ticket_id"

    res =db .supabase .table (table ).select ("*").eq (id_col ,ticket_id ).execute ()
    if not res .data :
        await query .answer ("Record not found.")
        return 
    ticket =res .data [0 ]

    if ticket_id .startswith ("ORD-"):
        db .supabase .table ("tg_orders").update ({"status":"closed"}).eq ("order_num",ticket_id ).execute ()

    db .close_ticket (ticket_id ,query .from_user .full_name )

    url =f"https://high-core-dc-bot-production.up.railway.app/view/transcript/{ticket_id }"
    b_url =InlineKeyboardBuilder ()
    b_url .row (InlineKeyboardButton (text ="View Web Transcript",url =url ))

    try :
        await bot .send_message (
        chat_id =TRANSCRIPT_GROUP_ID if TRANSCRIPT_GROUP_ID else ADMIN_GROUP_ID ,
        message_thread_id =int (TRANSCRIPT_TOPIC_ID )if TRANSCRIPT_TOPIC_ID else None ,
        text =f"▶ <b>TRANSCRIPT • Archive — Case #{ticket_id }</b>\n\n<b>User:</b> {ticket ['user_name']} ({ticket ['user_id']})\n<b>Closed By:</b> {query .from_user .full_name }",
        reply_markup =b_url .as_markup ()
        )
    except Exception as e :
        pass 

    try :
        b =InlineKeyboardBuilder ()
        for i in range (1 ,6 ):
            b .button (text =f"{i } ⭐",callback_data =f"rate_{ticket_id }_{i }")
        b .adjust (5 )

        await bot .send_message (
        ticket ['user_id'],
        f"🔒 Your ticket <b>{ticket_id }</b> has been closed by {query .from_user .full_name }.\n\nPlease rate your experience:",
        reply_markup =b .as_markup ()
        )
    except :
        pass 

    try :
        await bot .close_forum_topic (chat_id =ADMIN_GROUP_ID ,message_thread_id =ticket ['topic_id'])
    except :
        pass 

    cp_kb =InlineKeyboardBuilder ()
    cp_kb .row (
    InlineKeyboardButton (text ="Reopen",callback_data =f"admin_reopen_{ticket_id }"),
    InlineKeyboardButton (text ="Transcript",callback_data =f"admin_transcript_{ticket_id }"),
    InlineKeyboardButton (text ="Delete",callback_data =f"admin_delete_{ticket_id }")
    )

    cp_text =f"🔒 <b>TICKET CLOSED</b>\nAgent <b>{query .from_user .full_name }</b> has closed this ticket.\n\nSelect an action below."
    try :
        from aiogram .types import FSInputFile 
        await bot .send_photo (
        chat_id =ADMIN_GROUP_ID ,
        message_thread_id =ticket ['topic_id'],
        photo =FSInputFile ("assets/support.png"),
        caption =cp_text ,
        reply_markup =cp_kb .as_markup ()
        )
    except Exception :
        await bot .send_message (
        chat_id =ADMIN_GROUP_ID ,
        message_thread_id =ticket ['topic_id'],
        text =cp_text ,
        reply_markup =cp_kb .as_markup ()
        )

    try :
        msg_text =query .message .text or query .message .caption or ""
        new_text =msg_text +f"\n\n❌ <b>Closed by:</b> {query .from_user .full_name }"
        if query .message .photo or query .message .document :
            await query .message .edit_caption (caption =new_text )
        else :
            await query .message .edit_text (new_text )
    except :
        pass 
    await query .answer ("Ticket closed!")

@router .message (Command ("close"))
async def close_ticket_command (message :Message ,bot :Bot ):
    if str (message .chat .id )!=str (ADMIN_GROUP_ID )or not message .message_thread_id :
        return 

    topic_id =message .message_thread_id 
    ticket =db .get_ticket_by_topic (topic_id )

    if ticket :
        ticket_id =ticket ['ticket_id']
        db .close_ticket (ticket_id ,message .from_user .full_name )

        url =f"https://high-core-dc-bot-production.up.railway.app/view/transcript/{ticket_id }"
        b_url =InlineKeyboardBuilder ()
        b_url .row (InlineKeyboardButton (text ="View Web Transcript",url =url ))

        try :
            await bot .send_message (
            chat_id =TRANSCRIPT_GROUP_ID if TRANSCRIPT_GROUP_ID else ADMIN_GROUP_ID ,
            message_thread_id =int (TRANSCRIPT_TOPIC_ID )if TRANSCRIPT_TOPIC_ID else None ,
            text =f"▶ <b>TRANSCRIPT • Archive — Case #{ticket_id }</b>\n\n<b>User:</b> {ticket ['user_name']} ({ticket ['user_id']})\n<b>Closed By:</b> {message .from_user .full_name }",
            reply_markup =b_url .as_markup ()
            )
        except Exception as e :
            await message .answer (f"Failed to send transcript: {e }")

        try :
            b =InlineKeyboardBuilder ()
            for i in range (1 ,6 ):
                b .button (text =f"{i } ⭐",callback_data =f"rate_{ticket_id }_{i }")
            b .adjust (5 )

            await bot .send_message (
            ticket ['user_id'],
            f"🔒 Your ticket <b>{ticket_id }</b> has been closed by {message .from_user .full_name }.\n\nPlease rate your experience:",
            reply_markup =b .as_markup ()
            )
        except :
            pass 

        try :
            await bot .close_forum_topic (chat_id =ADMIN_GROUP_ID ,message_thread_id =topic_id )
        except :
            pass 

        cp_kb =InlineKeyboardBuilder ()
        cp_kb .row (
        InlineKeyboardButton (text ="Reopen",callback_data =f"admin_reopen_{ticket_id }"),
        InlineKeyboardButton (text ="Transcript",callback_data =f"admin_transcript_{ticket_id }"),
        InlineKeyboardButton (text ="Delete",callback_data =f"admin_delete_{ticket_id }")
        )
        cp_text =f"🔒 <b>TICKET CLOSED</b>\nAgent {message .from_user .full_name } has closed this ticket.\n\nSelect an action below."
        try :
            from aiogram .types import FSInputFile 
            await bot .send_photo (chat_id =ADMIN_GROUP_ID ,message_thread_id =topic_id ,photo =FSInputFile ("assets/support.png"),caption =cp_text ,reply_markup =cp_kb .as_markup ())
        except Exception :
            await bot .send_message (chat_id =ADMIN_GROUP_ID ,message_thread_id =topic_id ,text =cp_text ,reply_markup =cp_kb .as_markup ())
    else :
        await message .answer ("No open ticket found for this topic.")

class FeedbackState (StatesGroup ):
    waiting_for_feedback =State ()

@router .callback_query (F .data .startswith ("rate_"))
async def process_rating (query :CallbackQuery ,state :FSMContext ):
    parts =query .data .split ("_")
    ticket_id =parts [1 ]
    rating =parts [2 ]

    await state .update_data (rating =rating ,ticket_id =ticket_id )
    await state .set_state (FeedbackState .waiting_for_feedback )
    await query .message .edit_text (f"Thank you for rating {rating } ⭐!\nPlease type your feedback text below:")
    await query .answer ()

@router .message (FeedbackState .waiting_for_feedback )
async def process_feedback_text (message :Message ,state :FSMContext ,bot :Bot ):
    from utils .feedback_generator import generate_feedback_image 
    from config import PUBLIC_GROUP_ID 
    import os 

    data =await state .get_data ()
    rating =data .get ("rating",5 )
    ticket_id =data .get ("ticket_id","UNKNOWN")
    feedback_text =message .text 

    await message .answer ("✅ Thank you! Your feedback has been submitted successfully.")
    await state .clear ()

    try :
        out_path =f"feedback_out_{ticket_id }.png"
        generate_feedback_image (int (rating ),feedback_text ,out_path )

        photo =FSInputFile (out_path )

        user_mention =f"@{message .from_user .username }"if message .from_user .username else f"<a href='tg://user?id={message .from_user .id }'>{message .from_user .full_name }</a>"

        await bot .send_photo (
        chat_id =PUBLIC_GROUP_ID ,
        message_thread_id =248 ,
        photo =photo ,
        caption =f"### Feedback from {user_mention }",
        parse_mode ="HTML"
        )
        os .remove (out_path )
    except Exception as e :
        print (f"Error sending feedback image: {e }")

@router .message (Command ("broadcast"))
async def broadcast_command (message :Message ,command :CommandObject ,bot :Bot ):
    if message .chat .type =="private":
        return 

    member =await bot .get_chat_member (message .chat .id ,message .from_user .id )
    if member .status not in ["administrator","creator"]:
        return 

    text =command .args 
    if not text :
        await message .answer ("Usage: /broadcast [message]")
        return 

    users =db .get_all_users ()
    count =0 
    for uid in users :
        try :
            await bot .send_message (uid ,f"📢 <b>Broadcast</b>\n\n{text }")
            count +=1 
        except Exception :
            pass 

    await message .answer (f"✅ Broadcast sent to {count } users.")

@router .message (Command ("invoice"))
async def invoice_command (message :Message ,command :CommandObject ,bot :Bot ):
    if message .chat .type =="private":
        return 

    member =await bot .get_chat_member (message .chat .id ,message .from_user .id )
    if member .status not in ["administrator","creator"]:
        return 
    if not message .message_thread_id :
        return 

    topic_id =message .message_thread_id 
    order =db .get_order_by_topic (topic_id )

    if not order :
        await message .answer ("This is not an order topic.")
        return 

    inv_text =(
    f"🧾 <b>INVOICE - {order ['order_num']}</b>\n"
    f"<b>Client:</b> {order ['user_name']}\n"
    f"<b>Project:</b> {order ['project']}\n"
    f"<b>Total Amount:</b> ${order ['total_price']}\n\n"
    f"Please proceed with the payment."
    )

    await message .answer ("Invoice sent to client.")
    try :
        await bot .send_message (order ['user_id'],inv_text )
    except Exception as e :
        await message .answer (f"Failed to send invoice: {e }")
