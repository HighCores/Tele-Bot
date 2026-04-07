import os, asyncio, logging, json
# REDEPLOY_TRIGGER: Highcore Agency Assistant v4.0 [Full Professional Parity]
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums import ChatAction
from aiogram.utils.keyboard import InlineKeyboardBuilder

import google.generativeai as genai
from supabase import create_client, Client

# --- CONFIGURATION ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN") 
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROUP_ID = -1003809843024 

# --- DISCORD LOG CHANNELS ---
LOG_CHANNELS = {
    "JOIN": "1490840457981333635",
    "MSG": "1490840517079208047",
    "TICKET": "1490840580073193523",
    "CMD": "1490840640085295186",
    "MOD": "1490840680766115840",
    "WARN": "1490840718040760473"
}

# --- SERVICES DATA (Discord Parity) ---
SERVICES = {
    "designer": [
        {"id": "ds_logo", "name": "Logo Design", "price": 20},
        {"id": "ds_id", "name": "Full Visual Identity", "price": 50},
        {"id": "ds_social", "name": "Social Media Design", "price": 25},
        {"id": "ds_discord", "name": "Discord Welcome/Packs", "price": 20},
        {"id": "ds_banner", "name": "Covers & Banners", "price": 25},
        {"id": "ds_motion", "name": "Motion Graphics", "price": 45},
        {"id": "ds_uiux", "name": "UI/UX Design", "price": 60}
    ],
    "developer": [
        {"id": "dv_web", "name": "Web Developer", "price": 30},
        {"id": "dv_bot", "name": "Bots Developer", "price": 40}
    ],
    "minecraft": [
        {"id": "mc_plugin", "name": "Plugin Development", "price": 30},
        {"id": "mc_config", "name": "Config Specialist", "price": 30}
    ],
    "editor": [
        {"id": "ed_short", "name": "Reels/Shorts Editor", "price": 20},
        {"id": "ed_long", "name": "Long-form Video", "price": 30}
    ]
}

ADDONS = {
    "designer": [{"id": "ad_rush", "name": "Rush Delivery", "price": 25}, {"id": "ad_source", "name": "Source Files", "price": 30}],
    "developer": [{"id": "ad_automation", "name": "Automation Engine", "price": 35}],
    "minecraft": [{"id": "ad_rush", "name": "Rush Delivery", "price": 50}],
    "editor": [{"id": "ad_rush", "name": "Rush Delivery", "price": 20}]
}

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
    selecting_addons = State()
    writing_specs = State()
    confirming = State()

# --- UTILS: DISCORD RELAY ---
async def send_discord_log(channel_key, title, body, color=0xFFFFFF):
    if not DISCORD_TOKEN: return
    channel_id = LOG_CHANNELS.get(channel_key)
    if not channel_id: return
    
    url = f"https://discord.com/api/v10/channels/{channel_id}/messages"
    headers = {"Authorization": f"Bot {DISCORD_TOKEN}", "Content-Type": "application/json"}
    
    payload = {
        "embeds": [{
            "title": f"✨ {title}",
            "description": body,
            "color": color,
            "footer": {"text": "Highcore Agency \u2022 Agency Assistant"}
        }]
    }
    try:
        async with asyncio.get_event_loop().run_in_executor(None, lambda: __import__('requests').post(url, headers=headers, json=payload)): pass
    except: pass

# --- UTILS: AGENCY UI ---
def get_agency_header(category: str, service: str):
    return f"**▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬**\n✨ **{category.upper()}** • {service}\n**━━━━━━━━━━━━━━━**\n\n"

def get_agency_footer():
    return f"\n\n**━━━━━━━━━━━━━━━**\n📌 *Highcore Agency • Professional Service Hub ({datetime.now().strftime('%H:%M:%S')})*"

# --- KEYBOARDS ---
def main_kb():
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="📩 Open Support Hub", callback_query_data="ticket_start"))
    builder.row(types.InlineKeyboardButton(text="🛒 Start New Project", callback_query_data="order_start"))
    builder.row(types.InlineKeyboardButton(text="📊 Services", callback_query_data="view_services"),
                types.InlineKeyboardButton(text="💬 Manager", url="https://t.me/OmarAmr"))
    builder.row(types.InlineKeyboardButton(text="🌐 Agency Dashboard", url="https://highcore-dashboard.vercel.app"))
    return builder.as_markup()

