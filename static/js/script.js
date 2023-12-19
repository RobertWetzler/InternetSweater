snowStorm.excludeMobile = false;
snowStorm.followMouse = true;
snowStorm.vMaxX = 2;
snowStorm.vMaxY = 3;
var socket = io();
function toggleLED() {
    socket.emit('toggle_led');
}
function setMode(mode) {
    socket.emit('set_mode', mode);
}
socket.on('led_state', function (state) {
    var body = document.body;
    var button = document.querySelector('button');
    if (state) {
        body.classList.add('disco');
        button.textContent = 'Turn Off';
    } else {
        body.classList.remove('disco');
        button.textContent = 'Turn On';
    }
});
document.addEventListener('DOMContentLoaded', function () {
    socket.emit('get_led_state');
});