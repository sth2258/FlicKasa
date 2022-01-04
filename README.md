# FlicKasa
Local toggle of Kasa plugs/outlets using Flic buttons

This setup relies on the a local Flask instance running on the same network as the Kasa devices. In my instance, I'm running on a Raspberry Pi. The script here is largely based on the reverse engineering work done by the guys at softScheck - https://github.com/softScheck/tplink-smartplug/

1. Enable Flic SDK within the app and take note of the SDK Password written on the device itself
2. Login to the SDK at https://hubsdk.flic.io/
3. Create a Flic Module - copy the content from the main.js script here into the web editor. 
4. Install the `webapp/app.py` script on your server and update the relevant content
  - Create `Device` objects (line 106-113) for your Kasa devices
  - Set the relevant action of your Flic buttons (line 126 - 157)
