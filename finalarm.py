#!/usr/bin/env python3
# Copyright 2017 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""Run a recognizer using the Google Assistant Library.

The Google Assistant Library has direct access to the audio API, so this Python
code doesn't need to record audio. Hot word detection "OK, Google" is supported.

The Google Assistant Library can be installed with:
    env/bin/pip install google-assistant-library==0.0.2

It is available for Raspberry Pi 2/3 only; Pi Zero is not supported.
"""

import logging
import platform
import subprocess
import sys

import aiy.assistant.auth_helpers
from aiy.assistant.library import Assistant
import aiy.audio
import aiy.voicehat
from time import sleep
from gpiozero import Servo
from google.assistant.library.event import EventType

import RPi.GPIO as GPIO
servo1 = Servo(26)
servo2 = Servo(6)
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
)

# function to control gripper
def SetGripperAngle(angle):
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(26,GPIO.OUT)
	pwm = GPIO.PWM(26,50)
	pwm.start(0)

	duty = angle / 18+2
	
	GPIO.output(26,True)
	pwm.ChangeDutyCycle(duty)
	sleep(2)
	GPIO.output(26,False)
	pwm.ChangeDutyCycle(0)

# function to control wrist
def SetWristAngle1(angle):
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(6,GPIO.OUT)
	pwm = GPIO.PWM(6,50)
	pwm.start(0)

	duty = angle / 18+2
	
	GPIO.output(6,True)
	pwm.ChangeDutyCycle(duty)
	sleep(2)
	GPIO.output(6,False)
	pwm.ChangeDutyCycle(0)
	
# function to control Elbow1
def SetElbowAngle1(angle):
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(13,GPIO.OUT)
	pwm = GPIO.PWM(13,50)
	pwm.start(0)

	duty = angle / 18+2
	
	GPIO.output(13,True)
	pwm.ChangeDutyCycle(duty)
	sleep(2)
	GPIO.output(13,False)
	pwm.ChangeDutyCycle(0)


# function to control Elbow
def SetElbowAngle(angle):
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(5,GPIO.OUT)
	pwm = GPIO.PWM(5,50)
	pwm.start(0)

	duty = angle / 18+2
	
	GPIO.output(5,True)
	pwm.ChangeDutyCycle(duty)
	sleep(2)
	GPIO.output(5,False)
	pwm.ChangeDutyCycle(0)


# function to control base1
def SetBaseAngle1(angle):
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(12,GPIO.OUT)
	pwm = GPIO.PWM(12,50)
	pwm.start(0)

	duty = angle / 18+2
	
	GPIO.output(12,True)
	pwm.ChangeDutyCycle(duty)
	sleep(2)
	GPIO.output(12,False)
	pwm.ChangeDutyCycle(0)
	
# function to control base
def SetBaseAngle(angle):
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(24,GPIO.OUT)
	pwm = GPIO.PWM(24,50)
	pwm.start(0)

	duty = angle / 18+2
	
	GPIO.output(24,True)
	pwm.ChangeDutyCycle(duty)
	sleep(2)
	GPIO.output(24,False)
	pwm.ChangeDutyCycle(0)


#function to control arm through voice
def open():
    aiy.audio.say('opening')
    print('i m opening......')
    SetGripperAngle(20)
    SetWristAngle1(60)
    
def close():
    aiy.audio.say('closing')
    print('I am closing......')
    SetGripperAngle(90)
  
def stand():
    aiy.audio.say('Standing')
    print('I am Standing.....')
    SetBaseAngle1(59)
    SetElbowAngle(133)
    SetElbowAngle1(20)
    SetWristAngle1(120)
    
    

def rotate():
    aiy.audio.say('rotating....')
    print('I am rotating.....')
    SetWristAngle1(0)
    SetWristAngle1(90)
    SetWristAngle1(120)
    SetWristAngle1(90)




def power_off_pi():
    aiy.audio.say('Shutting down.')
    subprocess.call('sudo shutdown now', shell=True)


def reboot_pi():
    aiy.audio.say('Rebooting now.')
    subprocess.call('sudo reboot', shell=True)


def say_ip():
    ip_address = subprocess.check_output("hostname -I | cut -d' ' -f1", shell=True)
    aiy.audio.say('My IP address is %s' % ip_address.decode('utf-8'))


def process_event(assistant, event):
    status_ui = aiy.voicehat.get_status_ui()
    if event.type == EventType.ON_START_FINISHED:
        status_ui.status('ready')
        if sys.stdout.isatty():
            print('Say "OK, Google" then speak, or press Ctrl+C to quit...')

    elif event.type == EventType.ON_CONVERSATION_TURN_STARTED:
        status_ui.status('listening')

    elif event.type == EventType.ON_RECOGNIZING_SPEECH_FINISHED and event.args:
        print('You said:', event.args['text'])
        text = event.args['text'].lower()
        if text == 'power off':
            assistant.stop_conversation()
            power_off_pi()
        elif text == 'reboot':
            assistant.stop_conversation()
            reboot_pi()
        elif text == 'ip address':
            assistant.stop_conversation()
            say_ip()
        elif text == 'open':
            assistant.stop_conversation()
            open()
        elif text == 'close':
            assistant.stop_conversation()
            close()
        elif text == 'stand':
            assistant.stop_conversation()
            stand()
        elif text == 'rotate':
            assistant.stop_conversation()
            rotate()
        
 
    elif event.type == EventType.ON_END_OF_UTTERANCE:
        status_ui.status('thinking')

    elif event.type == EventType.ON_CONVERSATION_TURN_FINISHED:
        status_ui.status('ready')

    elif event.type == EventType.ON_ASSISTANT_ERROR and event.args and event.args['is_fatal']:
        sys.exit(1)


def main():
    if platform.machine() == 'armv6l':
        print('Cannot run hotword demo on Pi Zero!')
        exit(-1)

    credentials = aiy.assistant.auth_helpers.get_assistant_credentials()
    with Assistant(credentials) as assistant:
        for event in assistant.start():
            process_event(assistant, event)


if __name__ == '__main__':
    main()
