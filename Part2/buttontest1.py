#!/usr/bin/env python3
import time
import board
import digitalio



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


if __name__ == "__main__":
	dt = 0.01
	bu1 = False
	bu1cnt = 0
	bu2 = False
	bu2cnt = 0
	bu3 = False
	bu3cnt = 0
	bu4 = False
	bu4cnt = 0
	relay.value = False
	try:
		while True: 
			if not button1.value:
				if not bu1:
					bu1cnt = bu1cnt +1 
					print('button 1 pressed - event#'+str(bu1cnt))
					bu1 = True
			else:
				if bu1:
					print('button 1 released')
					bu1 = False
			if not button4.value:
				if not bu4:
					bu4cnt = bu4cnt +1 
					print('button 4 pressed - event#'+str(bu4cnt))
					bu4 = True
					relay.value = not relay.value 
			else:
				if bu4:
					print('button 4 released')
					bu4 = False
					
			if relay.value: 
				dt = 0.1
			else:
				dt = 0.01

			time.sleep(dt)
		#end while
	except KeyboardInterrupt:
		print('bye')
	#end try
#end if
