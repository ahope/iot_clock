# Scoreboard matrix display
# uses AdafruitIO to set scores and team names for a scoreboard
# Perfect for cornhole, ping pong, and other games

import time
import board
import terminalio
import displayio
from adafruit_matrixportal.matrixportal import MatrixPortal
from adafruit_display_text.label import Label
from adafruit_matrixportal.network import Network
from adafruit_bitmap_font import bitmap_font
import adafruit_minimqtt.adafruit_minimqtt as MQTT
import adafruit_esp32spi.adafruit_esp32spi_socket as socket
from secrets import secrets
# import openweather_graphics 

# --- Display setup ---
matrixportal = MatrixPortal(status_neopixel=board.NEOPIXEL, debug=False)
network = matrixportal.network
network.connect()

network.get_local_time() 

display = matrixportal.graphics.display

mqtt = MQTT.MQTT(
    broker=secrets.get("mqtt_broker"),
    username=secrets["aio_username"],
    password=secrets["aio_key"],
    port=1883,
)


DISPLAY_CLOCK = 1
DISPLAY_SPOTIFY = 2


CURRENT_DISPLAY = DISPLAY_SPOTIFY## DISPLAY_CLOCK

scroll_delay = 0.03

RED_COLOR = 0xAA0000
TURQUOISE_COLOR = 0x00FFAA
PINK_COLOR = 0xFF0088

text_colors = [TURQUOISE_COLOR, PINK_COLOR, RED_COLOR]
current_text_color = 0

MQTT.set_socket(socket, network._wifi.esp)


last_data = {}

group = None# = displayio.Group()  # Create a Group
bitmap = None # = displayio.Bitmap(64, 32, 2)  # Create a bitmap object,width, height, bit depth
color = None #= displayio.Palette(4)  # Create a color palette

# Create a TileGrid using the Bitmap and Palette
tile_grid = None #= displayio.TileGrid(bitmap, pixel_shader=color)

font = bitmap_font.load_font("/IBMPlexMono-Medium-24_jep.bdf")
clock_label = Label(font)
artist_label = None
title_label = None

small_font = bitmap_font.load_font("/fonts/Arial-12.bdf")
medium_font = bitmap_font.load_font("/fonts/Arial-14.bdf")

BLINK = True




def set_display_clock(): 
    # global matrixportal
    global clock_label
    global group
    global bitmap
    global color
    global display
    # matrixportal.add_text(text_color=0xFF8800,
    #                       text_position=(30,5))
    # now = time.localtime() 
    # matrixportal.set_text(now[3], CLOCK_DISPLAY_TEXT_INDEX)

    # --- Drawing setup ---
    group = displayio.Group()  # Create a Group
    bitmap = displayio.Bitmap(64, 32, 2)  # Create a bitmap object,width, height, bit depth
    color = displayio.Palette(4)  # Create a color palette
    color[0] = 0x000000  # black background
    color[1] = 0xFF0000  # red
    color[2] = 0xCC4000  # amber
    color[3] = 0x85FF00  # greenish

    # Create a TileGrid using the Bitmap and Palette
    tile_grid = displayio.TileGrid(bitmap, pixel_shader=color)
    group.append(tile_grid)  # Add the TileGrid to the Group
    display.show(group)

    clock_label = Label(font)
    clock_label.text = "Yo!"
    clock_label.x = 3
    clock_label.y = 3   

    update_time()
    group.append(clock_label)
    CURRENT_DISPLAY = DISPLAY_CLOCK


def set_display_spotify():
    global title_label
    global artist_label
    group = displayio.Group()
    artist_label = Label(small_font)
    title_label = Label(medium_font)

    now = time.localtime()  # Get the time values we need
    print(now)
    artist_label.text = '{0}:{1}'.format(now[3], now[4])
    title_label.text = "Waiting for update..."

    bbx, bby, bbwidth, bbh = title_label.bounding_box
    # Center the label
    print(title_label.bounding_box)
    title_label.x = 1 #3round(display.width / 2 - bbwidth / 2)
    title_label.y = -1*bby ##display.height // 2

    # bbx, bby, bbwidth, bbh = artist_label.bounding_box
    artist_label.x = 1
    artist_label.y = title_label.y + bbh + 1 ##32 - bbh

    group.append(title_label)
    group.append(artist_label)

    display.show(group)
    CURRENT_DISPLAY = DISPLAY_SPOTIFY


    # matrixportal.add_text(text_wrap=10, 
    #                 text_maxlen=25, 
    #                 text_position=(2, 15),
    #                 scrolling=False)
    # matrixportal.set_text("waiting for update", 0)


def spotify_update(message):
    global title_label
    global artist_label
    index = message.find("|")
    if (index >= 0):
        title_text = message[0:index]
        artist_text = message[index + 1:]
        title_label.text = title_text
        artist_label.text = artist_text
        title_label.color = text_colors[current_text_color]

