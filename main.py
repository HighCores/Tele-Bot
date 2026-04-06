import os, asyncio, logging, json
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums import ChatAction
from aiogram.utils.keyboard import InlineKeyboardBuilder

import google.generativeai as genai
from supabase import create_client, Client

# --- CONFIGURATION (Sync with Discord) ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROUP_ID = -1003809843024 
MAIN_PANEL_TOPIC = 6

# --- INITIALIZATION ---
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
genai.configure(api_key=GEMINI_API_KEY)
ai_model = genai.GenerativeModel('gemini-1.5-flash') 

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
logging.basicConfig(level=logging.INFO)

# --- FSM STATES ---
class OrderStates(StatesGroup):
    selecting_category = State()
    selecting_services = State()
    writing_specs = State()
    uploading_media = State()
    confirming = State()

# --- UTILS: TERMINAL UI ---
def get_terminal_header(title: str, subtitle: str):
    return f"═══ 『 𝐇𝐈𝐆𝐇𝐂𝐎𝐑𝐄 𝐀𝐆𝐄𝐍𝐂𝐘 』 ═══\n\n« {title.upper()} »\n// {subtitle}\n"

def get_agency_footer():
    return f"\n\n▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰\n🛰 Highcore Agency | {datetime.now().strftime('%H:%M:%S')}"

# --- KEYBOARDS ---
def main_kb():
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="🎫 Open Ticket", callback_query_data="ticket_start"))
    builder.row(types.InlineKeyboardButton(text="🛒 New Order", callback_query_data="order_start"))
    builder.row(types.InlineKeyboardButton(text="👥 Our Team", callback_query_data="view_team"),
                types.InlineKeyboardButton(text="🚀 Services", callback_query_data="view_services"))
    builder.row(types.InlineKeyboardButton(text="📊 Dashboard", url="https://highcore-dashboard.vercel.app"))
    return builder.as_markup()

def ticket_categories_kb():
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="🛠 Technical Support", callback_query_data="cat_tech_support"))
    builder.row(types.InlineKeyboardButton(text="🎨 Design Inquiry", callback_query_data="cat_design"))
    builder.row(types.InlineKeyboardButton(text="💻 Development", callback_query_data="cat_dev"))
    builder.row(types.InlineKeyboardButton(text="⚙️ Management", callback_query_data="cat_management"))
    builder.row(types.InlineKeyboardButton(text="⬅️ Back", callback_query_data="back_home"))
    return builder.as_markup()

def order_categories_kb():
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="🎨 Graphic Design", callback_query_data="wiz_designer"))
    builder.row(types.InlineKeyboardButton(text="⚙️ Software Dev", callback_query_data="wiz_developer"))
    builder.row(types.InlineKeyboardButton(text="🎬 Video Editing", callback_query_data="wiz_editor"))
    builder.row(types.InlineKeyboardButton(text="⬅️ Back", callback_query_data="back_home"))
    return builder.as_markup()

# --- GEMINI BRAIN (Highcore Agency AI Persona) ---
async def ask_gemini(prompt_text):
    system_instruction = """
    أنت نظام الذكاء الاصطناعي المركزي لوكالة Highcore Agency.
    القواعد:
    1. رد باحترافية وتحدث بلسان وكالة Highcore.
    2. لا تقم بتأليف حالة الطلبات. إذا سأل المستخدم عن طلب تبدأ بـ HC-، أخبره أن يستخدم أمر الاستعلام أو تكت الدعم.
    3. خدماتنا: البرمجة (بوتات، مواقع)، التصميم (هوية، موشن)، ماين كرافت، والمونتاج.
    4. فريق العمل: عمر (باك-إيند)، سعد (موشن جرافيك).
    5. استخدم لغة مهذبة وراقية (Clean English/Arabic).
    """
    try:
        response = await ai_model.generate_content_async(f"{system_instruction}\n\nالمستخدم: {prompt_text}")
        return response.text
    except:
        return "⚠️ Sync error. Connection instability detected in the Agency node."

# --- HANDLERS ---

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    header = get_terminal_header("Agency Management", "Connection Secure")
    body = "Welcome to the Highcore Agency Digital Branch.\nSelect a service below to begin your professional consultation."
    await message.answer(header + body + get_agency_footer(), reply_markup=main_kb())

