from aiogram .utils .keyboard import InlineKeyboardBuilder 
from aiogram .types import InlineKeyboardButton 

def get_main_menu ():
    builder =InlineKeyboardBuilder ()
    builder .row (InlineKeyboardButton (text ="🚀 خدماتنا",callback_data ="view_services"))
    builder .row (InlineKeyboardButton (text ="👥 فريق العمل",callback_data ="view_team"))
    builder .row (InlineKeyboardButton (text ="💬 تواصل معنا",callback_data ="contact_us"))
    return builder .as_markup ()

def get_back_button ():
    builder =InlineKeyboardBuilder ()
    builder .add (InlineKeyboardButton (text ="⬅️ رجوع",callback_data ="back_home"))
    return builder .as_markup ()