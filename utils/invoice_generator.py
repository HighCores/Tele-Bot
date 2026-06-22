import io 
import requests 
from PIL import Image ,ImageDraw ,ImageFont 
from datetime import date 

COL_GOLD =(197 ,160 ,89 )
COL_WHITE =(255 ,255 ,255 )
COL_CREAM =(234 ,234 ,234 )
BANNER_NEW ="https://i.imgur.com/OHF6qJB.png"

def truncate (s ,n ):
    if not s :
        return ""
    return s [:n -3 ]+"..."if len (s )>n else s 

def generate_invoice (order_id :str ,items :list ,total_price :float ,client_name :str ,project_name :str ,contact :str ,discount :float =0.0 )->bytes :
    try :
        template =Image .open ("assets/invoice.png").convert ("RGBA")
    except :
        try :
            response =requests .get (BANNER_NEW )
            template =Image .open (io .BytesIO (response .content )).convert ("RGBA")
        except :
            template =Image .new ("RGBA",(1000 ,1400 ),(25 ,25 ,25 ,255 ))

    img =Image .new ("RGBA",template .size )
    img .paste (template ,(0 ,0 ))
    draw =ImageDraw .Draw (img )

    W ,H =template .size 
    sX =W /1000.0 
    sY =H /1000.0 

    try :
        font_24 =ImageFont .truetype ("arialbd.ttf",int (24 *sX ))
        font_22 =ImageFont .truetype ("arialbd.ttf",int (22 *sX ))
        font_20 =ImageFont .truetype ("arialbd.ttf",int (20 *sX ))
        font_18 =ImageFont .truetype ("arialbd.ttf",int (18 *sX ))
        font_18_reg =ImageFont .truetype ("arial.ttf",int (18 *sX ))
        font_17 =ImageFont .truetype ("arial.ttf",int (17 *sX ))
        font_16 =ImageFont .truetype ("arialbd.ttf",int (16 *sX ))
        font_16_reg =ImageFont .truetype ("arial.ttf",int (16 *sX ))
        font_23 =ImageFont .truetype ("arialbd.ttf",int (23 *sX ))
    except :
        font_24 =font_22 =font_20 =font_18 =font_18_reg =font_17 =font_16 =font_16_reg =font_23 =ImageFont .load_default ()

    draw .text ((int (685 *sX ),int (152 *sY )),order_id ,fill =COL_GOLD ,font =font_24 ,anchor ="ls")

    uName =truncate (client_name ,20 )
    draw .text ((int (775 *sX ),int (237 *sY )),uName ,fill =COL_WHITE ,font =font_16 ,anchor ="ms")

    statusText ="PENDING"
    draw .text ((int (810 *sX ),int (284 *sY )),statusText ,fill =COL_GOLD ,font =font_18 ,anchor ="ms")

    draw .text ((int (675 *sX ),int (355 *sY )),truncate (client_name ,25 ),fill =COL_WHITE ,font =font_18 ,anchor ="ls")
    if contact :
        draw .text ((int (675 *sX ),int (380 *sY )),truncate (contact ,30 ),fill =COL_CREAM ,font =font_16_reg ,anchor ="ls")

    draw .text ((int (300 *sX ),int (248 *sY )),truncate (project_name ,25 ),fill =COL_WHITE ,font =font_20 ,anchor ="ls")
    draw .text ((int (260 *sX ),int (278 *sY )),"Software Services",fill =COL_CREAM ,font =font_17 ,anchor ="ls")

    addons =[i for i in items if not i .get ('is_main',True )]
    addOnStartY =int (385 *sY )
    for i ,item in enumerate (addons [:6 ]):
        draw .text ((int (145 *sX ),addOnStartY +(i *int (26 *sY ))),"• "+truncate (item ['name'],45 ),fill =COL_CREAM ,font =font_18_reg ,anchor ="ls")

    col_ServicesX =int (150 *sX )
    col_PriceX =int (660 *sX )
    col_QtyX =int (745 *sX )
    col_TotalX =int (830 *sX )
    tableStartY =int (635 *sY )
    tableRowGap =int (45 *sY )

    main_items =[i for i in items if i .get ('is_main',True )]
    for i ,item in enumerate (main_items [:5 ]):
        y =tableStartY +(i *tableRowGap )
        draw .text ((col_ServicesX ,y ),truncate (item ['name'],40 ),fill =COL_WHITE ,font =font_16 ,anchor ="ls")

        pStr =f"${item ['price']:,.2f}"if item ['price']>0 else "Quote"

        draw .text ((col_PriceX ,y ),pStr ,fill =COL_WHITE ,font =font_16_reg ,anchor ="ms")
        draw .text ((col_QtyX ,y ),"1",fill =COL_WHITE ,font =font_16_reg ,anchor ="ms")
        draw .text ((col_TotalX ,y ),pStr ,fill =COL_WHITE ,font =font_16_reg ,anchor ="ms")

    subtotalVal =sum (i ['price']for i in main_items )
    taxVal =subtotalVal *0.05 
    finalTotal =max (0 ,(subtotalVal +taxVal )-discount )

    draw .text ((int (245 *sX ),int (862 *sY )),f"${subtotalVal :,.2f}",fill =(255 ,213 ,112 ),font =font_22 ,anchor ="ls")

    discStr =f"-${discount :,.2f}"
    draw .text ((int (245 *sX ),int (888 *sY )),discStr ,fill =(255 ,213 ,112 ),font =font_22 ,anchor ="ls")

    draw .text ((int (725 *sX ),int (852 *sY )),f"${taxVal :,.2f}",fill =COL_WHITE ,font =font_22 ,anchor ="ls")
    draw .text ((int (775 *sX ),int (888 *sY )),f"${finalTotal :,.2f}",fill =COL_WHITE ,font =font_23 ,anchor ="ls")

    bio =io .BytesIO ()
    img .save (bio ,"PNG")
    bio .seek (0 )
    return bio .getvalue ()
