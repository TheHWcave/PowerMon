#!/usr/bin/env python
import time
import Adafruit_GPIO.I2C as I2C


ina = I2C.get_i2c_device(address=0x40, busnum=None)


SHUNT_OHMS = 0.1

INA_REG_CONFIG  = 0x00
INA_REG_SHUNT_V = 0x01
INA_REG_BUS_V   = 0x02
INA_REG_POWER   = 0x03
INA_REG_CURRENT = 0x04
INA_REG_CAL     = 0x05

INA_BUS_16V     = 0
INA_BUS_32V     = 0

INA_SHUNT_40MV  = 0
INA_SHUNT_80MV  = 1
INA_SHUNT_160MV = 2
INA_SHUNT_320MV = 3

CALVAL =   [(34133,1.2E-5,0.00024),
			(16384,2.5E-5,0.0005),
			( 8192,5.0E-5,0.001),
			( 4096,1.0E-4,0.002)]
INA_ADC_12B_1S  = 0x03
INA_ADC_12B_2S  = 0x09
INA_ADC_12B_4S  = 0x0A
INA_ADC_12B_8S  = 0x0B
INA_ADC_12B_16S = 0x0C
INA_ADC_12B_32S = 0x0D
INA_ADC_12B_64S = 0x0E
INA_ADC_12B_128S= 0x0F

INA_MODE_S_B_C  = 0x07  # shunt and bus  continuous 

power_LSB = 0.0
current_LSB = 0.0


def writereg(reg, regval):
	value_pair = [(regval >> 8)&0xFF,regval & 0xFF]
	ina.writeList(reg,value_pair)
	#print('W:'+hex(regval) +'H='+hex(value_pair[0])+' L='+hex(value_pair[1]))

def configure_INA(busvolts = INA_BUS_32V, shuntvolts = INA_SHUNT_320MV):
	global power_LSB
	global current_LSB
	configval = INA_MODE_S_B_C + \
			0x0008 * INA_ADC_12B_1S + \
			0x0080 * INA_ADC_12B_1S + \
			0x0800 * shuntvolts +     \
			0x2000 * busvolts
	writereg(INA_REG_CONFIG,configval)
	writereg(INA_REG_CAL,CALVAL[shuntvolts][0])
	current_LSB = CALVAL[shuntvolts][1]
	power_LSB = CALVAL[shuntvolts][2]
 

def CalReg():
	regval = ina.readU16BE(INA_REG_CONFIG)
	print('co:'+hex(regval),end='')
	regval = ina.readU16BE(INA_REG_CAL)
	print(' ca:'+hex(regval))
	return regval
	
	
def ShuntVolt():
	regval = ina.readS16BE(INA_REG_SHUNT_V)
	#print('S:'+hex(regval))
	return float(regval) * 0.00001
	
def BusVolt():
	regval = ina.readU16BE(INA_REG_BUS_V)
	#print('B:'+hex(regval))
	return float(regval>>3) * 0.004
	
def Power():
	regval = ina.readU16BE(INA_REG_POWER)
	#print('P:'+hex(regval))
	return float(regval) * power_LSB

def Current():
	regval = ina.readS16BE(INA_REG_CURRENT)
	#print('C:'+hex(regval))
	return float(regval) * current_LSB
	

if __name__ == "__main__":
	dt = 1.0
	configure_INA(INA_BUS_16V, INA_SHUNT_40MV),
	print(power_LSB,current_LSB)
	try:
		while True:
			#configure_INA(INA_BUS_16V, INA_SHUNT_40MV),
			#calreg  = CalReg()
			busvolt = BusVolt()
			shuntvolt = ShuntVolt()
			current = Current()
			power = Power()
			
			print('bus:{0:6.3f}V shunt{1:6.6f}V cur:{2:6.6f}A pwr:{3:6.3f}W'.format(busvolt,shuntvolt,current,power))
			
			time.sleep(dt)
		#end while
	except KeyboardInterrupt:
		print('bye')
	#end try
#end if
