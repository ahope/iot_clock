

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

# --- Display setup ---
matrixportal = MatrixPortal(status_neopixel=board.NEOPIXEL, debug=False)
display = matrixportal.graphics.display

# --- Network setup ---
network = matrixportal.network
network.connect()
network.get_local_time() 

# --- MQTT Setup ---
mqtt = MQTT.MQTT(
    broker=secrets.get("mqtt_broker"),
    username=secrets["aio_username"],
    password=secrets["aio_key"],
    port=1883,
)

MQTT.set_socket(socket, network._wifi.esp)

MQTT_URL_SPOTIFY = "ahslaughter/feeds/matrix-display-feeds.spotify"
MQTT_URL_COLOR = "ahslaughter/feeds/matrix-display-feeds.color"
MQTT_URL_WHICH_DISPLAY = "ahslaughter/feeds/matrix-display-feeds.which-display"

MQTT_TOPIC_COLOR = "color"
MQTT_TOPIC_WHICH_DISPLAY = "which-display"
MQTT_TOPIC_SPOTIFY = "spotify"

## --- Display Options ---
DISPLAY_CLOCK = 1
DISPLAY_SPOTIFY = 2

current_display = DISPLAY_SPOTIFY

scroll_delay = 0.03

NUM_COLORS = 5
RED = 0xAA0000
TURQUOISE = 0x00FFAA
PINK = 0xFF0088
YELLOW = 0xFFFF00
ORANGE = 0xFF7722

text_colors = [RED, ORANGE, YELLOW, TURQUOISE, PINK]
current_text_color = 0

## --- Fonts ---
font = bitmap_font.load_font("/IBMPlexMono-Medium-24_jep.bdf")
small_font = bitmap_font.load_font("/fonts/Arial-12.bdf")
medium_font = bitmap_font.load_font("/fonts/Arial-14.bdf")

## --- MQTT data and info ---
last_data = {}




## --- Clock data and info ---
group = None
bitmap = None
color = None

# Create a TileGrid using the Bitmap and Palette
tile_grid = None 

clock_label = Label(font)
artist_label = None
title_label = None

BLINK = True

last_time_check = None

TIME_STRING_FORMAT = "{hours}{colon}{minutes:02d}"
current_time_string = None


def set_display_clock(): 
    print("setting up the clock display")
    global clock_label
    global group
    global bitmap
    global color
    global display
    global current_display

    # --- Drawing setup ---
    group = displayio.Group()  # Create a Group
    bitmap = displayio.Bitmap(64, 32, 2)  # Create a bitmap object,width, height, bit depth

    # Create a TileGrid using the Bitmap and Palette
    tile_grid = displayio.TileGrid(bitmap, pixel_shader=color)
    group.append(tile_grid)  # Add the TileGrid to the Group
    display.show(group)

    clock_label = Label(font) 

    update_time()
    group.append(clock_label)
    current_display = DISPLAY_CLOCK
    print("curent display is hte clock")


def set_display_spotify():
    global title_label
    global artist_label
    global current_display
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
    title_label.x = 1 
    title_label.y = -1*bby 

    artist_label.x = 1
    artist_label.y = title_label.y + bbh + 1 

    group.append(title_label)
    group.append(artist_label)

    display.show(group)

    mqtt.subscribe(MQTT_URL_SPOTIFY)
    mqtt.add_topic_callback(MQTT_TOPIC_SPOTIFY, spotify_update)

    current_display = DISPLAY_SPOTIFY

def clear_display_spotify():
    mqtt.unsubscribe(MQTT_URL_SPOTIFY)
    mqtt.remove_topic_callback(MQTT_TOPIC_SPOTIFY)


def spotify_update(message):
    global title_label
    global artist_label
    print("got a spotify update!")
    last_data.push(message)
    index = message.find("|")
    if (index >= 0):
        title_text = message[0:index]
        artist_text = message[index + 1:]
        title_label.text = title_text
        artist_label.text = artist_text
        title_label.color = text_colors[current_text_color]

def scroll_spotify():
    if len(last_data) == 0: 
        artist_label.text = current_time_string

    title_label.color = text_colors[current_text_color]

    if title_label.width > display.width: 
        # Run a loop until the label is offscreen again and leave function
        for _ in range(title_label.width):
            title_label.x = title_label.x - 1
            time.sleep(scroll_delay)
        title_label.x = display.width
        for _ in range(display.width):
            title_label.x = title_label.x - 1
            time.sleep(scroll_delay)

    if artist_label.width > display.width:
        # Run a loop until the label is offscreen again and leave function
        for _ in range(artist_label.width):
            artist_label.x = artist_label.x - 1
            time.sleep(scroll_delay)
        artist_label.x = display.width
        for _ in range(display.width):
            artist_label.x = artist_label.x - 1
            time.sleep(scroll_delay)

def change_display(message):
    if (message != "spotify"):
        clear_display_spotify()

    if (message == "spotify"):
        set_display_spotify()
        return
    if (message == "clock"):
        set_display_clock()
        return
    print(message)

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


### Checks the current time
### Populates the global current_time_string with the current time. 
def update_time(*, hours=None, minutes=None, show_colon=False):
    global current_time_string

    now = time.localtime()  # Get the time values we need

    if hours is None:
        hours = now[3]
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

    current_time_string = TIME_STRING_FORMAT.format(
        hours=hours, minutes=minutes, colon=colon
    )



def get_last_data(feed):
    feed_url = feeds.get(feed)
    return last_data.get(feed_url)


def subscribe():
    try:
        mqtt.is_connected()
    except MQTT.MMQTTException:
        mqtt.connect()
    
    mqtt.subscribe(MQTT_URL_COLOR)
    mqtt.subscribe(MQTT_URL_WHICH_DISPLAY)
    mqtt.on_message = message_received
    mqtt.add_topic_callback(MQTT_TOPIC_COLOR, color_update)
    mqtt.add_topic_callback(MQTT_TOPIC_WHICH_DISPLAY, change_display)

def color_update(which):
    global current_text_color
    print("color_update")
    new_color_index = int(which)
    if new_color_index < NUM_COLORS:
        current_text_color = new_color_index


def update_clock():
    clock_label.text = current_time_string

    clock_label.color = text_colors[current_text_color]
    bbx, bby, bbwidth, bbh = clock_label.bounding_box
    # Center the label
    clock_label.x = round(display.width / 2 - bbwidth / 2)
    clock_label.y = display.height // 2


def update_mqtt_messages(): 
    try:
        mqtt.is_connected()
        mqtt.loop()
    except (MQTT.MMQTTException, RuntimeError):
        network.connect()
        mqtt.reconnect()

subscribe()
# set_display_clock()
set_display_spotify()

while True:
    if last_time_check is None or time.monotonic() > last_time_check + 3600:
        network.get_local_time()  # Synchronize Board's clock to Internet
        last_time_check = time.monotonic()
    update_time(show_colon=True)

    if (current_display == DISPLAY_CLOCK):
        update_clock()
        
    if (current_display == DISPLAY_SPOTIFY):
        scroll_spotify()

    update_mqtt_messages()    

    time.sleep(1)