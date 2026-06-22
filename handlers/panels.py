from aiogram import Router ,F 
from aiogram .filters import Command 
from aiogram .types import Message ,CallbackQuery ,InputMediaPhoto ,FSInputFile 
from utils .formatting import get_startup_keyboard ,get_tickets_keyboard ,get_orders_keyboard 

router =Router ()

IMG_DIR =r"C:\Users\omars\OneDrive\Desktop\Worker\HighCores\HighCore Studio\HighCores Studio Identity\HIGHCORE FINAL FINAL"

@router .message (Command ("startup","start"))
async def cmd_startup (message :Message ):
    text ="<b>HighCore Agency</b>\n\nSelect a module below to proceed."
    photo1 =FSInputFile (fr"{IMG_DIR }\Highcore Agency - 1.jpg")
    photo2 =FSInputFile (fr"{IMG_DIR }\Wekcome to Highcore Agency_.jpg")
    await message .answer_photo (photo1 )
    await message .answer_photo (photo2 ,caption =text ,reply_markup =get_startup_keyboard ())

    import db 
    db .add_user_for_broadcast (message .from_user .id )

@router .message (Command ("line"))
async def cmd_line (message :Message ):
    photo =FSInputFile ("Server Line Black Padded.jpg")
    await message .answer_photo (photo )

@router .message (Command ("tickets","ticket"))
async def cmd_tickets (message :Message ):
    text =(
    "📜 <b>RULES & GUIDELINES</b>\n\n"
    "<b>Mutual Respect</b> — Please respect all staff members.\n"
    "<b>One Ticket</b> — Open only one ticket per issue.\n"
    "<b>Clarity</b> — Please fully describe your issue.\n"
    "<b>Content</b> — Spam and external links are strictly prohibited.\n"
    "<b>Mentions</b> — Pinging staff inside the ticket is forbidden."
    )
    photo =FSInputFile (fr"{IMG_DIR }\Tickets.jpg")
    await message .answer_photo (photo ,caption =text ,reply_markup =get_tickets_keyboard ())

@router .message (Command ("order","orders"))
async def cmd_order (message :Message ):
    text =(
    "◗ Ready to bring your idea to life ?\n\n"
    "Choose a category below to see our services.\n"
    "After that, you can fill in your project details."
    )
    photo =FSInputFile (fr"{IMG_DIR }\Orders_.jpg")
    await message .answer_photo (photo ,caption =text ,reply_markup =get_orders_keyboard ())

@router .message (Command ("terms"))
async def cmd_terms (message :Message ):

    urls =[
    'https://files.catbox.moe/fraywe.jpg',
    'https://files.catbox.moe/90bi1d.jpg',
    'https://files.catbox.moe/0o0cxs.jpg',
    'https://files.catbox.moe/4s0pag.jpg',
    'https://files.catbox.moe/k9l9i4.jpg',
    'https://files.catbox.moe/vc4hb4.jpg'
    ]

    for url in urls :
        await message .answer_photo (photo =url )

@router .callback_query (F .data =="btn_highcore")
async def btn_highcore_handler (query :CallbackQuery ):
    text =(
    "<b>Server Navigation Guide</b>\n\n"
    "Start Up → /startup\n"
    "Our Terms → /terms\n"
    "Support → /tickets\n"
    )
    photo =FSInputFile (fr"{IMG_DIR }\Server Banner.jpg")
    await query .message .answer_photo (photo =photo ,caption =text )
    await query .answer ()

@router .callback_query (F .data =="btn_about")
async def btn_about_handler (query :CallbackQuery ):
    text ="<b>Agency Profile</b>\nSelect a specialist module below to examine our creative service protocols and price scales."
    photo =FSInputFile (fr"{IMG_DIR }\Highcore Agency - 1.jpg")
    await query .message .answer_photo (photo =photo ,caption =text ,reply_markup =get_orders_keyboard ())
    await query .answer ()

@router .callback_query (F .data =="btn_partners")
async def btn_partners_handler (query :CallbackQuery ):
    text ="🤝 <b>Strategic Alliances</b>\nHighCore Agency is connected with industry leaders to provide elite-scale solutions."
    photo =FSInputFile (fr"{IMG_DIR }\Partners.jpg")
    await query .message .answer_photo (photo =photo ,caption =text )
    await query .answer ()
