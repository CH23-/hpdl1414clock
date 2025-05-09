# This file is executed on every boot (including wake-boot from deepsleep)

from machine import Pin
import machine
import network
import ntptime
import time

A0 = Pin(7, Pin.OUT)
A1 = Pin(8, Pin.OUT)
WR0 = Pin(9, Pin.OUT)
WR0.value(1)

network.country('NL')

timezone_offset = 1* 3600
months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Dec"]

chartable = {
    " ":0b0100000,
    "!":0b0100001,
    '"':0b0100010,
    "#":0b0100011,
    "$":0b0100100,
    "%":0b0100101,
    "&":0b0100110,
    "'":0b0100111,
    "<":0b0101000,
    ">":0b0101001,
    "*":0b0101010,
    "+":0b0101011,
    ",":0b0101100,
    "-":0b0101101,
    ".":0b0101110,
    "/":0b0101111,
    "0":0b0110000,
    "1":0b0110001,
    "2":0b0110010,
    "3":0b0110011,
    "4":0b0110100,
    "5":0b0110101,
    "6":0b0110110,
    "7":0b0110111,
    "8":0b0111000,
    "9":0b0111001,
    ":":0b0111010,
    ";":0b0111011,
    "{":0b0111100,
    "=":0b0111101,
    "}":0b0111110,
    "?":0b0111111,
    "@":0b1000000,
    "a":0b1000001,
    "b":0b1000010,
    "c":0b1000011,
    "d":0b1000100,
    "e":0b1000101,
    "f":0b1000110,
    "g":0b1000111,
    "h":0b1001000,
    "i":0b1001001,
    "j":0b1001010,
    "k":0b1001011,
    "l":0b1001100,
    "m":0b1001101,
    "n":0b1001110,
    "o":0b1001111,    
    "p":0b1010000,
    "q":0b1010001,
    "r":0b1010010,
    "s":0b1010011,
    "t":0b1010100,
    "u":0b1010101,
    "v":0b1010110,
    "w":0b1010111,
    "x":0b1011000,
    "y":0b1011001,
    "z":0b1011010,
    "[":0b1011011,
    "\\":0b1011100,
    "]":0b1011101,
    "^":0b1011110,
    "_":0b1011111,  
    }


def letter(inputchar,position):
    lettercode=chartable[inputchar.lower()]
    position = position % 4
    position = 3 - position
    
    for i in range(0,7):
        value=(lettercode>>i)&1
        D=Pin(i, Pin.OUT)
        D.value(value)
        
    A0.value(position & 1)
    A1.value((position >> 1) & 1)
    WR0.value(0)
    time.sleep_us(1)
    WR0.value(1)
    time.sleep_us(1)
        
def printstring(text,startingposition):
    for i, char in enumerate(text):
        currentposition = startingposition+i
        if currentposition > 11:
            return
        letter(char, currentposition)

def clearscreen():
    printstring("    ",0)

#   STAT_IDLE -- 1000
#   STAT_CONNECTING -- 1001
#   STAT_GOT_IP -- 1010
#   STAT_NO_AP_FOUND -- 201
#   STAT_WRONG_PASSWORD -- 202
#   STAT_BEACON_TIMEOUT -- 200
#   STAT_ASSOC_FAIL -- 203
#   STAT_HANDSHAKE_TIMEOUT -- 204

time.sleep(3)

NETWORKS = [('SSID1', 'PASSWORD1'), ('SSID2', 'PASSWORD2')]

