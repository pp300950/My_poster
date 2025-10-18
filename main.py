# -*- coding: utf-8 -*-
from PIL import Image, ImageDraw, ImageFont
import pandas as pd
from datetime import datetime
import locale

def get_thai_date():
    """สร้างข้อความวันที่ภาษาไทยสำหรับโปสเตอร์"""
    try:
        locale.setlocale(locale.LC_TIME, 'th_TH.UTF-8')
    except locale.Error:
        try:
            locale.setlocale(locale.LC_TIME, 'th_TH')
        except locale.Error:
            print("ไม่สามารถตั้งค่า Locale ภาษาไทยได้")

    now = datetime.now()
    return now.strftime(f"ประจำวันที่ %d %B {now.year + 543}")

def get_value_color(value):
    """กำหนดสีของตัวเลขตามค่า PM2.5"""
    if value <= 15.0: return (0, 157, 224)    # สีฟ้า
    elif value <= 25.0: return (0, 175, 80)     # สีเขียว
    elif value <= 37.5: return (255, 192, 0)    # สีเหลือง
    elif value <= 75.0: return (255, 122, 0)    # สีส้ม
    else: return (237, 28, 36)                  # สีแดง

def create_pm_poster(data_file, template_file, output_file):
    try:
        df = pd.read_csv(data_file)
    except FileNotFoundError:
        print(f"ไม่พบไฟล์ข้อมูล '{data_file}'")
        return

    top_5 = df.nlargest(5, 'Value').reset_index(drop=True)
    bottom_5 = df.nsmallest(5, 'Value').reset_index(drop=True)

    try:
        font_date = ImageFont.truetype("Sarabun-Bold.ttf", 38)
        # เพิ่มฟอนต์สำหรับเลขลำดับ
        font_rank = ImageFont.truetype("Sarabun-Bold.ttf", 34)
        font_location = ImageFont.truetype("Sarabun-Regular.ttf", 34)
        font_value = ImageFont.truetype("Sarabun-Bold.ttf", 60)
        font_unit = ImageFont.truetype("Sarabun-Regular.ttf", 18)
    except IOError:
        print("ไม่พบไฟล์ฟอนต์! กรุณาดาวน์โหลด Sarabun-Bold.ttf และ Sarabun-Regular.ttf")
        return

    # ---! จุดปรับแก้หลัก !---
    # นี่คือชุดพิกัดที่ถูกต้องสำหรับโปสเตอร์เต็มใบ
    
    # ตำแหน่งวันที่
    DATE_POS = (540, 250)
    
    
    
    # พิกัดสำหรับ 5 อันดับสูงสุด
    TOP5_RANK_X = 650         # << เพิ่มใหม่: พิกัดเลขลำดับ
    TOP5_LOCATION_X = 710
    TOP5_VALUE_X = 950
    TOP5_UNIT_X = 1020
    TOP5_START_Y = 415
    Y_STEP = 44               # ระยะห่างระหว่างบรรทัดที่ถูกต้อง

    # พิกัดสำหรับ 5 อันดับต่ำสุด
    BOTTOM5_RANK_X = TOP5_RANK_X # << เพิ่มใหม่
    BOTTOM5_LOCATION_X = TOP5_LOCATION_X
    BOTTOM5_VALUE_X = TOP5_VALUE_X
    BOTTOM5_UNIT_X = TOP5_UNIT_X
    BOTTOM5_START_Y = 665

    try:
        img = Image.open(template_file).convert("RGBA")
        draw = ImageDraw.Draw(img)
    except FileNotFoundError:
        print(f"ไม่พบไฟล์เทมเพลต '{template_file}'")
        return

    # วาดวันที่
    thai_date = get_thai_date()
    draw.text(DATE_POS, thai_date, font=font_date, fill=(0, 77, 136), anchor="mm")

    # วาดข้อมูล 5 อันดับสูงสุด
    for i, row in top_5.iterrows():
        y_pos = TOP5_START_Y + (i * Y_STEP)
        value = row['Value']
        color = get_value_color(value)
        
        # << เพิ่มใหม่: วาดเลขลำดับ >>
        draw.text((TOP5_RANK_X, y_pos), f"{i+1}", font=font_rank, fill="black", anchor="lm")
        
        draw.text((TOP5_LOCATION_X, y_pos), row['Location'], font=font_location, fill="black", anchor="lm")
        draw.text((TOP5_VALUE_X, y_pos), str(value), font=font_value, fill=color, anchor="mm")
        draw.text((TOP5_UNIT_X, y_pos - 15), "มคก./", font=font_unit, fill="black", anchor="lm")
        draw.text((TOP5_UNIT_X, y_pos + 5), "ลบ.ม.", font=font_unit, fill="black", anchor="lm")

    # วาดข้อมูล 5 อันดับต่ำสุด
    for i, row in bottom_5.iterrows():
        y_pos = BOTTOM5_START_Y + (i * Y_STEP)
        value = row['Value']
        color = get_value_color(value)

        # << เพิ่มใหม่: วาดเลขลำดับ >>
        draw.text((BOTTOM5_RANK_X, y_pos), f"{i+1}", font=font_rank, fill="black", anchor="lm")

        draw.text((BOTTOM5_LOCATION_X, y_pos), row['Location'], font=font_location, fill="black", anchor="lm")
        draw.text((BOTTOM5_VALUE_X, y_pos), str(value), font=font_value, fill=color, anchor="mm")
        draw.text((BOTTOM5_UNIT_X, y_pos - 15), "มคก./", font=font_unit, fill="black", anchor="lm")
        draw.text((BOTTOM5_UNIT_X, y_pos + 5), "ลบ.ม.", font=font_unit, fill="black", anchor="lm")

    img.save(output_file, "PNG")
    print(f"สร้างโปสเตอร์สำเร็จ! บันทึกเป็นไฟล์ '{output_file}'")

# --- Main Execution ---
if __name__ == "__main__":
    DATA_FILENAME = "pm_data.csv"
    TEMPLATE_FILENAME = "template.png"
    OUTPUT_FILENAME = f"PM2.5_Report_{datetime.now().strftime('%Y-%m-%d')}.png"
    
    create_pm_poster(DATA_FILENAME, TEMPLATE_FILENAME, OUTPUT_FILENAME)