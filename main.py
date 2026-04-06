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

# --- SERVICE REGISTRY (Point 7 Knowledge) ---
SERVICES = {
    "designer": [
        {"id": "ds_logo", "name": "Logo Design", "price": "20"},
        {"id": "ds_id", "name": "Full Visual Identity", "price": "50"},
        {"id": "ds_motion", "name": "Motion Graphics", "price": "45"}
    ],
    "developer": [
        {"id": "dv_web", "name": "Web Development", "price": "30"},
        {"id": "dv_bot", "name": "Bot Development", "price": "40"}
    ]
}

# --- INITIALIZATION ---
# NOTE: User should install dependencies: pip install aiogram google-generativeai supabase
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

def get_node_footer():
    return f"\n\n▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰\n🛰 Node: Telegram-B3 | {datetime.now().strftime('%H:%M:%S')}"

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
    builder.row(types.InlineKeyboardButton(text="⛏ Minecraft", callback_query_data="wiz_minecraft"))
    builder.row(types.InlineKeyboardButton(text="🎬 Video Editing", callback_query_data="wiz_editor"))
    builder.row(types.InlineKeyboardButton(text="⬅️ Back", callback_query_data="back_home"))
    return builder.as_markup()

# --- GEMINI BRAIN (Point 7) ---
async def ask_gemini(prompt_text):
    system_instruction = """
    أنت نظام الذكاء الاصطناعي المركزي لوكالة Highcore Agency.
    القواعد:
    1. رد باحترافية وتقنية عالية (Terminal Aesthetic).
    2. لا تقم بتأليف حالة الطلبات. إذا سأل المستخدم عن طلب تبدأ بـ HC-، أخبره أن يستخدم أمر الاستعلام أو تكت الدعم.
    3. خدماتنا: البرمجة (بوتات، مواقع)، التصميم (هوية، موشن)، ماين كرافت، والمونتاج.
    4. فريق العمل: عمر (باك-إيند)، سعد (موشن جرافيك).
    """
    try:
        response = await ai_model.generate_content_async(f"{system_instruction}\n\nالمستخدم: {prompt_text}")
        return response.text
    except:
        return "⚠️ Error in neural link. Connectivity unstable."

# --- HANDLERS ---

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    header = get_terminal_header("Operational Hub", "Link Established")
    body = "Welcome to the Highcore Agency Node.\nSelect a protocol below to begin interaction."
    await message.answer(header + body + get_node_footer(), reply_markup=main_kb())

@dp.callback_query(F.data == "back_home")
async def back_home(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    header = get_terminal_header("Operational Hub", "Control Restored")
    await callback.message.edit_text(header + "System idle. Waiting for input." + get_node_footer(), reply_markup=main_kb())

# TICKETS
@dp.callback_query(F.data == "ticket_start")
async def ticket_start(callback: types.CallbackQuery):
    header = get_terminal_header("Ticket Protocol", "Subject Selection")
    await callback.message.edit_text(header + "Please select the department for your inquiry:" + get_node_footer(), reply_markup=ticket_categories_kb())

@dp.callback_query(F.data.startswith("cat_"))
async def ticket_open(callback: types.CallbackQuery):
    cat_type = callback.data.split("_")[1]
    user = callback.from_user
    ticket_id = f"{datetime.now().strftime('%y%m%d%H%M')}"
    topic_name = f"Ticket-{ticket_id} | {user.first_name}"
    
    try:
        topic = await bot.create_forum_topic(chat_id=GROUP_ID, name=topic_name)
        welcome_text = (
            f"══ 『 🎫 **NEW TICKET LOGGED** 』 ══\n\n"
            f"**Subject:** {cat_type.upper()}\n"
            f"**User:** {user.full_name}\n"
            f"**ID:** `{user.id}`\n\n"
            f"📜 **PROTOCOL:**\n"
            f"▸ Please provide full situational context.\n"
            f"▸ Attach any visual telemetry (screenshots).\n"
            f"▸ An operative will be assigned shortly."
        )
        await bot.send_message(GROUP_ID, welcome_text, message_thread_id=topic.message_thread_id)
        
        invite_link = f"https://t.me/c/{str(GROUP_ID)[4:]}/{topic.message_thread_id}"
        await callback.message.answer(f"✅ **PROTOCOL INITIATED**\n🔗 [ACCESS TICKET CHANNEL]({invite_link})", disable_web_page_preview=True)
        
        supabase.table("dc_tickets").insert({"ticket_id": ticket_id, "user_id": str(user.id), "channel_id": str(topic.message_thread_id), "type": cat_type, "status": "open"}).execute()
        
    except Exception as e:
        await callback.message.answer("❌ FAILED: Terminal restricted in this sector (Topic creation error).")

# ORDERS
@dp.callback_query(F.data == "order_start")
async def order_start(callback: types.CallbackQuery, state: FSMContext):
    header = get_terminal_header("Dequisition Engine", "Sector Allocation")
    await callback.message.edit_text(header + "Choose your primary project sector:" + get_node_footer(), reply_markup=order_categories_kb())
    await state.set_state(OrderStates.selecting_category)

@dp.callback_query(OrderStates.selecting_category)
async def order_cat_selected(callback: types.CallbackQuery, state: FSMContext):
    sector = callback.data.split("_")[1]
    await state.update_data(category=sector)
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="Standard Package", callback_query_data="srv_std"))
    builder.row(types.InlineKeyboardButton(text="Premium Package", callback_query_data="srv_prm"))
    await callback.message.edit_text(f"Sector: **{sector.upper()}**\nChoose your service tier:", reply_markup=builder.as_markup())
    await state.set_state(OrderStates.selecting_services)

