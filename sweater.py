from MenorahOperations import MenorahOperations
from flask import Flask, render_template
from flask_socketio import SocketIO
import atexit
import RPi.GPIO as GPIO
from MenorahOperations import Mode

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
menorah = MenorahOperations(socketio)


@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('update_candle')
def handle_update_candle(data):
    menorah.set_mode(Mode.Interactive)
    candle_number = data['candleNumber']
    state = data['state']
    menorah.set_candle_state(candle_number, state)
    socketio.emit('candle_states', menorah.get_candles_states(), room=None)


@socketio.on('toggle_led')
def handle_update_all_candle():
    menorah.set_mode(Mode.Interactive)
    all_on = all(menorah.get_candles_states())
    menorah.set_all_candles(not all_on)
    socketio.emit('candle_states', menorah.get_candles_states(), room=None)

@socketio.on('connect')
def handle_connect():
    socketio.emit('candle_states', menorah.get_candles_states(), room=None)

@socketio.on('set_mode')
def handle_set_mode(mode):
    mode_map = {'strobe': Mode.Strobe, 'interactive': Mode.Interactive, 'wave': Mode.Wave, 'random': Mode.Random}
    if mode in mode_map:
        menorah.set_mode(mode_map[mode])


def cleanup():
    GPIO.cleanup()
    print("GPIO cleanup done!")

atexit.register(cleanup)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=False, allow_unsafe_werkzeug=True)
