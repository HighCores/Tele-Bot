from aiogram import Router ,F ,Bot 
from aiogram .types import CallbackQuery ,Message ,InlineKeyboardButton 
from aiogram .utils .keyboard import InlineKeyboardBuilder 
from aiogram .fsm .context import FSMContext 
from aiogram .fsm .state import State ,StatesGroup 
from config import ADMIN_GROUP_ID 
import db 

router =Router ()

class TicketState (StatesGroup ):
    waiting_for_subject =State ()

from aiogram .fsm .storage .base import StorageKey 

@router .callback_query (F .data .startswith ("ticket_init_"))
async def init_ticket (query :CallbackQuery ,state :FSMContext ,bot :Bot ):
    ticket_type =query .data .split ("_")[-1 ].capitalize ()

    if query .message .chat .type !="private":
        try :

            key =StorageKey (bot_id =bot .id ,chat_id =query .from_user .id ,user_id =query .from_user .id )
            await state .storage .set_state (key ,TicketState .waiting_for_subject )
            await state .storage .set_data (key ,{"ticket_type":ticket_type })

            await bot .send_message (
            query .from_user .id ,
            f"<b>{ticket_type } Ticket</b>\nPlease reply with a brief description of your issue or request:"
            )
            await query .answer ("Please check your DMs! I've sent you a message.",show_alert =True )
        except Exception as e :
            await query .answer ("I can't DM you! Please send me a private message first to start the bot.",show_alert =True )
        return 

    await state .update_data (ticket_type =ticket_type )

    await query .message .answer (
    f"<b>{ticket_type } Ticket</b>\nPlease reply with a brief description of your issue or request:"
    )
    await state .set_state (TicketState .waiting_for_subject )
    await query .answer ()

@router .message (TicketState .waiting_for_subject )
async def process_ticket_subject (message :Message ,state :FSMContext ,bot :Bot ):
    if message .chat .type !="private":
        return 

    data =await state .get_data ()
    ticket_type =data ['ticket_type']
    subject =message .text 

    existing =db .get_ticket_by_user (message .from_user .id )
    if existing :
        await message .answer ("You already have an open ticket! Please close it before opening a new one.")
        await state .clear ()
        return 

    topic_name =f"{ticket_type } - {message .from_user .full_name }"
    try :
        topic =await bot .create_forum_topic (chat_id =ADMIN_GROUP_ID ,name =topic_name )
        topic_id =topic .message_thread_id 

        ticket_id =db .get_next_id ("TICK")
        db .create_ticket (
        ticket_id =ticket_id ,
        user_id =message .from_user .id ,
        user_name =message .from_user .full_name ,
        subject =subject ,
        type_val =ticket_type ,
        topic_id =topic_id 
        )

        b =InlineKeyboardBuilder ()
        admin_text =(
        f"🎫 <b>New {ticket_type } Ticket</b>\n"
        f"<b>Ticket ID:</b> {ticket_id }\n"
        f"<b>User:</b> {message .from_user .full_name } ({message .from_user .id })\n"
        f"<b>Subject:</b> {subject }\n\n"
        f"<i>Reply to this topic to talk to the client.</i>"
        )

        kb =InlineKeyboardBuilder ()
        kb .row (
        InlineKeyboardButton (text ="Claim",callback_data =f"admin_claim_{ticket_id }"),
        InlineKeyboardButton (text ="Close Ticket",callback_data =f"admin_close_{ticket_id }")
        )
        kb .row (InlineKeyboardButton (text ="Rename",callback_data =f"admin_rename_{ticket_id }"))

        try :
            from aiogram .types import FSInputFile 
            photo_file =FSInputFile ("assets/support.png")
            await bot .send_photo (
            chat_id =ADMIN_GROUP_ID ,
            message_thread_id =topic_id ,
            photo =photo_file ,
            caption =admin_text ,
            reply_markup =kb .as_markup ()
            )
        except Exception as e :
            await bot .send_message (
            chat_id =ADMIN_GROUP_ID ,
            message_thread_id =topic_id ,
            text =admin_text ,
            reply_markup =kb .as_markup ()
            )

        await message .answer (f"✅ Your ticket has been created! Ticket ID: <b>{ticket_id }</b>\nAn admin will review it shortly. You can send further messages here.")
    except Exception as e :
        await message .answer ("❌ Error creating ticket. Please contact an admin directly.")
        print (f"Error creating topic: {e }")

    await state .clear ()

from aiogram .filters import StateFilter 

@router .message (F .chat .type =="private",StateFilter (None ))
async def user_to_topic (message :Message ,bot :Bot ):
    if message .text and message .text .startswith ("/"):
        return 

    ticket =db .get_ticket_by_user (message .from_user .id )
    order =db .get_order_by_user (message .from_user .id )

    if not ticket and not order :
        return 

    active_item =ticket if ticket else order 
    topic_id =active_item ['topic_id']
    item_id =active_item .get ('ticket_id')or active_item .get ('order_num')

    try :

        await bot .copy_message (
        chat_id =ADMIN_GROUP_ID ,
        message_thread_id =topic_id ,
        from_chat_id =message .chat .id ,
        message_id =message .message_id 
        )

        caption_or_text =message .text or message .caption or "[Media]"
        db .save_ticket_message (item_id ,message .from_user .id ,message .from_user .full_name ,caption_or_text ,message .message_id )
    except Exception as e :
        print (f"Error forwarding to topic: {e }")

@router .message (F .chat .id ==int (ADMIN_GROUP_ID ))
async def topic_to_user (message :Message ,bot :Bot ):
    if not message .message_thread_id :
        return 

    if message .text and message .text .startswith ("/"):
        return 

    ticket =db .get_ticket_by_topic (message .message_thread_id )
    if not ticket :

        order =db .get_order_by_topic (message .message_thread_id )
        if order :
            await bot .copy_message (
            chat_id =order ['user_id'],
            from_chat_id =message .chat .id ,
            message_id =message .message_id 
            )
        return 

    try :
        await bot .copy_message (
        chat_id =ticket ['user_id'],
        from_chat_id =ADMIN_GROUP_ID ,
        message_id =message .message_id 
        )
        caption_or_text =message .text or message .caption or "[Media]"
        db .save_ticket_message (ticket ['ticket_id'],message .from_user .id ,message .from_user .full_name ,caption_or_text ,message .message_id )
    except Exception as e :
        print (f"Error forwarding to user: {e }")
