import argparse
import socket
import json
from flask import Flask
from flask import request
from struct import pack

app = Flask(__name__)

class Device:
  def __init__(self, devicename, ip, deviceid):
    self.devicename = devicename
    self.ip = ip
    self.deviceid = deviceid


# Predefined Kasa Smart Plug Commands
# For a full list of commands, consult tplink_commands.txt
commands = {'info'       : '{"system":{"get_sysinfo":{}}}',
            'on'         : '{"system":{"set_relay_state":{"state":1}}}',
            'on-target'  : '{"context":{"child_ids":["%ID%"]},"system":{"set_relay_state":{"state":1}}}',
            'off'        : '{"system":{"set_relay_state":{"state":0}}}',
            'off-target' : '{"context":{"child_ids":["%ID%"]},"system":{"set_relay_state":{"state":0}}}',
            'ledoff'     : '{"system":{"set_led_off":{"off":1}}}',
            'ledon'      : '{"system":{"set_led_off":{"off":0}}}',
            'cloudinfo'  : '{"cnCloud":{"get_info":{}}}',
            'wlanscan'   : '{"netif":{"get_scaninfo":{"refresh":0}}}',
            'time'       : '{"time":{"get_time":{}}}',
            'schedule'   : '{"schedule":{"get_rules":{}}}',
            'countdown'  : '{"count_down":{"get_rules":{}}}',
            'antitheft'  : '{"anti_theft":{"get_rules":{}}}',
            'reboot'     : '{"system":{"reboot":{"delay":1}}}',
            'reset'      : '{"system":{"reset":{"delay":1}}}',
            'energy'     : '{"emeter":{"get_realtime":{}}}'
}

# Encryption and Decryption of TP-Link Smart Home Protocol
# XOR Autokey Cipher with starting key = 171
def encrypt(string):
    key = 171
    result = pack(">I", len(string))
    for i in string:
        a = key ^ ord(i)
        key = a
        result += bytes([a])
    return result

def decrypt(string):
    key = 171
    result = ""
    for i in string:
        a = key ^ i
        key = i
        result += chr(a)
    return result

def kasatoggle(dev):
    try:
        sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock_tcp.settimeout(int(10))
        sock_tcp.connect((dev.ip, 9999))
        sock_tcp.settimeout(None)
                
        #Get the info
        sock_tcp.send(encrypt(commands["info"]))
        data = sock_tcp.recv(2048)
        decrypted = decrypt(data[4:])
        #print("Sent(enc):", encrypt(commands["info"]))
        #print("Sent:     ", commands["info"])
        #print("Received: ", decrypted)

        #Single device -  {"system":{"get_sysinfo":{"sw_ver":"1.0.2 Build 200819 Rel.105309","hw_ver":"5.0","model":"HS200(US)","deviceId":"80067C79433DD2AE5591CD6662B578111E606285","oemId":"8754F01961F1BCDAEC5B68B74FFFA7E0","hwId":"6F710464613C9F1EA67305BD422BC2D0","rssi":-27,"latitude_i":407833,"longitude_i":-734693,"alias":"Front Soffit Lights Left","status":"new","mic_type":"IOT.SMARTPLUGSWITCH","feature":"TIM","mac":"00:5F:67:D5:88:06","updating":0,"led_off":0,"relay_state":0,"on_time":0,"icon_hash":"","dev_name":"Smart Wi-Fi Light Switch","active_mode":"schedule","next_action":{"type":1,"id":"2B8D5E4555A47E75AD2BEABD24136AAD","schd_sec":59940,"action":1},"err_code":0}}}
        #Double Device -  {"system":{"get_sysinfo":{"sw_ver":"1.0.6 Build 200821 Rel.090909","hw_ver":"2.0","model":"KP400(US)","deviceId":"8006D423B768AAE715A859F498DE50781E022A75","oemId":"F1196F3490F9EFBDCCAE31630D4BE646","hwId":"1C60F8EEC0C0E044887DA93DBB91BE38","rssi":-60,"longitude_i":-734693,"latitude_i":407833,"alias":"TP-LINK_Smart Plug_4044","status":"new","mic_type":"IOT.SMARTPLUGSWITCH","feature":"TIM","mac":"90:9A:4A:1B:40:44","updating":0,"led_off":0,"children":[{"id":"8006D423B768AAE715A859F498DE50781E022A7500","state":0,"alias":"Right Front Lights","on_time":0,"next_action":{"type":1,"schd_sec":59940,"action":1}},{"id":"8006D423B768AAE715A859F498DE50781E022A7501","state":1,"alias":"Christmas 1","on_time":44463,"next_action":{"type":-1}}],"child_num":2,"ntc_state":0,"err_code":0}}}
        
        get_sysinfo = json.loads(decrypted)
        # Single Device Type Toggle
        if get_sysinfo["system"]["get_sysinfo"]['deviceId'] == dev.deviceid :
            print("Currently, Device is " + str(get_sysinfo["system"]["get_sysinfo"]["relay_state"]))
            if get_sysinfo["system"]["get_sysinfo"]["relay_state"] == 0:
                sock_tcp.send(encrypt(commands["on"]))
                data = sock_tcp.recv(2048)
                decrypted = decrypt(data[4:])
            elif get_sysinfo["system"]["get_sysinfo"]["relay_state"] == 1:
                sock_tcp.send(encrypt(commands["off"]))
                data = sock_tcp.recv(2048)
                decrypted = decrypt(data[4:])
        # Multiple Device Type Toggle
        elif "children" in get_sysinfo["system"]["get_sysinfo"] : 
            for baby in get_sysinfo["system"]["get_sysinfo"]["children"]:
                if baby["id"] == dev.deviceid and baby["state"] == 0:
                    sock_tcp.send(encrypt(commands["on-target"].replace("%ID%",dev.deviceid)))
                    data = sock_tcp.recv(2048)
                    decrypted = decrypt(data[4:])
                elif baby["id"] == dev.deviceid and baby["state"] == 1:
                    sock_tcp.send(encrypt(commands["off-target"].replace("%ID%",dev.deviceid)))
                    data = sock_tcp.recv(2048)
                    decrypted = decrypt(data[4:])
        sock_tcp.close()
    except socket.error:
        quit(f"Could not connect to host {ip}:{port}")
    return



