import os 
from PIL import Image ,ImageDraw ,ImageFont 
import textwrap 
try :
    import arabic_reshaper 
    from bidi .algorithm import get_display 
except ImportError :
    pass 

IMG_DIR =r"C:\Users\omars\OneDrive\Desktop\Worker\HighCores\HighCore Studio\HighCores Studio Identity\HIGHCORE FINAL FINAL"
FONT_PATH =r"C:\Users\omars\OneDrive\Desktop\Worker\HighCores\HighCore Studio\HighCore Discord Bot\highcore-bot\src\main\resources\templates\Zain-Bold.ttf"

def generate_feedback_image (stars :int ,feedback_text :str ,output_path :str ):

    stars =max (1 ,min (5 ,int (stars )))
    template_path =os .path .join (IMG_DIR ,f"Feedback_{stars }_.jpg")

    if not os .path .exists (template_path ):
        raise FileNotFoundError (f"Template not found: {template_path }")

    img =Image .open (template_path ).convert ("RGBA")
    draw =ImageDraw .Draw (img )

    try :
        font =ImageFont .truetype (FONT_PATH ,45 )
    except Exception as e :
        print (f"Error loading font: {e }")
        font =ImageFont .load_default ()

    import re 

    clean_text =re .sub (r'[^\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF\u0020-\u007E\n]','',feedback_text )

    try :
        import arabic_reshaper 
        from bidi .algorithm import get_display 
        reshaper =arabic_reshaper .ArabicReshaper (
        configuration ={
        'delete_harakat':False ,
        'support_ligatures':True ,
        'use_unshaped_instead_of_isolated':True 
        }
        )
        reshaped_text =reshaper .reshape (clean_text )
        bidi_text =get_display (reshaped_text )
    except ImportError :
        bidi_text =clean_text 

    x ,y =545 ,341 
    box_w ,box_h =1273 -545 ,592 -341 

    lines =[]
    paragraphs =bidi_text .split ('\n')
    for p in paragraphs :

        words =p .split ()
        curr_line =""
        for word in words :
            test_line =f"{curr_line } {word }".strip ()
            bbox =draw .textbbox ((0 ,0 ),test_line ,font =font )
            if (bbox [2 ]-bbox [0 ])<=box_w :
                curr_line =test_line 
            else :
                lines .append (curr_line )
                curr_line =word 
        if curr_line :
            lines .append (curr_line )

    curr_y =y 
    for line in lines :
        bbox =draw .textbbox ((0 ,0 ),line ,font =font )
        h =bbox [3 ]-bbox [1 ]
        w =bbox [2 ]-bbox [0 ]

        line_x =x +(box_w -w )/2 
        draw .text ((line_x ,curr_y ),line ,fill =(255 ,255 ,255 ,255 ),font =font )
        curr_y +=h +10 
        if curr_y >y +box_h :
            break 

    final_img =img .convert ("RGB")
    final_img .save (output_path ,format ="PNG")
    return output_path 
