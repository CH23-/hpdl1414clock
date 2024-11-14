# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
#import webrepl
#webrepl.start()

from machine import Pin
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

last_called = 0
interval = 3600  # 1 hour in seconds, so check NTP every hour.

# Wi-Fi credentials
SSID1 = "" # Replace with your Wi-Fi SSID
PASSWORD1 = "" # Replace with your Wi-Fi password
SSID2 = ""
PASSWORD2 = ""
SSID3 = ""
PASSWORD3 = ""

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
#    display = position // 4
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
#    print(text)
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

NETWORKS = [["ssid2", "password"],["revspace-pub-2.4ghz", ""]]

def connect_to_wifi():
    network_id = 0
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    print("connecting to wifi", wlan.status())
    printstring("con?",0)
    while not wlan.isconnected():
        status = wlan.status()
        try:
            cur_network = NETWORKS[network_id]
            print("connecting to", cur_network[0])
            if cur_network[1] != "":
                wlan.connect(cur_network[0])
            else:
                wlan.connect(cur_network[0], cur_network[1])
            time.sleep(2)
            print("stat", status)
            status = wlan.status()
            while status == 1001:
                printstring("con.",0)
                print("connecting...", status)
                time.sleep(1)
                status = wlan.status()
        except:
            print("err")
        finally:
            if wlan.isconnected():
                printstring("con!",0)
                print("connected to", cur_network[0])
                break
            else:
                printstring("econ",0)
                print("connecting failed", status)
                wlan.disconnect()
                time.sleep(4)
                network_id = (network_id+1)%len(NETWORKS)
                print("now trying", NETWORKS[network_id])
    print("connected to wifi?")

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
    ntptime.settime()  # This will set the time on the Pico W - hopefully also on the esp32 c3 super mini


def check_and_run():
    global last_called
    current_time = time.time()  # Get the current time in seconds

    # Check if the elapsed time since the last call is greater than the interval
    if current_time - last_called >= interval:
        ntp_sync()          # Call the function
        last_called = current_time  # Update last called time

connect_to_wifi()

while 1:
 check_and_run()
 clock()
 time.sleep_us(1000000)
 clock()
 time.sleep_us(1000000)
 clock()
 time.sleep_us(1000000)
 clock()
 time.sleep_us(1000000)
 date()
 time.sleep_us(1000000)


