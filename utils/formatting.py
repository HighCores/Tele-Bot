from aiogram .utils .keyboard import InlineKeyboardBuilder 
from aiogram .types import InlineKeyboardButton 

ALL_ITEMS ={
"ds_logo":["Logo Design",30.0 ],
"ds_identity":["Full Visual Identity",60.0 ],
"ds_posters":["Posters & Ads",90.0 ],
"ds_social":["Social Media Design",20.0 ],
"ds_discord":["Discord Welcome Pack",20.0 ],
"ds_banners":["Covers & Banners",30.0 ],
"ds_print":["Prints & Brochures",25.0 ],
"ds_motion":["Motion Graphic",90.0 ],
"ds_uiux":["UI/UX Design",120.0 ],
"ds_info":["Infographic",40.0 ],
"ds_emoji":["Emoji / Stickers",30.0 ],
"da_revisions":["Additional Revisions (Quote)",0.0 ],
"da_rush":["Rush Delivery",45.0 ],
"da_source":["Source Files (AI/PSD)",250.0 ],
"da_colors":["Color Variants",35.0 ],
"da_anim":["Add Animation",200.0 ],
"da_2rev":["2 Revisions After Delivery",35.0 ],
"da_logosize":["Additional Logo Size",10.0 ],
"da_copy":["Copywriting",25.0 ],

"dv_web":["Web Developer",50.0 ],
"dv_bots":["Bots Developer",50.0 ],
"dv_full":["Full-Stack Developer",100.0 ],
"dv_front":["Front-End",30.0 ],
"dv_back":["Back-End",40.0 ],
"dv_ai":["AI & Automation",100.0 ],
"dv_db":["Database Administrator",30.0 ],
"dva_revisions":["Additional Revisions (Quote)",0.0 ],
"dva_rush":["Rush Delivery",70.0 ],
"dva_source":["Source Files",150.0 ],
"dva_2rev":["2 Revisions After Delivery",180.0 ],

"ed_reels":["Reels / Shorts Editor",60.0 ],
"ed_long":["Long-form Video Editor",120.0 ],
"ed_anim":["Animation Editor",150.0 ],
"ed_gaming":["Gaming Editor",150.0 ],
"eda_revisions":["Additional Revisions (Quote)",0.0 ],
"eda_rush":["Rush Delivery",45.0 ],
"eda_source":["Source Files (AI/PSD)",250.0 ],
"eda_colors":["Color Variants",35.0 ],
"eda_anim":["Add Animation",200.0 ],
"eda_2rev":["2 Revisions After Delivery",35.0 ],
"eda_size":["Additional Size",10.0 ],
"eda_copy":["Copywriting",25.0 ],

"mc_plugin":["Plugin Developer",50.0 ],
"mc_config":["Configuration Specialist",80.0 ],
"mc_map":["Map Maker / Builder",30.0 ],
"mc_pixel":["Pixel Artist / Texture Creator",130.0 ],
"mc_3d":["3D Modeler (Blockbench)",65.0 ],
"mc_admin":["Technical Admin / SysAdmin",55.0 ],
"mca_revisions":["Additional Revisions (Quote)",0.0 ],
"mca_rush":["Rush Delivery",45.0 ],
"mca_source":["Source Files (AI/PSD)",250.0 ],
"mca_colors":["Color Variants",35.0 ],
"mca_anim":["Add Animation",200.0 ],
"mca_2rev":["2 Revisions After Delivery",35.0 ],
"mca_mod":["Additional Modification",10.0 ],
"mca_copy":["Copywriting",25.0 ],
}

def get_startup_keyboard ():
    b =InlineKeyboardBuilder ()
    b .button (text ="🌐 HighCore",callback_data ="btn_highcore")
    b .button (text ="📖 About Us",callback_data ="btn_about")
    b .button (text ="🤝 Partners",callback_data ="btn_partners")
    b .button (text ="🛠 Support",url ="https://discord.com/channels/YOUR_GUILD/YOUR_CHANNEL")
    b .adjust (2 ,2 )
    return b .as_markup ()

def get_tickets_keyboard ():
    b =InlineKeyboardBuilder ()
    b .button (text ="🛠 Support",callback_data ="ticket_init_support")
    b .button (text ="📝 Complaint",callback_data ="ticket_init_complaint")
    b .adjust (2 )
    return b .as_markup ()

def get_orders_keyboard ():
    b =InlineKeyboardBuilder ()
    b .button (text ="🎨 Designer",callback_data ="order_cat_designer")
    b .button (text ="💻 Developer",callback_data ="order_cat_developer")
    b .button (text ="🎬 Editor",callback_data ="order_cat_editor")
    b .button (text ="🧱 Minecraft",callback_data ="order_cat_minecraft")
    b .adjust (2 ,2 )
    return b .as_markup ()

def get_services_keyboard (category :str ,selected :set =None ):
    if selected is None :selected =set ()
    b =InlineKeyboardBuilder ()

    prefix =""
    if category =="designer":prefix ="ds_"
    elif category =="developer":prefix ="dv_"
    elif category =="editor":prefix ="ed_"
    elif category =="minecraft":prefix ="mc_"

    count =0 
    for k ,v in ALL_ITEMS .items ():
        if k .startswith (prefix )and "a_"not in k :
            mark ="🟢 "if k in selected else "🔘 "
            b .button (text =f"{mark }{v [0 ]} - ${v [1 ]}",callback_data =f"sel_main_{k }")
            count +=1 

    b .button (text ="➡ التالى: الإضافات (Next)",callback_data =f"next_addons_{category }")
    b .adjust (1 )
    return b .as_markup ()

def get_addons_keyboard (category :str ,selected :set =None ):
    if selected is None :selected =set ()
    b =InlineKeyboardBuilder ()

    prefix =""
    if category =="designer":prefix ="da_"
    elif category =="developer":prefix ="dva_"
    elif category =="editor":prefix ="eda_"
    elif category =="minecraft":prefix ="mca_"

    count =0 
    for k ,v in ALL_ITEMS .items ():
        if k .startswith (prefix ):
            mark ="🟢 "if k in selected else "➕ "
            b .button (text =f"{mark }{v [0 ]} - ${v [1 ]}",callback_data =f"sel_addon_{k }")
            count +=1 

    b .button (text ="✅ تأكيد الطلب (Confirm Order)",callback_data =f"confirm_order")
    b .adjust (1 )
    return b .as_markup ()