def ticket_categories_kb():
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="🛒 Purchase Order", callback_query_data="cat_purchase"))
    builder.row(types.InlineKeyboardButton(text="🛠️ Tech Support", callback_query_data="cat_support"))
    builder.row(types.InlineKeyboardButton(text="⚠️ General Inquiry", callback_query_data="cat_complaint"))
    builder.row(types.InlineKeyboardButton(text="⬅️ Back", callback_query_data="back_home"))
    return builder.as_markup()

# --- ASSISTANT LOGIC ---
async def ask_gemini(prompt_text, user_id=None):
    system_instruction = """
    You are the Senior Assistant for Highcore Agency. 
    Standard: Professional, human-led, and efficient.
    
    1. Language: English only.
    2. Tone: Helpful and direct. NO sci-fi jargon (Neural, Node, Prototype, Kernel).
    3. Knowledge: Specializing in Graphic Design, Software Development, and Minecraft Media.
    4. Order Status: If a user asks about their order/project, use provided data to interpret the 'status' and 'category' professionally.
    5. Direct Action: If a user wants to order or has a technical issue, direct them to use the 'Support Hub' or 'Start Project' buttons.
    6. Honesty: Do not invent order data. If no context is provided, ask the user for their order ID or to use the dashboard.
    """
    
    context = ""
    if user_id:
        try:
            res = supabase.table("dc_orders").select("*").eq("user_id", str(user_id)).execute()
            if res.data:
                orders_summary = "\n".join([f"Order #{o['order_num']}: Status {o['status']} (Category: {o['category']})" for o in res.data])
                context = f"\n\n[USER ORDER HISTORY HISTORY]\n{orders_summary}\n"
        except: pass

    try:
        response = await ai_model.generate_content_async(f"{system_instruction}{context}\n\nUser: {prompt_text}")
        return response.text
    except:
        return "\u26A0\uFE0F **Connection error:** Our assistant is temporarily offline. Please open a support ticket for urgent requests."

# --- HANDLERS ---

@dp.chat_member()
async def on_chat_member(event: types.ChatMemberUpdated):
    user = event.from_user
    if event.new_chat_member.status == "member":
        await send_discord_log("JOIN", "Join Event", f"User: {user.full_name} (@{user.username})\nID: `{user.id}`\nStatus: **JOINED**", 0x2ecc71)
    elif event.new_chat_member.status in ["left", "kicked"]:
        await send_discord_log("JOIN", "Left Event", f"User: {user.full_name} (@{user.username})\nID: `{user.id}`\nStatus: **LEFT**", 0xe74c3c)

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    header = get_agency_header("AGENCY", "Main Menu")
    body = "### ✨ Welcome\nWelcome to the Highcore Agency Assistant. We are ready to assist you.\nPlease select an option below to begin."
    await message.answer(header + body + get_agency_footer(), reply_markup=main_kb())
    await send_discord_log("CMD", "Command Log", f"User: {message.from_user.full_name}\nCommand: `/start`", 0x3498db)

@dp.message(Command("stats"))
async def cmd_stats(message: types.Message):
    res_orders = supabase.table("dc_orders").select("*", count="exact").execute()
    res_tickets = supabase.table("dc_tickets").select("*", count="exact").eq("status", "open").execute()
    
    header = get_agency_header("AGENCY", "Real-time Statistics")
    body = f"\uD83D\uDCCA **Live Overview**\n\u2501\u2501\u2501\u2501\nTotal Projects: `{res_orders.count}`\nActive Tickets: `{res_tickets.count}`\n\u2501\u2501\u2501\u2501"
    await message.answer(header + body + get_agency_footer())

@dp.message(Command("kick"))
async def cmd_kick(message: types.Message, command: CommandObject):
    if not message.reply_to_message:
        return await message.reply("\u26A0\uFE0F Reply to a user to kick them.")
    
    user = message.reply_to_message.from_user
    try:
        await bot.ban_chat_member(message.chat.id, user.id)
        await bot.unban_chat_member(message.chat.id, user.id)
        await message.answer(f"\u2705 **User Removed:** {user.full_name} has been removed from the agency group.")
        await send_discord_log("MOD", "Moderation Log", f"**Action:** KICK\n**User:** {user.full_name}\n**Moderator:** {message.from_user.full_name}", 0xe67e22)
    except Exception as e:
        await message.answer(f"\u274C **Error:** {str(e)}")