# duur = 200000
# while 1:
#     printstring("            ",0)
#     time.sleep_us(duur)
#     printstring("!!!!!!!!!!!!",0)
#     time.sleep_us(duur)
#     printstring('""""""""""""',0)
#     time.sleep_us(duur)
#     printstring("############",0)
#     time.sleep_us(duur)
#     printstring("$$$$$$$$$$$$",0)
#     time.sleep_us(duur)
#     printstring("%%%%%%%%%%%%",0)
#     time.sleep_us(duur)
#     printstring("&&&&&&&&&&&&",0)
#     time.sleep_us(duur)
#     printstring("''''''''''''",0)
#     time.sleep_us(duur)
#     printstring("<<<<<<<<<<<<",0)
#     time.sleep_us(duur)
#     printstring(">>>>>>>>>>>>",0)
#     time.sleep_us(duur)
#     printstring("************",0)
#     time.sleep_us(duur)
#     printstring("++++++++++++",0)
#     time.sleep_us(duur)
#     printstring(",,,,,,,,,,,,",0)
#     time.sleep_us(duur)
#     printstring("------------",0)
#     time.sleep_us(duur)
#     printstring("............",0)
#     time.sleep_us(duur)
#     printstring("////////////",0)
#     time.sleep_us(duur)
#     printstring("000000000000",0)
#     time.sleep_us(duur)
#     printstring("111111111111",0)
#     time.sleep_us(duur)
#     printstring("222222222222",0)
#     time.sleep_us(duur)
#     printstring("333333333333",0)
#     time.sleep_us(duur)
#     printstring("444444444444",0)
#     time.sleep_us(duur)
#     printstring("555555555555",0)
#     time.sleep_us(duur)
#     printstring("666666666666",0)
#     time.sleep_us(duur)
#     printstring("777777777777",0)
#     time.sleep_us(duur)
#     printstring("888888888888",0)
#     time.sleep_us(duur)
#     printstring("999999999999",0)
#     time.sleep_us(duur)
#     printstring("::::::::::::",0)
#     time.sleep_us(duur)
#     printstring(";;;;;;;;;;;;",0)
#     time.sleep_us(duur)
#     printstring("{{{{{{{{{{{{",0)
#     time.sleep_us(duur)
#     printstring("============",0)
#     time.sleep_us(duur)
#     printstring("}}}}}}}}}}}}",0)
#     time.sleep_us(duur)
#     printstring("????????????",0)
#     time.sleep_us(duur)
#     printstring("@@@@@@@@@@@@",0)
#     time.sleep_us(duur)
#     printstring("aaaaaaaaaaaa",0)
#     time.sleep_us(duur)
#     printstring("bbbbbbbbbbbb",0)
#     time.sleep_us(duur)
#     printstring("cccccccccccc",0)
#     time.sleep_us(duur)
#     printstring("dddddddddddd",0)
#     time.sleep_us(duur)
#     printstring("eeeeeeeeeeee",0)
#     time.sleep_us(duur)
#     printstring("ffffffffffff",0)
#     time.sleep_us(duur)
#     printstring("gggggggggggg",0)
#     time.sleep_us(duur)
#     printstring("hhhhhhhhhhhh",0)
#     time.sleep_us(duur)
#     printstring("iiiiiiiiiiii",0)
#     time.sleep_us(duur)
#     printstring("jjjjjjjjjjjj",0)
#     time.sleep_us(duur)
#     printstring("kkkkkkkkkkkk",0)
#     time.sleep_us(duur)
#     printstring("llllllllllll",0)
#     time.sleep_us(duur)
#     printstring("mmmmmmmmmmmm",0)
#     time.sleep_us(duur)
#     printstring("nnnnnnnnnnnn",0)
#     time.sleep_us(duur)
#     printstring("oooooooooooo",0)
#     time.sleep_us(duur)
#     printstring("pppppppppppp",0)
#     time.sleep_us(duur)
#     printstring("qqqqqqqqqqqq",0)
#     time.sleep_us(duur)
#     printstring("rrrrrrrrrrrr",0)
#     time.sleep_us(duur)
#     printstring("ssssssssssss",0)
#     time.sleep_us(duur)
#     printstring("tttttttttttt",0)
#     time.sleep_us(duur)
#     printstring("uuuuuuuuuuuu",0)
#     time.sleep_us(duur)
#     printstring("vvvvvvvvvvvv",0)
#     time.sleep_us(duur)
#     printstring("wwwwwwwwwwww",0)
#     time.sleep_us(duur)
#     printstring("xxxxxxxxxxxx",0)
#     time.sleep_us(duur)
#     printstring("yyyyyyyyyyyy",0)
#     time.sleep_us(duur)
#     printstring("zzzzzzzzzzzz",0)
#     time.sleep_us(duur)
#     printstring("[[[[[[[[[[[[",0)
#     time.sleep_us(duur)
#     printstring("\\\\\\\\\\\\",0)
#     time.sleep_us(duur)
#     printstring("]]]]]]]]]]]]",0)
#     time.sleep_us(duur)
#     printstring("^^^^^^^^^^^^",0)
#     time.sleep_us(duur)
#     printstring("____________",0)
#     time.sleep_us(duur)

#     printstring(" !\"#$%&'<>*+",0)
#     time.sleep_us(duur)
#     printstring(",-./12345678",0)
#     time.sleep_us(duur)
#     printstring("90abcdefghij",0)
#     time.sleep_us(duur)
#     printstring("klmnopqrstuv",0)
#     time.sleep_us(duur)
#     printstring("wxyz:;{=}?@[",0)
#     time.sleep_us(duur)
#     printstring("\\]^_ UwU :^}",0)
#     time.sleep_us(duur)

