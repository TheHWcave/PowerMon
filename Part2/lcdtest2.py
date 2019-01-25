import board
import digitalio
import time
lcd_rs = digitalio.DigitalInOut(board.D26)
lcd_en = digitalio.DigitalInOut(board.D19)
lcd_d7 = digitalio.DigitalInOut(board.D27)
lcd_d6 = digitalio.DigitalInOut(board.D22)
lcd_d5 = digitalio.DigitalInOut(board.D24)
lcd_d4 = digitalio.DigitalInOut(board.D25)
lcd_columns = 16
lcd_rows = 2


import adafruit_character_lcd.character_lcd as characterlcd
lcd = characterlcd.Character_LCD_Mono(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7, lcd_columns, lcd_rows)

def Kludge(txt):
	for c in txt:
		lcd._write8(ord(c),True)  # yeah, I know ...

if __name__ == "__main__":
	lcd.clear()
	Kludge('Hello World')
	time.sleep(3.0)
	
	Kludge(' ok')
	time.sleep(10.0)

	lcd.clear()
	Kludge('show cursor')
	lcd.cursor =True
	lcd.blink = True
	lcd.cursor_position(8,1)
	time.sleep(10.0)
	
	Kludge('hi ')
	time.sleep(10.0)
	
	Kludge('there')
