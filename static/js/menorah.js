document.addEventListener("DOMContentLoaded", function() {
    var scene = document.querySelector('.scene');
    var isTouchDevice = 'ontouchstart' in window || navigator.maxTouchPoints > 0 || navigator.msMaxTouchPoints > 0;

    if (isTouchDevice) {
        scene.addEventListener("touchend", handleFireToggle);
    } else {
        scene.addEventListener("click", handleFireToggle);
    }

    var touchHandled = false;

    function handleFireToggle(event) {
        if (event.type === "touchend") {
            touchHandled = true;
        } else if (touchHandled) {
            touchHandled = false;
            return;
        }

        toggleFire(event);
    }

    function toggleFire(event) {
        if (event.target.classList.contains('fire')) {
            var candleNumber = Array.from(scene.querySelectorAll('.fire')).indexOf(event.target) + 1;
            var newState = event.target.style.opacity !== "1";
            socket.emit('update_candle', { candleNumber: candleNumber, state: newState });
        }
    }

    socket.on('candle_states', function(states) {
        var fires = scene.querySelectorAll('.fire');
        states.forEach(function(state, index) {
            fires[index].style.opacity = state ? "1" : "0";
        });
    });
});
