from aiogram import Router ,F ,Bot 
from aiogram .types import Message ,CallbackQuery ,InlineKeyboardMarkup ,InlineKeyboardButton 
from aiogram .utils .keyboard import InlineKeyboardBuilder 
from aiogram .fsm .context import FSMContext 
from aiogram .fsm .state import State ,StatesGroup 
from utils .formatting import get_services_keyboard ,get_addons_keyboard ,ALL_ITEMS 
from config import ADMIN_GROUP_ID 
import db 

router =Router ()

class OrderState (StatesGroup ):
    waiting_for_project =State ()
    waiting_for_contact =State ()
    waiting_for_eta =State ()
    waiting_for_voucher =State ()

from aiogram .fsm .storage .base import StorageKey 

@router .callback_query (F .data .startswith ("order_cat_"))
async def order_category_selected (query :CallbackQuery ,state :FSMContext ,bot :Bot ):
    cat =query .data .split ("_")[-1 ]

    if query .message .chat .type !="private":
        try :
            key =StorageKey (bot_id =bot .id ,chat_id =query .from_user .id ,user_id =query .from_user .id )
            await state .storage .update_data (key ,{"category":cat ,"selected_main":set (),"selected_addons":set ()})
            text =(
            f"<b>{cat .upper ()}</b>\n"
            "Select one or more services. Prices are shown below each option."
            )
            await bot .send_message (query .from_user .id ,text =text ,reply_markup =get_services_keyboard (cat ))
            await query .answer ("Please check your DMs! I've sent you a message.",show_alert =True )
        except Exception as e :
            await query .answer ("I can't DM you! Please send me a private message first to start the bot.",show_alert =True )
        return 

    await state .update_data (category =cat ,selected_main =set (),selected_addons =set ())

    text =(
    f"<b>{cat .upper ()}</b>\n"
    "Select one or more services. Prices are shown below each option."
    )
    if query .message .photo :
        await query .message .edit_caption (caption =text ,reply_markup =get_services_keyboard (cat ))
    else :
        await query .message .edit_text (text =text ,reply_markup =get_services_keyboard (cat ))
    await query .answer ()

@router .callback_query (F .data .startswith ("sel_main_"))
async def sel_main (query :CallbackQuery ,state :FSMContext ):
    item =query .data .replace ("sel_main_","")
    data =await state .get_data ()
    selected =data .get ('selected_main',set ())

    if item in selected :
        selected .remove (item )
    else :
        selected .add (item )

    await state .update_data (selected_main =selected )
    await query .message .edit_reply_markup (reply_markup =get_services_keyboard (data ['category'],selected ))
    await query .answer ()

@router .callback_query (F .data .startswith ("next_addons_"))
async def next_addons (query :CallbackQuery ,state :FSMContext ):
    cat =query .data .split ("_")[-1 ]
    data =await state .get_data ()
    selected_main =data .get ('selected_main',set ())

    if not selected_main :
        await query .answer ("Please select at least one service!",show_alert =True )
        return 

    summary =", ".join ([ALL_ITEMS [i ][0 ]for i in selected_main ])
    text =(
    "<b>ADD-ONS</b>\n\n"
    f"<b>Selected services:</b> {summary }\n\n"
    "Now choose any add-ons, or click Confirm Order to skip."
    )
    if query .message .photo :
        await query .message .edit_caption (caption =text ,reply_markup =get_addons_keyboard (cat ,data .get ('selected_addons',set ())))
    else :
        await query .message .edit_text (text =text ,reply_markup =get_addons_keyboard (cat ,data .get ('selected_addons',set ())))

    await query .answer ()

@router .callback_query (F .data .startswith ("sel_addon_"))
async def sel_addon (query :CallbackQuery ,state :FSMContext ):
    item =query .data .replace ("sel_addon_","")
    data =await state .get_data ()
    selected =data .get ('selected_addons',set ())

    if item in selected :
        selected .remove (item )
    else :
        selected .add (item )

    await state .update_data (selected_addons =selected )
    await query .message .edit_reply_markup (reply_markup =get_addons_keyboard (data ['category'],selected ))
    await query .answer ()

@router .callback_query (F .data =="confirm_order")
async def confirm_order (query :CallbackQuery ,state :FSMContext ):
    data =await state .get_data ()
    main =data .get ('selected_main',set ())
    addons =data .get ('selected_addons',set ())

    total =sum ([ALL_ITEMS [i ][1 ]for i in main ])+sum ([ALL_ITEMS [i ][1 ]for i in addons ])
    await state .update_data (total_price =total )

    await query .message .answer (f"<b>Finalizing Order</b> (Total: ${total })\nPlease enter your Project details (e.g. Logo Design):")
    await state .set_state (OrderState .waiting_for_project )
    await query .answer ()

@router .message (OrderState .waiting_for_project )
async def process_project (message :Message ,state :FSMContext ):
    await state .update_data (project =message .text )
    await message .answer ("Please provide your Communication Method (e.g. Discord / Email):")
    await state .set_state (OrderState .waiting_for_contact )

@router .message (OrderState .waiting_for_contact )
async def process_contact (message :Message ,state :FSMContext ):
    await state .update_data (contact =message .text )
    await message .answer ("Please provide the expected ETA (e.g. 3 Days):")
    await state .set_state (OrderState .waiting_for_eta )

@router .message (OrderState .waiting_for_eta )
async def process_eta (message :Message ,state :FSMContext ):
    await state .update_data (eta =message .text )
    await message .answer ("Do you have a Voucher code? (Send the code, or type 'None' to skip):")
    await state .set_state (OrderState .waiting_for_voucher )

