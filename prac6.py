#Prac 6 Python file
#!/usr/bin/python3

import RPi.GPIO as GPIO
import Adafruit_MCP3008
from threading import Timer
import time
import os
from datetime import datetime
from datetime import timedelta
import math

#Disable GPIO ste warnings
GPIO.setwarnings(False)

#Setup GPIO pin selection method
GPIO.setmode(GPIO.BCM)

#Setup pins numbers for buttons
s_line_button = 6
mode_switch = 13

#Setup pin numbers for LEDs
LED_1 = 19

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
reading = 0

    # time recording variables
t_start_ready = 0                               #time of start of waiting for entry

pos_1 = 0                                       # stores current position of potentiometer
pos_0 = 0                                       # stores previous position of potentiometer

mode = 0                                        #indicates current mode of operation. initialized to idle mode

#Global variable declarations
global t				        #timer variable

#setup GPIO input pins
GPIO.setup(s_line_button, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(mode_switch, GPIO.IN)

#setup GPIO output pins
GPIO.setup(LED_1, GPIO.OUT)

#setup GPIO io pins for SPI interface
GPIO.setup(SPIMOSI, GPIO.OUT)
GPIO.setup(SPIMISO, GPIO.IN)
GPIO.setup(SPICLK, GPIO.OUT)
GPIO.setup(SPICS, GPIO.OUT)

#setup MCP3008
mcp = Adafruit_MCP3008.MCP3008(clk=SPICLK, cs=SPICS, mosi=SPIMOSI, miso=SPIMISO)

#function declarations
def s_line_button_callback(pin):
    global t_start_ready
    global pos_0
    global mode
    global entry_num
    
    if mode == 0:      # idle mode
        # Record time, position, set mode to ready_to_start:
        t_start_ready = time.time()
        pos_0 = int( (mcp.read_adc(0)/1023) * 127 )
        mode = 1    # mode -> ready_to_start
        entry_num = 0
        print('ready_to_start')     # for testing

def add_code(t_start, t_stop, direction):
    global entry_num
    global durations
    global directions
    global mode
    
    durations[entry_num] = round(t_stop - t_start, 2)
    directions[entry_num] = direction
    
    entry_num += 1
    
    if entry_num > 15:
        mode = 10   # mode -> end_combination

def print_combination():
    for i in range(entry_num):
        if directions[i] == 0:
            print('L', end='')
        else:
            print('R', end='')
        print(durations[i], end=' ')
    print('\n')
        

#setup edge detection for push button
GPIO.add_event_detect(s_line_button, GPIO.FALLING, bouncetime=200, callback=s_line_button_callback)

#setup GPIO output for LEDs, U and L

# Variables -> move to above function declarations later
t_turn_start = 0
t_turn_stop = 0
t_pause_start = 0

entry_num = 0
dir = 0

# temp code usage
read1 = int( (mcp.read_adc(0)/1023) * 127 )
read0 = read1

try:
        while True:
            #temp code:
            read1 = int( (mcp.read_adc(0)/1023) * 127 )
            if (read1 - read0 > 1) or (read0 - read1 > 1):
                read0 = read1
            else:
                read1 = read0
            time.sleep(0.1)
            #-------------------------
            
            
            # sample current position of potentiometer
            #pos_1 = mcp.read_adc(0)
            pos_1 = read1
            
            if mode != 0:
                print(pos_1) # for testing
            
            if mode == 0:      # idle mode
                # flash a light or something
                pos_0 = pos_1

            elif mode == 1:      # ready_to_start mode
                if pos_1 > pos_0:
                    # Record time, position, set mode to turn_right:
                    pos_0 = pos_1
                    t_turn_start = time.time()                    
                    mode = 2    # mode -> turn_right
                elif pos_1 < pos_0:
                    # Record time, position, set mode to turn_left:
                    pos_0 = pos_1
                    t_turn_start = time.time()                    
                    mode = 3    # mode -> turn_left
                elif (time.time() - t_start_ready > 2):
                    mode = 10   # mode -> end_combination
            
            elif mode == 2:  # turn_right mode
                if pos_1 == pos_0:
                    # Record time, position, set mode to turn_right_pause:
##                    print('pos_1 == pos_0')
                    pos_0 = pos_1
                    t_pause_start = time.time()
                    mode = 4    # mode -> turn_right_pause
                elif pos_1 < pos_0:
                    # Direction has changed. Record code and start new code
                    t_turn_stop = time.time()
                    add_code(t_turn_start, t_turn_stop, 1)
                    
                    t_turn_start = time.time()
                    pos_0 = pos_1
                    mode = 3 # mode -> turn_left
                else:
                    pos_0 = pos_1
            
            elif mode == 3: # turn_left mode
                if pos_1 == pos_0:
                    # Record time, position, set mode to turn_left_pause:
                    pos_0 = pos_1
                    t_pause_start = time.time()
                    mode = 5    # mode -> turn_left_pause
                elif pos_1 > pos_0:
                    # Direction has changed. Record code and start new code
                    t_turn_stop = time.time()
                    add_code(t_turn_start, t_turn_stop, 0)
                    
                    t_turn_start = time.time()
                    pos_0 = pos_1
                    mode = 2 # mode -> turn_right
                else:
                    pos_0 = pos_1
            
            elif mode == 4:  # turn_right_pause mode
                if pos_1 > pos_0:
                    # User has continued turning right. Ignore pause.
                    pos_0 = pos_1
                    mode = 2 # mode -> turn_right
                elif pos_1 < pos_0:
                    # Direction has changed. Record code and start new code
                    add_code(t_turn_start, t_pause_start, 1)
                    
                    t_turn_start = time.time()
                    pos_0 = pos_1
                    mode = 3 # mode -> turn_left
                elif (time.time() - t_pause_start > 1):
                    # Dial stopped for 1s. Record code and enter ready_to_start mode
##                    print('turn_right_pause end')
                    add_code(t_turn_start, t_pause_start, 1)
                    t_start_ready = time.time() - 1
                    mode = 1 # mode -> ready_to_start
            
            elif mode == 5:  # turn_left_pause mode
                if pos_1 < pos_0:
                    # User has continued turning left. Ignore pause.
                    pos_0 = pos_1
                    mode = 3 # mode -> turn_left
                elif pos_1 > pos_0:
                    # Direction has changed. Record code and start new code
                    t_turn_stop = time.time()
                    add_code(t_turn_start, t_pause_start, 0)
                    
                    t_turn_start = time.time()
                    pos_0 = pos_1
                    mode = 2 # mode -> turn_right
                elif (time.time() - t_pause_start > 1):
                    # Dial stopped for 1s. Record code and enter ready_to_start mode
                    add_code(t_turn_start, t_pause_start, 0)
                    t_start_ready = time.time() - 1
                    mode = 1 # mode -> ready_to_start
            
            elif mode == 10:     # end_combination mode
                # test code. will be changed
                print_combination()
                print(directions)
                print(durations)
                
                entry_num = 0
                mode = 0    # mode -> idle
                
                
except KeyboardInterrupt:
        GPIO.cleanup()  #cleanup GPIO on keyboard exit

GPIO.cleanup()  #cleanup GPIO on normal exit