@dp.message(Command("ban"))
async def cmd_ban(message: types.Message, command: CommandObject):
    if not message.reply_to_message:
        return await message.reply("\u26A0\uFE0F Reply to a user to ban them.")
    
    user = message.reply_to_message.from_user
    try:
        await bot.ban_chat_member(message.chat.id, user.id)
        await message.answer(f"\uD83D\uDD34 **User Banned:** {user.full_name} has been restricted from the agency group.")
        await send_discord_log("MOD", "Moderation Log", f"**Action:** BAN\n**User:** {user.full_name}\n**Moderator:** {message.from_user.full_name}", 0xc0392b)
    except Exception as e:
        await message.answer(f"\u274C **Error:** {str(e)}")

@dp.message(Command("unban"))
async def cmd_unban(message: types.Message, command: CommandObject):
    try:
        user_id = int(command.args) if command.args else None
        if not user_id: return await message.reply("\u26A0\uFE0F Please provide a User ID: `/unban ID`.")
        await bot.unban_chat_member(message.chat.id, user_id)
        await message.answer(f"\u2705 **User Unbanned:** The restriction for ID `{user_id}` has been lifted.")
        await send_discord_log("MOD", "Moderation Log", f"**Action:** UNBAN\n**User ID:** `{user_id}`\n**Moderator:** {message.from_user.full_name}", 0x27ae60)
    except Exception as e:
        await message.answer(f"\u274C **Error:** {str(e)}")

@dp.message(Command("warn"))
async def cmd_warn(message: types.Message, command: CommandObject):
    if not message.reply_to_message:
        return await message.reply("\u26A0\uFE0F Reply to a user to issue a warning.")
    
    user = message.reply_to_message.from_user
    reason = command.args if command.args else "No reason provided."
    
    try:
        supabase.table("dc_warnings").insert({
            "user_id": str(user.id),
            "user_name": user.full_name,
            "warned_by": str(message.from_user.id),
            "warned_by_name": message.from_user.full_name,
            "reason": reason,
            "guild_id": "telegram"
        }).execute()
        
        res = supabase.table("dc_warnings").select("*", count="exact").eq("user_id", str(user.id)).execute()
        warn_count = res.count if res.count else 0
        
        await message.answer(f"\u26A0\uFE0F **Professional Warning Issued**\n**User:** {user.full_name}\n**Count:** {warn_count}\n**Reason:** {reason}")
        await send_discord_log("WARN", "Warning Log (TG)", f"**User:** {user.full_name} (`{user.id}`)\n**Reason:** {reason}\n**Total Warnings:** {warn_count}\n**Mod:** {message.from_user.full_name}", 0xf39c12)
    except Exception as e:
        await message.answer(f"\u274C **Error:** {str(e)}")

@dp.callback_query(F.data == "back_home")
async def back_home(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    header = get_agency_header("AGENCY", "Main Menu")
    await callback.message.edit_text(header + "### \u23F3 Ready\nHow can we help you today?" + get_agency_footer(), reply_markup=main_kb())

# TICKETS
@dp.callback_query(F.data == "ticket_start")
async def ticket_start(callback: types.CallbackQuery):
    header = get_agency_header("SUPPORT", "Open Ticket")
    await callback.message.edit_text(header + "Please choose a professional category for your inquiry:" + get_agency_footer(), reply_markup=ticket_categories_kb())

@dp.callback_query(F.data.startswith("cat_"))
async def ticket_open(callback: types.CallbackQuery):
    cat_type = callback.data.split("_")[1]
    user = callback.from_user
    ticket_id = f"HC-TE-{datetime.now().strftime('%m%d%H%M')}"
    topic_name = f"{ticket_id} | {user.first_name}"
    
    try:
        topic = await bot.create_forum_topic(chat_id=GROUP_ID, name=topic_name)
        welcome_text = (
            f"### \u2728 NEW SUPPORT TICKET OPENED\n"
            f"\u25AC\u25AC\u25AC\u25AC\u25AC\u25AC\u25AC\u25AC\u25AC\u25AC\u25AC\u25AC\n"
            f"**Category:** {cat_type.upper()}\n"
            f"**User:** {user.full_name}\n"
            f"**Ticket ID:** `{ticket_id}`\n\n"
            f"**Important Info:**\n"
            f"\u2022 Please describe your request in detail.\n"
            f"\u2022 You can share relevant files/media.\n"
            f"\u2022 Our staff will respond shortly."
        )
        await bot.send_message(GROUP_ID, welcome_text, message_thread_id=topic.message_thread_id)
        
        invite_link = f"https://t.me/c/{str(GROUP_ID)[4:]}/{topic.message_thread_id}"
        await callback.message.answer(f"\u2705 **SUPPORT HUB OPENED**\n\uD83D\uDCE9 [ENTER SUPPORT CHANNEL]({invite_link})", disable_web_page_preview=True)
        
        supabase.table("dc_tickets").insert({"ticket_id": ticket_id, "user_id": str(user.id), "channel_id": str(topic.message_thread_id), "type": cat_type, "status": "open"}).execute()
        await send_discord_log("TICKET", "Ticket Initialized", f"**ID:** `{ticket_id}`\n**User:** {user.full_name}\n**Type:** {cat_type.upper()}", 0x2ecc71)
        
    except Exception as e:
        await callback.message.answer("\u274C **Error:** Could not initialize the support channel.")

# ORDERS (Full Parity Wizard)
@dp.callback_query(F.data == "order_start")
async def order_start(callback: types.CallbackQuery, state: FSMContext):
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="\uD83C\uDFA8 Digital Designer", callback_query_data="wiz_designer"))
    builder.row(types.InlineKeyboardButton(text="\u2699\uFE0F Software Developer", callback_query_data="wiz_developer"))
    builder.row(types.InlineKeyboardButton(text="\u26CF\uFE0F Minecraft Specialist", callback_query_data="wiz_minecraft"))
    builder.row(types.InlineKeyboardButton(text="\uD83C\uDFAC Video Editor", callback_query_data="wiz_editor"))
    builder.row(types.InlineKeyboardButton(text="\u2B05\uFE0F Back", callback_query_data="back_home"))
    
    header = get_agency_header("ORDERS", "Service Selection")
    await callback.message.edit_text(header + "Select the primary department for your project:" + get_agency_footer(), reply_markup=builder.as_markup())
    await state.set_state(OrderStates.selecting_category)

