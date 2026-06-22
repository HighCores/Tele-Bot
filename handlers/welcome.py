import os 
from aiogram import Router ,F 
from aiogram .types import Message ,FSInputFile 
from aiogram .filters import Command 
from config import PUBLIC_GROUP_ID ,WELCOME_TOPIC_ID 
from utils .welcome_generator import generate_welcome_card 

router =Router ()

@router .message (F .new_chat_members )
async def welcome_new_member (message :Message ):
    if str (message .chat .id )==str (PUBLIC_GROUP_ID ):
        for member in message .new_chat_members :
            if not member .is_bot :
                welcome_text =(
                f"Welcome to HighCore, {member .get_mention (as_html =True )}!\n\n"
                f"Check out our services by messaging our bot directly."
                )

                avatar_bytes =None 
                try :
                    user_photos =await message .bot .get_user_profile_photos (member .id ,limit =1 )
                    if user_photos .total_count >0 :
                        photo_file_id =user_photos .photos [0 ][-1 ].file_id 
                        file =await message .bot .get_file (photo_file_id )

                        import io 
                        avatar_io =io .BytesIO ()
                        await message .bot .download_file (file .file_path ,destination =avatar_io )
                        avatar_bytes =avatar_io .getvalue ()
                except Exception as e :
                    print (f"Failed to fetch avatar: {e }")

                try :
                    img_path =generate_welcome_card (member .full_name ,avatar_bytes )
                    photo =FSInputFile (img_path )

                    await message .bot .send_photo (
                    chat_id =PUBLIC_GROUP_ID ,
                    message_thread_id =int (WELCOME_TOPIC_ID )if WELCOME_TOPIC_ID and WELCOME_TOPIC_ID !="1"else None ,
                    photo =photo ,
                    caption =welcome_text ,
                    parse_mode ="HTML"
                    )

                    if os .path .exists (img_path ):
                        os .remove (img_path )
                except Exception as e :
                    print (f"Failed to send welcome image: {e }")

                    await message .bot .send_message (
                    chat_id =PUBLIC_GROUP_ID ,
                    message_thread_id =int (WELCOME_TOPIC_ID )if WELCOME_TOPIC_ID and WELCOME_TOPIC_ID !="1"else None ,
                    text =welcome_text ,
                    parse_mode ="HTML"
                    )
@router .message (Command ("testwelcome"))
async def cmd_test_welcome (message :Message ):
    member =message .from_user 
    welcome_text =(
    f"Welcome to HighCore, {member .get_mention (as_html =True )}!\n\n"
    f"Check out our services by messaging our bot directly."
    )

    avatar_bytes =None 
    try :
        user_photos =await message .bot .get_user_profile_photos (member .id ,limit =1 )
        if user_photos .total_count >0 :
            photo_file_id =user_photos .photos [0 ][-1 ].file_id 
            file =await message .bot .get_file (photo_file_id )
            import io 
            avatar_io =io .BytesIO ()
            await message .bot .download_file (file .file_path ,destination =avatar_io )
            avatar_bytes =avatar_io .getvalue ()
    except Exception as e :
        print (f"Failed to fetch avatar: {e }")

    img_path =generate_welcome_card (member .full_name ,avatar_bytes )
    photo =FSInputFile (img_path )

    await message .answer_photo (
    photo =photo ,
    caption =welcome_text ,
    parse_mode ="HTML"
    )
    if os .path .exists (img_path ):
        os .remove (img_path )
