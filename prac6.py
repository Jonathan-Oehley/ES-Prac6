#Prac 6 Python file
#!/usr/bin/python3

import RPi.GPIO as GPIO
import Adafruit_MCP3008
from threading import Timer

#Disable GPIO ste warnings
GPIO.setwarnings(False)

#Setup GPIO pin selection method
GPIO.setmode(GPIO.BCM)

#Setup pins numbers for buttons
s_line_button = 6
mode_switch = 13

#setup pin numbers for SPI interface
SPICLK = 11
SPIMISO = 9
SPIMOSI = 10
SPICS = 8

#Initialize variables for the program operation
tolerence = 50                                  #tolerance of duration readings in ms
sample_time = 100                               #sample time in ms
durations = [0 for i in range(16)]              #durations array
directions = [0 for i in range(16)]             #directions array
words=[[0]*2 for i in range(16)]                #2 by 16 2D data variable for direction, duration combinations 

#Global variable declarations
global t				        #timer variable

#setup GPIO input pins
GPIO.setup(s_line_button, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(mode_switch, GPIO.IN)

#setup GPIO io pins for SPI interface
GPIO.setup(SPIMOSI, GPIO.OUT)
GPIO.setup(SPIMISO, GPIO.IN)
GPIO.setup(SPICLK, GPIO.OUT)
GPIO.setup(SPICS, GPIO.OUT)

#setup MCP3008
mcp = Adafruit_MCP3008.MCP3008(clk=SPICLK, cs=SPICS, mosi=SPIMOSI, miso=SPIMISO)

#function declarations
def s_line_button_callback(pin):
        print("s_line_button_callback")

def read_data():        #modify for prac6
    global rec_num
    global rec_num_max
    global data
    global startTime
    global haveStartTime

    #find time
    time = datetime.now()

    #set the time of first reading
    if haveStartTime != 1:
	startTime = time
	haveStartTime = 1

    #store time and timerValue
    data[rec_num][0] = time
    data[rec_num][1] = str(time - startTime)[:7]

    #read in adc values and convert to appropriate units
    data[rec_num][2] = conv_10bit_to_3V3(mcp.read_adc(0))
    data[rec_num][3] = conv_10bit_to_deg_celsius(mcp.read_adc(1))
    data[rec_num][4] = conv_10bit_to_perc(mcp.read_adc(2))

    rec_num += 1
    rec_num_max = max(rec_num,rec_num_max)
    if rec_num == 5:
        rec_num = 0

    printing()

#setup edge detection for push button
GPIO.add_event_detect(s_line_button, GPIO.FALLING, bouncetime=200, callback=s_line_button_callback)

#setup GPIO output for LEDs, U and L

#purely testing things here

#put into program loop
#print("Setup done. Entering loop")
try:
        while True:
	  #Placeholder for later implementation
          time.sleep(5)
          
except KeyboardInterrupt:
        GPIO.cleanup()  #cleanup GPIO on keyboard exit
        t.cancel()

GPIO.cleanup()  #cleanup GPIO on normal exit

