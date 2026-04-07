import os

file_path = r"c:\Users\omars\Downloads\telegram_payload_node\main.py"

if not os.path.exists(file_path):
    print(f"File not found: {file_path}")
    exit(1)

with open(file_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    # UI & Headers
    line = line.replace('header = get_agency_header("MENU", "Main Menu")', 'header = get_agency_header("AGENCY", "Main Menu")')
    line = line.replace('Welcome to the Highcore Agency.', 'Welcome to the Highcore Agency Assistant.')
    line = line.replace('### \uD83D\uDE80 Welcome', '### \u2728 Welcome')
    
    # Humanization
    line = line.replace('ORDER REGISTRY REVIEW', 'ORDER SUMMARY REVIEW')
    line = line.replace('Sector identified', 'Department selected')
    line = line.replace('Assigning project tier', 'Selecting service tier')
    line = line.replace('REGISTER PROJECT', 'CONFIRM ORDER')
    line = line.replace('database registration', 'order registration')
    line = line.replace('Neural link lost', 'Connection error')
    line = line.replace('Agency node', 'Agency system')
    line = line.replace('Telegram Node HC-02', 'Highcore Agency Assistant')
    line = line.replace('SESSION SECURED', 'SUPPORT HUB OPENED')
    line = line.replace('ACCESS OPERATIONAL NODE', 'ENTER SUPPORT CHANNEL')
    line = line.replace('\u039B', '') # Remove Lambda
    line = line.replace('\u039E', '') # Remove Xi
    
    # Prompt Improvement (Surgical)
    if 'system_instruction = """' in line:
        line = '    system_instruction = """\n    You are the Senior Assistant for Highcore Agency.\n    Standard: Professional, human-led, and efficient.\n    \n    1. Language: English only.\n    2. Tone: Helpful and direct. NO sci-fi jargon.\n    3. Knowledge: Specializing in Design, Development, and Media.\n    4. Order Status: Use provided order history context to inform the user.\n    """\n'
    
    # Headers/Footers
    if 'return f"### {category.upper()}' in line:
        line = '    return f"**\\u25AC\\u25AC\\u25AC\\u25AC\\u25AC\\u25AC\\u25AC\\u25AC\\u25AC\\u25AC\\u25AC\\u25AC\\u25AC\\u25AC\\u25AC**\\n\\u2728 **{category.upper()}** \\u2022 {service}\\n**\\u2501\\u2501\\u2501\\u2501\\u2501\\u2501\\u2501\\u2501\\u2501\\u2501\\u2501\\u2501\\u2501\\u2501\\u2501**\\n\\n"\n'
    if 'return f"\\n\\n\\u25AC\\u25AC\\u25AC\\u25AC\\u25AC\\u25AC\\u25AC\\u25AC\\u25AC\\u25AC\\u25AC\\u25AC\\u25AC\\u25AC\\u25AC\\n*Highcore Agency 2026' in line:
        line = '    return f"\\n\\n**\\u2501\\u2501\\u2501\\u2501\\u2501\\u2501\\u2501\\u2501\\u2501\\u2501\\u2501\\u2501\\u2501\\u2501\\u2501**\\n\\uD83D\\uDCCC *Highcore Agency \\u2022 Professional Service Hub ({datetime.now().strftime(\'%H:%M:%S\')})*"\n'

    # Keyboards
    line = line.replace('text="\\uD83C\\uDFAB Create Ticket"', 'text="\\uD83D\\uDCE9 Open Support Hub"')
    line = line.replace('text="\\uD83D\\uDED2 Project Request"', 'text="\\uD83D\\uDED2 Start New Project"')
    line = line.replace('text="\\uD83D\\uDC65 Support"', 'text="\\uD83D\\uDCAC Manager"')
    line = line.replace('text="\\uD83D\\uDD17 Hub Dashboard"', 'text="\\uD83C\\uDF10 Agency Dashboard"')

    new_lines.append(line)

with open(file_path, "w", encoding="utf-8") as f:
    f.writelines(new_lines)
print("Telegram bot upgrade successfully applied (Line-by-Line)")