@dp.callback_query(F.data.startswith("wiz_"), OrderStates.selecting_category)
async def order_cat_selected(callback: types.CallbackQuery, state: FSMContext):
    cat = callback.data.split("_")[1]
    await state.update_data(category=cat, services=[])
    await show_service_menu(callback, cat, [])
    await state.set_state(OrderStates.selecting_services)

async def show_service_menu(callback, cat, selected_ids):
    builder = InlineKeyboardBuilder()
    for srv in SERVICES[cat]:
        check = "\u2705 " if srv['id'] in selected_ids else ""
        builder.row(types.InlineKeyboardButton(text=f"{check}{srv['name']} (${srv['price']})", callback_query_data=f"toggle_{srv['id']}"))
    
    builder.row(types.InlineKeyboardButton(text="\u27A1\uFE0F Next Step (Addons)", callback_query_data="step_addons"))
    builder.row(types.InlineKeyboardButton(text="\u2B05\uFE0F Re-select Category", callback_query_data="order_start"))
    
    header = get_agency_header("ORDERS", f"{cat.upper()} DEPARTMENT")
    await callback.message.edit_text(header + "### \uD83D\uDCE1 Service Allocation\nSelect one or more core services for your project:" + get_agency_footer(), reply_markup=builder.as_markup())

@dp.callback_query(F.data.startswith("toggle_"), OrderStates.selecting_services)
async def toggle_service(callback: types.CallbackQuery, state: FSMContext):
    srv_id = callback.data.split("_")[1]
    data = await state.get_data()
    selected = data.get('services', [])
    
    if srv_id in selected: selected.remove(srv_id)
    else: selected.append(srv_id)
    
    await state.update_data(services=selected)
    await show_service_menu(callback, data['category'], selected)