def scroll_spotify():
    # Run a loop until the label is offscreen again and leave function
    for _ in range(title_label.width):
        # self._scrolling_group.x = self._scrolling_group.x - 1
        title_label.x = title_label.x - 1
        time.sleep(scroll_delay)
    title_label.x = display.width
    for _ in range(display.width):
        title_label.x = title_label.x - 1
        time.sleep(scroll_delay)

    # Run a loop until the label is offscreen again and leave function
    for _ in range(artist_label.width):
        # self._scrolling_group.x = self._scrolling_group.x - 1
        artist_label.x = artist_label.x - 1
        time.sleep(scroll_delay)
    artist_label.x = display.width
    for _ in range(display.width):
        artist_label.x = artist_label.x - 1
        time.sleep(scroll_delay)



def change_display(message):
    if (message == "spotify"):
        set_display_spotify()
    if (message == "clock"):
        set_display_clock()
    pass

def message_received(client, topic, message):
    print("Received {} for {}".format(message, topic))
    if (topic == "ahslaughter/feeds/matrix-display-feeds.color"): 
        color_update(message)
    if (topic == "ahslaughter/feeds/matrix-display-feeds.spotify"):
        spotify_update(message)
    if (topic == "ahslaughter/feeds/matrix-display-feeds.which-display"):
        change_display(message)
    else: 
        matrixportal.set_text(message, 0)
        matrixportal.scroll_text()


localtime_refresh = None
# weather_refresh = None


def update_time(*, hours=None, minutes=None, show_colon=False):
    global clock_label
    global display
    global text_colors
    global current_text_color

    print("updating the time")
    now = time.localtime()  # Get the time values we need
    # print(now)
    # matrixportal.set_text('{0}:{1}'.format(now[3]%12, now[4]), 
    #     CLOCK_DISPLAY_TEXT_INDEX)

    if hours is None:
        hours = now[3]
    if hours >= 18 or hours < 6:  # evening hours to morning
        clock_label.color = color[1]
    else:
        clock_label.color = color[3]  # daylight hours
    if hours > 12:  # Handle times later than 12:59
        hours -= 12
    elif not hours:  # Handle times between 0:00 and 0:59
        hours = 12

    if minutes is None:
        minutes = now[4]

    if BLINK:
        colon = ":" if show_colon or now[5] % 2 else " "
    else:
        colon = ":"

    clock_label.text = "{hours}{colon}{minutes:02d}".format(
        hours=hours, minutes=minutes, colon=colon
    )

    clock_label.color = text_colors[current_text_color]


    bbx, bby, bbwidth, bbh = clock_label.bounding_box
    # Center the label
    clock_label.x = round(display.width / 2 - bbwidth / 2)
    clock_label.y = display.height // 2

    # print(clock_label.bounding_box)
    # print(display.width)

    # if DEBUG:
    print("Label bounding box: {},{},{},{}".format(bbx, bby, bbwidth, bbh))
    print("Label x: {} y: {}".format(clock_label.x, clock_label.y))
    print("label: {}".format(clock_label.text))


# def update_spotify():



def get_last_data(feed):
    feed_url = feeds.get(feed)
    return last_data.get(feed_url)


def subscribe():
    try:
        mqtt.is_connected()
    except MQTT.MMQTTException:
        mqtt.connect()
    mqtt.on_message = message_received

def color_update(which):
    global current_text_color
    print("Changing the color")
    current_text_color = int(which)
    # matrixportal.set_text_color(text_colors[int(which)], 0)



subscribe()
mqtt.subscribe("ahslaughter/feeds/matrix-display-feeds.spotify") ##"ahslaughter/feeds/spotify")
mqtt.subscribe("ahslaughter/feeds/matrix-display-feeds.color") ##"ahslaughter/feeds/spotify")
mqtt.subscribe("ahslaughter/feeds/matrix-display-feeds.which-display")
mqtt.on_message = message_received

last_check = None
localtime_refresh = None


def update_clock():
    global last_check
    if last_check is None or time.monotonic() > last_check + 3600:
        try:
            update_time(
                show_colon=True
            )  # Make sure a colon is displayed while updating
            network.get_local_time()  # Synchronize Board's clock to Internet
            last_check = time.monotonic()
        except RuntimeError as e:
            print("Some error occured, retrying! -", e)

    update_time()



def update_mqtt_messages(): 
    try:
        mqtt.is_connected()
        mqtt.loop()
    except (MQTT.MMQTTException, RuntimeError):
        network.connect()
        mqtt.reconnect()

# set_display_clock()
set_display_spotify()

while True:
    if (CURRENT_DISPLAY == DISPLAY_CLOCK):
        update_clock()
        
    if (CURRENT_DISPLAY == DISPLAY_SPOTIFY):
        scroll_spotify()

    update_mqtt_messages()    

    
    # if (CURRENT_DISPLAY == DISPLAY_WEATHER):
    #     update_weather()

    time.sleep(3)