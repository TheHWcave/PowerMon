#!/usr/bin/env python3
#MIT License
#
#Copyright (c) 2019 TheHWcave
#
#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.
#
import time
import Adafruit_GPIO.I2C as I2C
import board
import digitalio

LCD_RS = digitalio.DigitalInOut(board.D26)
LCD_EN = digitalio.DigitalInOut(board.D19)
LCD_D7 = digitalio.DigitalInOut(board.D27)
LCD_D6 = digitalio.DigitalInOut(board.D22)
LCD_D5 = digitalio.DigitalInOut(board.D24)
LCD_D4 = digitalio.DigitalInOut(board.D25)
LCD_COLUMNS = 16
LCD_ROWS = 2
import adafruit_character_lcd.character_lcd as characterlcd
lcd = characterlcd.Character_LCD_Mono(LCD_RS, LCD_EN, LCD_D4, LCD_D5, LCD_D6, LCD_D7, LCD_COLUMNS, LCD_ROWS)

ina = I2C.get_i2c_device(address=0x40, busnum=None)


SHUNT_OHMS = 0.1

INA_REG_CONFIG  = 0x00
INA_REG_SHUNT_V = 0x01
INA_REG_BUS_V   = 0x02
INA_REG_POWER   = 0x03
INA_REG_CURRENT = 0x04
INA_REG_CAL     = 0x05

INA_BUS_16V     = 0
INA_BUS_32V     = 1

INA_SHUNT_40MV  = 0
INA_SHUNT_80MV  = 1
INA_SHUNT_160MV = 2
INA_SHUNT_320MV = 3

CALVAL =   [(32768,1.25E-5,0.00025,40.0),
			(16384,2.5E-5,0.0005,80.0),
			( 8192,5.0E-5,0.001,160.0),
			( 4096,1.0E-4,0.002,320.0)]
INA_ADC_12B_1S  = 0x03
INA_ADC_12B_2S  = 0x09
INA_ADC_12B_4S  = 0x0A
INA_ADC_12B_8S  = 0x0B
INA_ADC_12B_16S = 0x0C
INA_ADC_12B_32S = 0x0D
INA_ADC_12B_64S = 0x0E
INA_ADC_12B_128S= 0x0F

INA_MODE_S_B_C  = 0x07  # shunt and bus  continuous 

INVALID = 9999.9 # invalid value (uninitialized or overflow)

#CALVAL access
CALREG=0
CURLSB=1
PWRLSB=2
SVMAX =3

#VAPS access
VOLTS=0
AMPS =1
PWR  =2
SHUNT=3

#CONF access
BV_RANGE = 0 # busvolt range
SV_RANGE = 1 # shuntvolt range
AV_RATE  = 2 # sampling rate



button1 = digitalio.DigitalInOut(board.D5)
button1.direction = digitalio.Direction.INPUT
button1.pull = digitalio.Pull.UP

button2 = digitalio.DigitalInOut(board.D6)
button2.direction = digitalio.Direction.INPUT
button2.pull = digitalio.Pull.UP

button3 = digitalio.DigitalInOut(board.D12)
button3.direction = digitalio.Direction.INPUT
button3.pull = digitalio.Pull.UP

button4 = digitalio.DigitalInOut(board.D13)
button4.direction = digitalio.Direction.INPUT
button4.pull = digitalio.Pull.UP

relay = digitalio.DigitalInOut(board.D16)
relay.direction = digitalio.Direction.OUTPUT






def writereg(reg, regval):
	value_pair = [(regval >> 8)&0xFF,regval & 0xFF]
	ina.writeList(reg,value_pair)

def configure_INA(bv = INA_BUS_32V, sv = INA_SHUNT_320MV,badc=INA_ADC_12B_1S,sadc=INA_ADC_12B_1S):
	configval = INA_MODE_S_B_C + \
			0x0008 * sadc + \
			0x0080 * badc + \
			0x0800 * sv   + \
			0x2000 * bv
	writereg(INA_REG_CONFIG,configval)
	writereg(INA_REG_CAL,CALVAL[sv][CALREG])


	
