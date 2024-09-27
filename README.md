# Internet-Controllable Hanukkah Sweater
Hacked together in the last few nights of Hanukkah, this web server hosted on a Pi Zero W allows multiple clients to interact with a light-up Hanukkah sweater. Great for parties!

> You may ask yourself – why make a sweater connected to the internet? Well, this sweater broke right before a holiday party, and I thought it would be a great opportunity to make its lighting patterns more complex by controlling it with a Pi Zero. I built the UI so people at the party could scan a QR code to control my sweater's patterns.

### Features
- Lasts for hours on battery
- Beautiful UI including interactive menorah and snow
- Multiple clients can control it at once; the state is synced over WebSocket

Below is a video of my parents controlling the sweater from across the country.
State is immediately synced between their UI and the sweater (okay, minus a few wires that had a short XD)

![Video](images/SweaterVid.gif)