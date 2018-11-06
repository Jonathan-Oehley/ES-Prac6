#Prac 6 Python file
#!/usr/bin/python3

import pygame
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
c_line = 26

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
durations = [0 for i in range(16)]              #durations array in seconds
directions = [0 for i in range(16)]             #directions array, right = 1, left = 0
words=[[0]*2 for i in range(16)]                #2 by 16 2D data variable for direction, duration combinations 
reading = 0

# time recording variables
t_start_ready = 0                               #time of start of waiting for entry

pos_1 = 0                                       # stores current position of potentiometer
pos_0 = 0                                       # stores previous position of potentiometer

mode = 0                                        #indicates current mode of operation. initialized to idle mode
entry_num = 0

t_turn_start = 0                                #time of the start of turn of the potentiometer
t_turn_stop = 0                                 #time of the end of the turn
t_pause_start = 0                               #start time of a pause/stop in turning 


#setup GPIO input pins
GPIO.setup(s_line_button, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(mode_switch, GPIO.IN)
GPIO.setup(c_line, GPIO.IN)

#setup GPIO output pins
GPIO.setup(LED_1, GPIO.OUT)

#setup GPIO output for LEDs, U and L

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
        time.sleep(0.2)
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

def sort(array):
    for i in range(len(array)):
        min_val = i

        for j in range (i+1, len(array)):
            if array[min_val] > array[j]:
                min[val] = j

        array[i], array[min_val] = array[min_val], array[i]

    return(array)
        

# sound playback setup
#pygame.mixer.pre_init(44100, -16, 1, 512)
#pygame.mixer.init()
pygame.init()


# create sound objects
clickR = pygame.mixer.Sound('clickR_88.wav')
clickL = pygame.mixer.Sound('clickL_88.wav')

#setup edge detection for push button
GPIO.add_event_detect(s_line_button, GPIO.FALLING, bouncetime=200, callback=s_line_button_callback)


# Variables for smoothing of adc input
numReadings = 10
readIndex = 0
total = 0
average = 0
read_avg = 0
readings = [0 for i in range(numReadings)]

def read_adc():
    global numReadings
    global readIndex
    global total
    global average
    global read_avg 
    global readings
    
    # subtract the last reading:
    total = total - readings[readIndex]
    # read from the sensor:
    readings[readIndex] = mcp.read_adc(0)
    # add the reading to the total:
    total = total + readings[readIndex]
    # advance to the next position in the array:
    readIndex = readIndex + 1
    
    # if we're at the end of the array...
    if (readIndex >= numReadings):
        #...wrap around to the beginning:
        readIndex = 0
        
    # calculate the average and round reading:
    average = total / numReadings
    return int( (average/1023) * 127)

try:
        while True:
            pos_1 = read_adc()
            time.sleep(0.02)
            
            if mode != 0:
                print(pos_1) # for testing
            
            if mode == 0:      # idle mode
                # flash a light or something
##                print(pos_1)
                pos_0 = pos_1

            elif mode == 1:      # ready_to_start mode
                if pos_1 > pos_0:
                    # Record time, position, set mode to turn_right:
                    pos_0 = pos_1
                    t_turn_start = time.time()
                    clickR.play()
                    mode = 2    # mode -> turn_right
                elif pos_1 < pos_0:
                    # Record time, position, set mode to turn_left:
                    pos_0 = pos_1
                    t_turn_start = time.time()
                    clickL.play()
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
                    clickR.stop()
                    clickL.play()
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
                    clickL.stop()
                    clickR.play()
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
                    clickR.stop()
                    clickL.play()
                    mode = 3 # mode -> turn_left
                elif (time.time() - t_pause_start > 1):
                    # Dial stopped for 1s. Record code and enter ready_to_start mode
                    add_code(t_turn_start, t_pause_start, 1)
                    t_start_ready = time.time() - 1
                    clickR.stop()
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
                    clickL.stop()
                    clickR.play()
                    mode = 2 # mode -> turn_right
                elif (time.time() - t_pause_start > 1):
                    # Dial stopped for 1s. Record code and enter ready_to_start mode
                    add_code(t_turn_start, t_pause_start, 0)
                    t_start_ready = time.time() - 1
                    clickL.stop()
                    mode = 1 # mode -> ready_to_start
            
            elif mode == 10:     # end_combination mode
                # test code. will be changed
                print_combination()
                print(directions)
                print(durations)
                
                pygame.mixer.stop() #stop any sounds playing
                
                entry_num = 0
                mode = 0    # mode -> idle
                
                
except KeyboardInterrupt:
        GPIO.cleanup()  #cleanup GPIO on keyboard exit
        pygame.mixer.stop() #stop any sounds playing
        pygame.quit()

GPIO.cleanup()  #cleanup GPIO on normal exit
pygame.quit()