def connect_to_wifi():
    printstring("con?",0)
    connected = False
    while not connected:
        for (network_name, network_password) in NETWORKS:
            try:
                wlan = network.WLAN(network.STA_IF)
                ip = wlan.ifconfig()[0]
                if ip != "0.0.0.0":
                    wlan.disconnect()
                    wlan.active(False)
                    time.sleep(4)
                wlan.active(True)
                print("first IP check", ip)
                print("connecting to", network_name)
                if network_password != "":
                    wlan.connect(network_name, network_password)
                    time.sleep(2)
                else:
                    wlan.connect(network_name)
                status = wlan.status()
                while status == 1001:
                    printstring("con.",0)
                    print("connecting...", status)
                    time.sleep(1)
                    status = wlan.status()
            except Exception as e:
                print("err", e)
            finally:
                if wlan.isconnected():
                    printstring("con!",0)
                    print("connected to", network_name)
                    connected = True
                    break
                else:
                    printstring("econ",0)
                    print("connecting failed", status)
                    wlan.disconnect()
                    wlan.active(False)
                    time.sleep(4)

    print("connected to wifi?")
    time.sleep(2)

def is_dst_europe(year, month, day, hour):
    """
    Determine if the given date and time is within European DST.
    DST in Europe:
        - Begins last Sunday of March at 1:00 UTC
        - Ends last Sunday of October at 1:00 UTC
    """
    def last_sunday(year, month):
        # Calculate the last Sunday of a given month and year
        for day in range(31, 24, -1):
            try:
                date = time.localtime(time.mktime((year, month, day, 0, 0, 0, 0, 0, 0)))
                if date[6] == 6:  # 6 is Sunday
                    return day
            except:
                continue
        return 31  # Default if unable to calculate (shouldn't happen)

    march_last_sunday = last_sunday(year, 3)
    october_last_sunday = last_sunday(year, 10)

    # DST begins from last Sunday of March at 1:00 UTC to last Sunday of October at 1:00 UTC
    start_dst = time.mktime((year, 3, march_last_sunday, 1, 0, 0, 0, 0, 0))
    end_dst = time.mktime((year, 10, october_last_sunday, 1, 0, 0, 0, 0, 0))

    current_time = time.mktime((year, month, day, hour, 0, 0, 0, 0, 0))
    return start_dst <= current_time < end_dst

def get_local_time():
    """
    Returns the local time with DST adjustment for Europe.
    """
    local_time_in_seconds = time.mktime(time.localtime()) + timezone_offset
    local_time = time.localtime(local_time_in_seconds)
    year, month, day, hour, minute, second, _, _= local_time

    if is_dst_europe(year, month, day, hour):
        hour += 1  # Add 1 hour for DST
    return (year, month, day, hour, minute, second)
 
def clock(): #only minutes and seconds, because we have 4 digits
    current_time = get_local_time()  # Get the local time
    formatted_time = "{:02d}{:02d}".format(
    current_time[4],current_time[5]
    )
    time.sleep_us(10000)
    printstring(formatted_time,0)
    
def date(): #only month and day, because we have 4 digits
    current_time = get_local_time()  # Get the local time
    formatted_date = "{:02d}{:02d}".format(
    current_time[1], current_time[2]
    )
    printstring(formatted_date,0)

def ntp_sync():
    wlan = network.WLAN(network.STA_IF)
    ip = wlan.ifconfig()[0]
    print("second IP check", ip)
    if ip != "0.0.0.0":
        ntptime.settime()  # This will set the time on the esp32 c3 super mini
        print("ntp")
    else:
        printstring("NOIP",0)
        machine.reset()


ntp_last_called = None
ntp_interval = 3600  # 1 hour in seconds, so check NTP every hour.

def check_and_run_ntp():
    global ntp_last_called
    current_time = time.time()  # Get the current time in seconds

    # Check if the elapsed time since the last call is greater than the interval
    if ntp_last_called is None or current_time - ntp_last_called >= ntp_interval:
        ntp_sync()          # Call the function
        ntp_last_called = current_time  # Update last called time

connect_to_wifi()

while 1:
 check_and_run_ntp()
 clock()
 time.sleep(0.5)
 clock()
 time.sleep(0.5)
 clock()
 time.sleep(0.5)
 clock()
 time.sleep(0.5)
 clock()
 time.sleep(0.5)
 clock()
 time.sleep(0.5)
 date()
 time.sleep(1)