@dp.callback_query(F.data == "back_home")
async def back_home(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    header = get_terminal_header("Agency Management", "Control Restored")
    await callback.message.edit_text(header + "Agency systems idle. Awaiting selection." + get_agency_footer(), reply_markup=main_kb())

# TICKETS
@dp.callback_query(F.data == "ticket_start")
async def ticket_start(callback: types.CallbackQuery):
    header = get_terminal_header("Support Service", "Subject Selection")
    await callback.message.edit_text(header + "Please select the department for your inquiry:" + get_agency_footer(), reply_markup=ticket_categories_kb())

@dp.callback_query(F.data.startswith("cat_"))
async def ticket_open(callback: types.CallbackQuery):
    cat_type = callback.data.split("_")[1]
    user = callback.from_user
    ticket_id = f"{datetime.now().strftime('%y%m%d%H%M')}"
    topic_name = f"Ticket-{ticket_id} | {user.first_name}"
    
    try:
        topic = await bot.create_forum_topic(chat_id=GROUP_ID, name=topic_name)
        welcome_text = (
            f"══ 『 🎫 **NEW PROJECT TICKET LOGGED** 』 ══\n\n"
            f"**Department:** {cat_type.upper()}\n"
            f"**Client:** {user.full_name}\n"
            f"**ID:** `{user.id}`\n\n"
            f"📜 **INSTRUCTIONS:**\n"
            f"▸ Please describe your requirements in detail.\n"
            f"▸ Attach any reference media.\n"
            f"▸ A Highcore operative will respond shortly."
        )
        await bot.send_message(GROUP_ID, welcome_text, message_thread_id=topic.message_thread_id)
        
        invite_link = f"https://t.me/c/{str(GROUP_ID)[4:]}/{topic.message_thread_id}"
        await callback.message.answer(f"✅ **SUPPORT SESSION INITIALIZED**\n🔗 [ACCESS PROJECT TICKET]({invite_link})", disable_web_page_preview=True)
        
        supabase.table("dc_tickets").insert({"ticket_id": ticket_id, "user_id": str(user.id), "channel_id": str(topic.message_thread_id), "type": cat_type, "status": "open"}).execute()
        
    except Exception as e:
        await callback.message.answer("❌ FAILED: Protocol restriction (Topic creation error). Ensure the bot has Forum Admin permissions.")

# ORDERS
@dp.callback_query(F.data == "order_start")
async def order_start(callback: types.CallbackQuery, state: FSMContext):
    header = get_terminal_header("Order System", "Category Selection")
    await callback.message.edit_text(header + "Select the primary sector for your project:" + get_agency_footer(), reply_markup=order_categories_kb())
    await state.set_state(OrderStates.selecting_category)

@dp.callback_query(OrderStates.selecting_category)
async def order_cat_selected(callback: types.CallbackQuery, state: FSMContext):
    sector = callback.data.split("_")[1]
    await state.update_data(category=sector)
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="Standard Service", callback_query_data="srv_std"))
    builder.row(types.InlineKeyboardButton(text="Premium Agency Solution", callback_query_data="srv_prm"))
    await callback.message.edit_text(f"Sector Identified: **{sector.upper()}**\nSelect your project tier:", reply_markup=builder.as_markup())
    await state.set_state(OrderStates.selecting_services)

@dp.callback_query(OrderStates.selecting_services)
async def order_srv_selected(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(service=callback.data)
    await callback.message.answer("📝 Please transmit your project specifications (Detailed Description):")
    await state.set_state(OrderStates.writing_specs)

@dp.message(OrderStates.writing_specs)
async def order_specs_received(message: types.Message, state: FSMContext):
    await state.update_data(specs=message.text)
    await message.answer("📸 (Optional) Upload visual reference/media or type 'DONE':")
    await state.set_state(OrderStates.uploading_media)

@dp.message(OrderStates.uploading_media)
async def order_media_received(message: types.Message, state: FSMContext):
    if message.photo: await state.update_data(media_id=message.photo[-1].file_id)
    data = await state.get_data()
    summary = f"══ 『 🛒 **ORDER REGISTRY REVIEW** 』 ══\n\n**Sector:** {data['category'].upper()}\n**Tier:** {data['service']}\n**Brief:** {data['specs'][:100]}...\n\nProceed with registration?"
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="✅ REGISTER PROJECT", callback_query_data="order_confirm"))
    builder.row(types.InlineKeyboardButton(text="❌ CANCEL", callback_query_data="back_home"))
    await message.answer(summary, reply_markup=builder.as_markup())
    await state.set_state(OrderStates.confirming)

@dp.callback_query(F.data == "order_confirm", OrderStates.confirming)
async def order_final(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    order_id = f"HC-{datetime.now().strftime('%m%d%H%M')}"
    supabase.table("dc_orders").insert({
        "order_num": order_id, 
        "user_id": str(callback.from_user.id), 
        "status": "PENDING", 
        "category": data['category'], 
        "specs": {"details": data['specs'], "service": data['service']}
    }).execute()
    await callback.message.edit_text(f"🏁 **PROJECT REGISTERED IN AGENCY DATABASE**\nDesignation: `{order_id}`\nRegistry updated.")
    await state.clear()

# --- ADMIN COMMANDS ---

@dp.message(Command("kick"))
async def cmd_kick(message: types.Message):
    if not message.reply_to_message:
        return await message.answer("⚠️ Action Required: Reply to the target user to initiate ejection.")
    try:
        await bot.ban_chat_member(message.chat.id, message.reply_to_message.from_user.id)
        await bot.unban_chat_member(message.chat.id, message.reply_to_message.from_user.id)
        await message.answer(f"✅ Security Protocol: User {message.reply_to_message.from_user.first_name} ejected from sector.")
    except Exception as e:
        await message.answer(f"❌ Access Denied: {e}")

@dp.message(Command("autoreply"))
async def cmd_autoreply(message: types.Message):
    parts = message.text.split(" ", 2)
    if len(parts) < 3:
        return await message.answer("📝 Registry Format: `/autoreply [keyword] [response]`")
    kw, resp = parts[1].lower(), parts[2]
    supabase.table("dc_auto_responses").upsert({
        "keyword": kw,
        "response_text": resp,
        "platform": "telegram",
        "created_by": str(message.from_user.id)
    }).execute()
    await message.answer(f"✅ Smart response registry `{kw}` synchronized.")

# --- RESPONSE HANDLERS ---
@dp.message()
async def global_handler(message: types.Message):
    if message.message_thread_id: return
    text = message.text.lower().strip() if message.text else ""
    res = supabase.table("dc_auto_responses").select("*").eq("keyword", text).execute()
    if res.data:
        await message.reply(res.data[0]['response_text'])
        return
    if message.text:
        await bot.send_chat_action(message.chat.id, ChatAction.TYPING)
        reply = await ask_gemini(message.text)
        await message.answer(reply)

# SETUP
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