@dp.callback_query(F.data == "step_addons", OrderStates.selecting_services)
async def step_addons(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if not data.get('services'):
        return await callback.answer("\u26A0\uFE0F Please select at least one service.", show_alert=True)
    
    await state.update_data(addons=[])
    await show_addon_menu(callback, data['category'], [])
    await state.set_state(OrderStates.selecting_addons)

async def show_addon_menu(callback, cat, selected_ids):
    builder = InlineKeyboardBuilder()
    for add in ADDONS.get(cat, []):
        check = "\u2705 " if add['id'] in selected_ids else ""
        builder.row(types.InlineKeyboardButton(text=f"{check}{add['name']} (+${add['price']})", callback_query_data=f"atogl_{add['id']}"))
    
    builder.row(types.InlineKeyboardButton(text="\u27A1\uFE0F Submit Details", callback_query_data="step_specs"))
    
    header = get_agency_header("ORDERS", "Service Add-ons")
    await callback.message.edit_text(header + "### \uD83D\uDD04 Advanced Features\nEnhance your project with these specialized modules:" + get_agency_footer(), reply_markup=builder.as_markup())

@dp.callback_query(F.data.startswith("atogl_"), OrderStates.selecting_addons)
async def toggle_addon(callback: types.CallbackQuery, state: FSMContext):
    add_id = callback.data.split("_")[1]
    data = await state.get_data()
    selected = data.get('addons', [])
    
    if add_id in selected: selected.remove(add_id)
    else: selected.append(add_id)
    
    await state.update_data(addons=selected)
    await show_addon_menu(callback, data['category'], selected)

@dp.callback_query(F.data == "step_specs", OrderStates.selecting_addons)
async def step_specs(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("\uD83D\uDCDD **Project Details Required:**\nPlease provide detailed project specifications and any preferred deadline.")
    await state.set_state(OrderStates.writing_specs)

@dp.message(OrderStates.writing_specs)
async def order_specs_received(message: types.Message, state: FSMContext):
    await state.update_data(specs=message.text)
    data = await state.get_data()
    
    total = 0
    srv_list = ""
    for s in SERVICES[data['category']]:
        if s['id'] in data['services']:
            total += s['price']
            srv_list += f"- {s['name']}\n"
    for a in ADDONS.get(data['category'], []):
        if a['id'] in data['addons']:
            total += a['price']
            srv_list += f"- {a['name']} (Addon)\n"

    summary = (
        f"### \u2728 ORDER SUMMARY REVIEW\n"
        f"\u25AC\u25AC\u25AC\u25AC\u25AC\u25AC\u25AC\u25AC\u25AC\u25AC\u25AC\u25AC\n"
        f"**Department:** {data['category'].upper()}\n"
        f"**Selected Services:**\n{srv_list}\n"
        f"**ESTIMATED TOTAL:** `${total}`\n"
        f"\u25AC\u25AC\u25AC\u25AC\u25AC\u25AC\u25AC\u25AC\u25AC\u25AC\u25AC\u25AC\n"
        f"Proceed with official registration?"
    )
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="\u2705 CONFIRM & REGISTER", callback_query_data="order_confirm"))
    builder.row(types.InlineKeyboardButton(text="\u274C CANCEL", callback_query_data="back_home"))
    await message.answer(summary, reply_markup=builder.as_markup())
    await state.set_state(OrderStates.confirming)

@dp.callback_query(F.data == "order_confirm", OrderStates.confirming)
async def order_final(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    order_id = f"HC-TE-OR-{datetime.now().strftime('%m%d%H%M')}"
    
    specs_json = {
        "details": data['specs'],
        "services": data['services'],
        "addons": data['addons']
    }
    
    supabase.table("dc_orders").insert({
        "order_num": order_id, 
        "user_id": str(callback.from_user.id), 
        "status": "PENDING", 
        "category": data['category'], 
        "specs": specs_json
    }).execute()
    
    await callback.message.edit_text(f"\uD83C\uDFC1 **OFFICIAL ORDER SUBMITTED**\nOrder ID: `{order_id}`\nYou will be notified of updates.")
    await send_discord_log("TICKET", "New Order (TG)", f"**ID:** `{order_id}`\n**User:** {callback.from_user.full_name}\n**Department:** {data['category'].upper()}", 0xf1c40f)
    await state.clear()

# --- RESPONSE HANDLERS ---
@dp.message()
async def global_handler(message: types.Message):
    if not message.text: return
    if message.message_thread_id: return
    
    text = message.text.lower().strip()
    
    # Word Filter
    try:
        res_wf = supabase.table("dc_word_filter").select("*").execute()
        forbidden = [r['word'].lower() for r in res_wf.data] if res_wf.data else []
        if any(w in text for w in forbidden):
            await message.delete()
            await send_discord_log("WARN", "Forbidden Content (TG)", f"**User:** {message.from_user.full_name}\n**Content:** {message.text}", 0xe74c3c)
            return
    except: pass

    # Auto Reply
    try:
        res = supabase.table("dc_auto_responses").select("*").eq("keyword", text).execute()
        if res.data:
            await message.reply(res.data[0]['response_text'])
            return
    except: pass
        
    # AI Logic
    await bot.send_chat_action(message.chat.id, ChatAction.TYPING)
    reply = await ask_gemini(message.text, user_id=message.from_user.id)
    await message.answer(reply)
    await send_discord_log("MSG", "Message Log (TG)", f"**User:** {message.from_user.full_name}\n**Content:** {message.text[:200]}", 0x3498db)

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