#Get Device IDs from https://github.com/softScheck/tplink-smartplug/
#`kasa` command will run discovery
light_frontSoffitLeft = Device("Front Soffit Lights Left - HS200(US)", "192.168.1.100", "80067C79433DD2AE5591CD6662B578111E606285")
light_frontSoffitRight = Device("Front Soffit Lights Right - HS200(US)", "192.168.1.51", "80066BAC4451744AF31D223238E123F51E608702")
light_frontLeft = Device("Front Left Lights", "192.168.1.228", "8006FC6DBE4703F4FCC9C2EB9B28AFB91E027F9C00")
light_rightFront = Device("Right Front Lights", "192.168.1.92", "8006D423B768AAE715A859F498DE50781E022A7500")
light_christmas1 = Device("Christmas 1", "192.168.1.92", "8006D423B768AAE715A859F498DE50781E022A7501")
light_christmas2 = Device("Christmas 2", "192.168.1.228", "8006FC6DBE4703F4FCC9C2EB9B28AFB91E027F9C01")
light_rearLandscape = Device("Rear Landscape Lights","192.168.1.123","80066F237AE04D2B4827D1E72BD551AA1DFFB41B00")
light_rearFloodLight = Device("Rear Flood Light","192.168.1.123","80066F237AE04D2B4827D1E72BD551AA1DFFB41B01")
light_masterFan = Device("Master Bedroom Fan - HS200(US)", "192.168.1.56", "800638C33F2FAF9BA5C504DCF71E2E081EE6539B")
light_master = Device("Master Bedroom Dimmer - HS220(US)", "192.168.1.116", "80068DCBBCA3C5F344FE56385DC9CDE81EBF5CB1")

@app.route('/', methods = ['POST'])
def index():
    
    content = request.get_json()
    serialnumber = content["serial-number"]
    clicktype = content["click-type"]

    #click, double_click, hold
    print("Serial Number: "+serialnumber + ", Click Type: "+clicktype)
    
    # Playroom Button
    if serialnumber == "BE34-C75495":
        if clicktype == "click":
            kasatoggle(light_rearFloodLight)
            return "Toggle RearFloodLight"
        if clicktype == "double_click":
            kasatoggle(light_rearLandscape)
            return "Toggle RearLandscape"
        if clicktype == "hold":
            #Do nothing?
            return "Do Nothing"
    
    #Backdoor
    if serialnumber == "BF43-C04275":
        if clicktype == "click":
            kasatoggle(light_rearFloodLight)
            return "Toggle RearFloodLight"
        if clicktype == "double_click":
            kasatoggle(light_rearLandscape)
            return "Toggle RearLandscape"
        if clicktype == "hold":
            #Do nothing?
            return "Do Nothing"

    #Master - Steph
    if serialnumber == "BE34-C73768":
        if clicktype == "click":
            kasatoggle(light_master)
            return "Toggle Master Lights"
        if clicktype == "double_click":
            kasatoggle(light_masterFan)
            return "Toggle Master Fan"
        if clicktype == "hold":
            #Do nothing?
            return "Do Nothing"

    #Test button
    if serialnumber == "BF43-C05878":
        if clicktype == "click":
            kasatoggle(light_rearFloodLight)
            return "Toggle RearFloodLight"
        if clicktype == "double_click":
            kasatoggle(light_rearLandscape)
            return "Toggle RearLandscape"
        if clicktype == "hold":
            #Do nothing?
            return "Do Nothing"

    
    return 'Hello world'

if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=5000)