@router .message (OrderState .waiting_for_voucher )
async def process_voucher (message :Message ,state :FSMContext ,bot :Bot ):
    voucher_input =message .text .strip ()
    data =await state .get_data ()

    project =data ['project']
    contact =data ['contact']
    eta =data ['eta']
    total =float (data ['total_price'])
    main =data .get ('selected_main',set ())
    addons =data .get ('selected_addons',set ())

    discount =0.0 
    discount_text =""
    if voucher_input .lower ()!="none":
        voucher =db .get_voucher (voucher_input )
        if voucher :
            pct =int (voucher ['percentage'])
            discount =total *(pct /100.0 )
            total =total -discount 
            discount_text =f"\n<b>Voucher Applied:</b> {voucher_input } (-{pct }%)"
            db .mark_voucher_used (voucher ['code'],message .from_user .id )
        else :
            await message .answer ("Invalid or already used voucher. Processing without discount.")

    await state .update_data (total_price =total )
    order_num =db .get_next_id ("ORD")

    topic_name =f"Order - {message .from_user .full_name }"
    try :
        topic =await bot .create_forum_topic (chat_id =ADMIN_GROUP_ID ,name =topic_name )
        topic_id =topic .message_thread_id 

        db .create_order (order_num ,message .from_user .id ,message .from_user .full_name ,project ,contact ,eta ,topic_id )

        import supabase 
        from config import SUPABASE_URL ,SUPABASE_KEY 
        supa =supabase .create_client (SUPABASE_URL ,SUPABASE_KEY )
        supa .table ("tg_orders").update ({"total_price":total }).eq ("order_num",order_num ).execute ()

        items_to_save =[]
        receipt_items =[]
        for i in main :
            items_to_save .append ({"id":i ,"name":ALL_ITEMS [i ][0 ],"price":ALL_ITEMS [i ][1 ]})
            receipt_items .append ({"name":ALL_ITEMS [i ][0 ],"price":ALL_ITEMS [i ][1 ],"is_main":True })
        for i in addons :
            items_to_save .append ({"id":i ,"name":ALL_ITEMS [i ][0 ],"price":ALL_ITEMS [i ][1 ]})
            receipt_items .append ({"name":ALL_ITEMS [i ][0 ],"price":ALL_ITEMS [i ][1 ],"is_main":False })

        db .save_order_items (order_num ,items_to_save )

        main_sum =", ".join ([ALL_ITEMS [i ][0 ]for i in main ])
        addon_sum =", ".join ([ALL_ITEMS [i ][0 ]for i in addons ])if addons else "None"

        admin_text =(
        f"🛒 <b>New Order Created</b>\n"
        f"<b>Order ID:</b> {order_num }\n"
        f"<b>User:</b> {message .from_user .full_name } ({message .from_user .id })\n"
        f"<b>Project:</b> {project }\n"
        f"<b>Contact:</b> {contact }\n"
        f"<b>ETA:</b> {eta }\n\n"
        f"<b>Services:</b> {main_sum }\n"
        f"<b>Add-ons:</b> {addon_sum }{discount_text }\n"
        f"<b>Total Value:</b> ${total :.2f}\n\n"
        f"<i>Reply here to communicate with the client.</i>"
        )

        try :
            from utils .invoice_generator import generate_invoice 
            from aiogram .types import BufferedInputFile 

            invoice_bytes =generate_invoice (order_num ,receipt_items ,total ,message .from_user .full_name ,project ,contact ,discount )
            photo =BufferedInputFile (invoice_bytes ,filename =f"invoice_{order_num }.png")

            kb =InlineKeyboardBuilder ()
            kb .row (
            InlineKeyboardButton (text ="Claim",callback_data =f"admin_claim_{order_num }"),
            InlineKeyboardButton (text ="Close Ticket",callback_data =f"admin_close_{order_num }")
            )
            kb .row (InlineKeyboardButton (text ="Rename",callback_data =f"admin_rename_{order_num }"))

            await bot .send_photo (chat_id =ADMIN_GROUP_ID ,message_thread_id =topic_id ,photo =photo ,caption =admin_text ,reply_markup =kb .as_markup ())

            user_photo =BufferedInputFile (invoice_bytes ,filename =f"invoice_{order_num }.png")
            await message .answer_photo (
            photo =user_photo ,
            caption =f"✅ Your order has been placed! Order ID: <b>{order_num }</b>{discount_text }\nAn admin will review it and contact you here."
            )
        except Exception as e :
            print (f"Failed to generate/send invoice: {e }")

            kb =InlineKeyboardBuilder ()
            kb .row (
            InlineKeyboardButton (text ="Claim",callback_data =f"admin_claim_{order_num }"),
            InlineKeyboardButton (text ="Close Ticket",callback_data =f"admin_close_{order_num }")
            )
            kb .row (InlineKeyboardButton (text ="Rename",callback_data =f"admin_rename_{order_num }"))

            await bot .send_message (chat_id =ADMIN_GROUP_ID ,message_thread_id =topic_id ,text =admin_text ,reply_markup =kb .as_markup ())

            await message .answer (f"✅ Your order has been placed! Order ID: <b>{order_num }</b>{discount_text }\nAn admin will review it and contact you here.")
    except Exception as e :
        await message .answer ("❌ Error creating order. Please contact an admin directly.")
        print (f"Error: {e }")

    await state .clear ()
