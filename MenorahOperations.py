import os
import threading
from enum import Enum
import time
from flask_socketio import SocketIO
import random


# Import the GPIO library only if not in local development environment
if not os.getenv('LOCAL_DEV'):
    import RPi.GPIO as GPIO

class Mode(Enum):
    Interactive =0
    Strobe = 1
    Wave = 2
    Random = 3


class MenorahOperations:
    def __init__(self, socket: SocketIO):
        self.local_dev = bool(os.getenv('LOCAL_DEV'))
        self.socket = socket
        # Assuming you have a mapping of candle numbers to GPIO pins
        self.pin_map = {1: 16, 2: 11, 3: 13, 4: 22, 5: 18, 6: 36, 7: 12, 8: 15, 9: 29}
        if not self.local_dev:
            GPIO.setmode(GPIO.BOARD)
            for pin in self.pin_map.values():
                GPIO.setup(pin, GPIO.OUT)
                GPIO.output(pin, GPIO.HIGH)
        self.states = [True] * 9  # Initial states for 9 candles
        self.mode = Mode.Interactive
        self.strobe_delay = 0.5
        self.strobe_running = False
        self.strobe_thread = None

        # Wave effect specific variables
        self.wave_running = False
        self.wave_thread = None
        self.wave_delay = 0.07  # Adjust the speed of the wave here

        self.random_running = False
        self.random_thread = None
        self.random_delay=0.07

    def set_mode(self, mode: Mode):
        if mode != self.mode:
            cleanup = {
                Mode.Interactive: None, 
                Mode.Strobe: self.stop_strobe, 
                Mode.Wave: self.stop_wave,
                Mode.Random: self.stop_random
            }
            startup = {
                Mode.Interactive: None, 
                Mode.Strobe: self.start_strobe, 
                Mode.Wave: self.start_wave,
                Mode.Random: self.start_random
            }

            if cleanup[self.mode]:
                cleanup[self.mode]()
            self.mode = mode
            if startup[self.mode]:
                startup[self.mode]()

    def set_candle_state(self, candle_number: int, state: bool, emit_socket=True):
        if not self.local_dev:
            pin = self.pin_map.get(candle_number)
            if pin is not None:
                GPIO.output(pin, GPIO.HIGH if state else GPIO.LOW)
        self.states[candle_number - 1] = state
        if emit_socket:
            self.emit_socket()
    
    def emit_socket(self):
        self.socket.emit('candle_states', self.get_candles_states(), room=None)

    def set_all_candles(self, state: bool=True):
        if not self.local_dev:
            for pin in self.pin_map.values():
                GPIO.output(pin, GPIO.HIGH if state else GPIO.LOW)
        self.states = [state] * 9
   
    def _reset_candles(self):
        if not self.local_dev:
            for pin in self.pin_map.values():
                GPIO.output(pin, GPIO.LOW)
        self.states = [False] * 9

    def get_candles_states(self):
        return self.states
    
    def start_strobe(self, delay=0.3):
        self.strobe_delay = max(0.1, delay)
        if not self.strobe_running:
            self.strobe_running = True
            self.strobe_thread = threading.Thread(target=self._strobe_effect, daemon=True)
            self.strobe_thread.start()

    def stop_strobe(self):
        self.strobe_running = False
        if self.strobe_thread:
            self.strobe_thread.join(timeout=1.0)  # Timeout to avoid indefinite waiting
            self.strobe_thread = None

    def _strobe_effect(self):
        while self.strobe_running:
            for candle_num in self.pin_map:
                self.set_candle_state(candle_num, True, emit_socket=False)
            self.emit_socket()
            time.sleep(self.strobe_delay)  # Strobe speed
            for candle_num in self.pin_map:
                self.set_candle_state(candle_num, False, emit_socket=False)
            self.emit_socket()
            time.sleep(self.strobe_delay*0.2)

    def start_wave(self):
        if not self.wave_running:
            self.wave_running = True
            self.wave_thread = threading.Thread(target=self._wave_effect, daemon=True)
            self.wave_thread.start()

    def stop_wave(self):
        self.wave_running = False
        if self.wave_thread:
            self.wave_thread.join(timeout=1.0)
            self.wave_thread = None

    def _wave_effect(self):
        while self.wave_running:
            for candle_num in self.pin_map:
                self.set_candle_state(candle_num, True)
                time.sleep(self.wave_delay)
                self.set_candle_state(candle_num, False)

    def start_random(self):
        if not self.random_running:
            self.random_running = True
            self.random_thread = threading.Thread(target=self._random_effect, daemon=True)
            self.random_thread.start()

    def stop_random(self):
        self.random_running = False
        if self.random_thread:
            self.random_thread.join(timeout=1.0)
            self.random_thread = None

    def _random_effect(self):
        while self.random_running:
            # Randomly select a candle number
            candle_num = random.choice(list(self.pin_map.keys()))

            # Toggle the selected candle
            self.set_candle_state(candle_num, True)
            time.sleep(self.random_delay)  # Control the speed of toggling
            self.set_candle_state(candle_num, False)

            # Wait a bit before toggling the next random candle
            time.sleep(self.random_delay)