def Read_INA(pgaval):
	regval = ina.readU16BE(INA_REG_POWER)
	p = float(regval) * CALVAL[pgaval][PWRLSB]
	regval = ina.readS16BE(INA_REG_CURRENT)
	a = float(regval) * CALVAL[pgaval][CURLSB]
	regval = ina.readS16BE(INA_REG_SHUNT_V)
	s = float(regval) * 0.00001 *1000
	regval = ina.readU16BE(INA_REG_BUS_V)
	if regval & 0x0001 == 1: #math overflow occured
		p = INVALID
		a = INVALID
	v = float(regval>>3) * 0.004 
	return (v,a,p,s)



def Kludge(col,row,txt):
	lcd.cursor_position(col,row)
	for c in txt:
		lcd._write8(ord(c),True)
	
		
if __name__ == "__main__":
	dt = 0.1
	bu1 = False
	bu2 = False
	bu3 = False
	bu4 = False
	oldrange = [-1,-1,-1,-1]
	newrange = [INA_BUS_16V,INA_SHUNT_40MV,INA_ADC_12B_1S ]
	bv_overflow = False
	sv_overflow = False
	
	pga = 0
	#			1234567890123456
	Kludge(0,0,'xx.xxxV +x.xxxA ')
	Kludge(0,1,'xxx.xxW +xxx.xmV')
	relay.value = False
	oldvaps = (INVALID,INVALID,INVALID,INVALID)
	try:
		while True: 
			if oldrange != newrange:
				pga = newrange[SV_RANGE]
				configure_INA(newrange[BV_RANGE], pga,newrange[AV_RATE],newrange[AV_RATE])

				#  SV_RANGE  BV_RANGE  AV_RATE    display
				#     0..3      16V        1S      0..3
				#     0..3      32V        1S      a..d
				#     0..3      16V       >1S      4..7
				#     0..3      32V       >1S      e..h     
				c=pga
				if newrange[AV_RATE] != INA_ADC_12B_1S:
					c = c + 4
				if newrange[BV_RANGE] == INA_BUS_16V:
					c = c +48
				else:
					c = c +97
				Kludge(15,0,chr(c))
				oldrange = list(newrange)
			
			newvaps = Read_INA(pga)
			if newvaps[VOLTS] != oldvaps[VOLTS]:
				bv_overflow = (newvaps[VOLTS] >= 16.0) and (oldrange[BV_RANGE] == INA_BUS_16V)
				Kludge(0,0,"{:6.3f}".format(newvaps[0]))
			if newvaps[AMPS] != oldvaps[AMPS]:
				Kludge(8,0,"{:+6.3f}".format(newvaps[1]))
			if newvaps[PWR] != oldvaps[PWR]:
				Kludge(0,1,"{:6.2f}".format(newvaps[2]))
			if newvaps[SHUNT] != oldvaps[SHUNT]:
				sv_overflow = (abs(newvaps[SHUNT]) >= CALVAL[oldrange[SV_RANGE]][SVMAX])
				Kludge(8,1,"{:+6.1f}".format(newvaps[3]))
			oldvaps = newvaps
		

			if not button1.value:
				if not bu1:
					bu1 = True  # toggle busvolt range
					if oldrange[BV_RANGE] == INA_BUS_16V:
						newrange[BV_RANGE] = INA_BUS_32V
					else:
						newrange[BV_RANGE] = INA_BUS_16V
			else:
				if bu1:
					bu1 = False

			if not button2.value:
				if not bu2:
					bu2 = True  # up shuntvolt range
					if oldrange[SV_RANGE] < INA_SHUNT_320MV:
						newrange[SV_RANGE] = oldrange[SV_RANGE] + 1
			else:
				if bu2:
					bu2 = False
					
			if not button3.value:
				if not bu3:
					bu3 = True  # down shuntvolt range 
					if oldrange[SV_RANGE] > INA_SHUNT_40MV:
						newrange[SV_RANGE] = oldrange[SV_RANGE] - 1
			else:
				if bu3:
					bu3 = False
			
			if not button4.value:
				if not bu4:
					bu4 = True  # toggle smoothing
					if oldrange[AV_RATE] == INA_ADC_12B_1S :
						newrange[AV_RATE] = INA_ADC_12B_8S 
					else:
						newrange[AV_RATE] = INA_ADC_12B_1S 
			else:
				if bu4:
					bu4 = False

			relay.value = sv_overflow or bv_overflow or (oldvaps[AMPS] == INVALID)
			
			time.sleep(dt)
		#end while
	except KeyboardInterrupt:
		print('bye')
	#end try
#end if