@dp.callback_query(OrderStates.selecting_services)
async def order_srv_selected(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(service=callback.data)
    await callback.message.answer("📝 Please transmit your project specifications (Technical Description):")
    await state.set_state(OrderStates.writing_specs)

@dp.message(OrderStates.writing_specs)
async def order_specs_received(message: types.Message, state: FSMContext):
    await state.update_data(specs=message.text)
    await message.answer("📸 (Optional) Upload visual reference/photo or type 'SKIP':")
    await state.set_state(OrderStates.uploading_media)

@dp.message(OrderStates.uploading_media)
async def order_media_received(message: types.Message, state: FSMContext):
    if message.photo: await state.update_data(media_id=message.photo[-1].file_id)
    data = await state.get_data()
    summary = f"══ 『 🛒 **ORDER REVIEW** 』 ══\n\n**Sector:** {data['category'].upper()}\n**Service:** {data['service']}\n**Specs:** {data['specs'][:100]}...\n\nConfirm transmission?"
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="✅ CONFIRM", callback_query_data="order_confirm"))
    builder.row(types.InlineKeyboardButton(text="❌ CANCEL", callback_query_data="back_home"))
    await message.answer(summary, reply_markup=builder.as_markup())
    await state.set_state(OrderStates.confirming)

@dp.callback_query(F.data == "order_confirm", OrderStates.confirming)
async def order_final(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    order_id = f"HC-{datetime.now().strftime('%m%d%H%M')}"
    supabase.table("dc_orders").insert({"order_num": order_id, "user_id": str(callback.from_user.id), "status": "PENDING", "category": data['category'], "specs": {"details": data['specs'], "service": data['service']}}).execute()
    await callback.message.edit_text(f"🏁 **PROJECT LOGGED**\nDesignation: `{order_id}`\nRegistry updated.")
    await state.clear()

# --- ADMIN COMMANDS (Point 6) ---

@dp.message(Command("kick"))
async def cmd_kick(message: types.Message):
    # Basic check - In production, check user_id against Staff table
    if not message.reply_to_message:
        return await message.answer("⚠️ Please reply to the user you want to eject.")
    
    try:
        await bot.ban_chat_member(message.chat.id, message.reply_to_message.from_user.id)
        await bot.unban_chat_member(message.chat.id, message.reply_to_message.from_user.id) # Kick = Ban then Unban
        await message.answer(f"✅ User {message.reply_to_message.from_user.first_name} has been ejected from sector.")
    except Exception as e:
        await message.answer(f"❌ Authorization failure: {e}")

@dp.message(Command("autoreply"))
async def cmd_autoreply(message: types.Message):
    parts = message.text.split(" ", 2)
    if len(parts) < 3:
        return await message.answer("📝 Usage: `/autoreply [keyword] [response]`")
    
    kw, resp = parts[1].lower(), parts[2]
    supabase.table("dc_auto_responses").upsert({
        "keyword": kw,
        "response_text": resp,
        "platform": "telegram",
        "created_by": str(message.from_user.id)
    }).execute()
    
    await message.answer(f"✅ Neural trigger `{kw}` synchronized.")

# --- AUTO-REPLIES & AI ---
@dp.message()
async def global_handler(message: types.Message):
    if message.message_thread_id: return
    text = message.text.lower().strip()
    res = supabase.table("dc_auto_responses").select("*").eq("keyword", text).execute()
    if res.data:
        await message.reply(res.data[0]['response_text'])
        return
    await bot.send_chat_action(message.chat.id, ChatAction.TYPING)
    reply = await ask_gemini(message.text)
    await message.answer(reply)

# SETUP
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
