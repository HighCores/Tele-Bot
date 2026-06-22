import os 
from PIL import Image ,ImageDraw ,ImageFont ,ImageFilter 
import io 

IMG_DIR =r"C:\Users\omars\OneDrive\Desktop\Worker\HighCores\HighCore Studio\HighCores Studio Identity\HIGHCORE FINAL FINAL"

def create_gradient_image (width ,height ,color_top ,color_bottom ):
    gradient =Image .new ('RGBA',(width ,height ),color_top )
    draw =ImageDraw .Draw (gradient )
    for y in range (height ):
        r =int (color_top [0 ]+(color_bottom [0 ]-color_top [0 ])*y /height )
        g =int (color_top [1 ]+(color_bottom [1 ]-color_top [1 ])*y /height )
        b =int (color_top [2 ]+(color_bottom [2 ]-color_top [2 ])*y /height )
        draw .line ([(0 ,y ),(width ,y )],fill =(r ,g ,b ,255 ))
    return gradient 

def generate_welcome_card (name :str ,avatar_bytes :bytes =None )->str :

    bg_path =os .path .join (IMG_DIR ,"Welcome Message.jpg")
    if not os .path .exists (bg_path ):
        raise FileNotFoundError ("Welcome Message.jpg not found")

    background =Image .open (bg_path ).convert ("RGBA")
    width ,height =background .size 

    avatar_size =642 
    avatar_x =409 
    avatar_y =198 

    if avatar_bytes :
        avatar =Image .open (io .BytesIO (avatar_bytes )).convert ("RGBA")
    else :

        avatar =Image .new ("RGBA",(256 ,256 ),(212 ,175 ,55 ,255 ))

    avatar =avatar .resize ((avatar_size ,avatar_size ),Image .LANCZOS )

    mask =Image .new ("L",(avatar_size ,avatar_size ),0 )
    mask_draw =ImageDraw .Draw (mask )
    mask_draw .ellipse ((0 ,0 ,avatar_size ,avatar_size ),fill =255 )

    background .paste (avatar ,(avatar_x ,avatar_y ),mask )

    name =name .upper ()
    if len (name )>25 :
        name =name [:23 ]+".."

    font_size =60 

    font_path =r"C:\Users\omars\OneDrive\Desktop\Worker\HighCores\HighCore Studio\HighCore Discord Bot\highcore-bot\src\main\resources\templates\Zain-Bold.ttf"
    if not os .path .exists (font_path ):
        font_path ="arial.ttf"

    font =ImageFont .truetype (font_path ,font_size )

    dummy_draw =ImageDraw .Draw (background )
    bbox =dummy_draw .textbbox ((0 ,0 ),name ,font =font )
    name_width =bbox [2 ]-bbox [0 ]
    name_height =bbox [3 ]-bbox [1 ]

    name_box_width =2045 -1204 
    name_x =1204 +(name_box_width -name_width )//2 

    name_y =652 +((725 -652 )//2 )-(name_height //2 )

    shadow_layer =Image .new ("RGBA",background .size ,(0 ,0 ,0 ,0 ))
    shadow_draw =ImageDraw .Draw (shadow_layer )
    shadow_draw .text ((name_x +3 ,name_y +3 ),name ,font =font ,fill =(0 ,0 ,0 ,180 ))
    background =Image .alpha_composite (background ,shadow_layer )

    text_mask =Image .new ("L",background .size ,0 )
    text_mask_draw =ImageDraw .Draw (text_mask )
    text_mask_draw .text ((name_x ,name_y ),name ,font =font ,fill =255 )

    gradient =create_gradient_image (background .width ,background .height ,(197 ,160 ,89 ),(142 ,115 ,65 ))

    gradient_layer =Image .new ("RGBA",background .size ,(0 ,0 ,0 ,0 ))
    gradient_layer .paste (gradient ,(0 ,0 ),text_mask )
    background =Image .alpha_composite (background ,gradient_layer )

    highlight_layer1 =Image .new ("RGBA",background .size ,(0 ,0 ,0 ,0 ))
    ImageDraw .Draw (highlight_layer1 ).text ((name_x ,name_y -1 ),name ,font =font ,fill =(255 ,255 ,255 ,60 ))
    background =Image .alpha_composite (background ,highlight_layer1 )

    highlight_layer2 =Image .new ("RGBA",background .size ,(0 ,0 ,0 ,0 ))
    ImageDraw .Draw (highlight_layer2 ).text ((name_x ,name_y -1 ),name ,font =font ,fill =(240 ,230 ,140 ,100 ))
    background =Image .alpha_composite (background ,highlight_layer2 )

    out_path ="welcome_out.png"
    background .convert ("RGB").save (out_path )
    return out_path 
