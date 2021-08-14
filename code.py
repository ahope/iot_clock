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
import openweather_graphics 

# --- Display setup ---
matrixportal = MatrixPortal(status_neopixel=board.NEOPIXEL, debug=False)
network = matrixportal.network
network.connect()


mqtt = MQTT.MQTT(
    broker=secrets.get("mqtt_broker"),
    username=secrets["aio_username"],
    password=secrets["aio_key"],
    port=1883,
)


RED_COLOR = 0xAA0000
TURQUOISE_COLOR = 0x00FFAA
PINK_COLOR = 0xFF0088

text_colors = [TURQUOISE_COLOR, PINK_COLOR, RED_COLOR]

MQTT.set_socket(socket, network._wifi.esp)


last_data = {}

## Stuff for the Clock display 
color = displayio.Palette(4)  # Create a color palette
color[0] = 0x000000  # black background
color[1] = 0xFF0000  # red
color[2] = 0xCC4000  # amber
color[3] = 0x85FF00  # greenish
font = bitmap_font.load_font("/IBMPlexMono-Medium-24_jep.bdf")
clock_label = Label(font)

BLINK = True


## Stuff for the Weather display 
UNITS = "imperial"
# Use cityname, country code where countrycode is ISO3166 format.
# E.g. "New York, US" or "London, GB"
LOCATION = "Seattle, US"
print("Getting weather for {}".format(LOCATION))
# Set up from where we'll be fetching data
DATA_SOURCE = (
    "http://api.openweathermap.org/data/2.5/weather?q=" + LOCATION + "&units=" + UNITS
)
DATA_SOURCE += "&appid=" + secrets["openweather_token"]
# You'll need to get a token from openweather.org, looks like 'b6907d289e10d714a6e88b30761fae22'
# it goes in your secrets.py file on a line such as:
# 'openweather_token' : 'your_big_humongous_gigantor_token',
DATA_LOCATION = []
SCROLL_HOLD_TIME = 0  # set this to hold each line before finishing scroll
if UNITS == "imperial" or UNITS == "metric":
    gfx = openweather_graphics.OpenWeather_Graphics(
        matrixportal.graphics.display, am_pm=True, units=UNITS
    )

def set_display_clock(): 
    matrixportal.add_text(text_wrap=10, 
                        text_maxlen=25, 
                        text_position=(2, 15),
                        scrolling=False)

    matrixportal.add_text(text_color=0xFF8800,
                          text_position=(30,5))
    now = time.localtime() 
    matrixportal.set_text(now[3], 1)

    matrixportal.set_text("waiting for update", 0)
    pass 

def set_display_weather():
    pass

def set_display_spotify():
    pass



def message_received(client, topic, message):
    print("Received {} for {}".format(message, topic))
    if (topic == "ahslaughter/feeds/matrix-display-feeds.color"): 
        color_update(message)
    else: 
        matrixportal.set_text(message, 0)
        matrixportal.scroll_text()


localtime_refresh = None
weather_refresh = None


def update_time(*, hours=None, minutes=None, show_colon=False):
    now = time.localtime()  # Get the time values we need
    matrixportal.set_text('{0}:{1}'.format(now[3]%12, now[4]), 
        1)


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
    print("Changing the color")
    matrixportal.set_text_color(text_colors[int(which)], 0)
    pass


subscribe()
mqtt.subscribe("ahslaughter/feeds/matrix-display-feeds.spotify") ##"ahslaughter/feeds/spotify")
mqtt.subscribe("ahslaughter/feeds/matrix-display-feeds.color") ##"ahslaughter/feeds/spotify")
mqtt.on_message = message_received

# mqtt.add_topic_callback("ahslaughter/feeds/matrix-display-feeds.color", color_update)

# customize_team_names()
# update_scores()

last_check = None
localtime_refresh = None
weather_refresh = None

while True:
    # print("looping")
    # Set the red score text
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

    if (not weather_refresh) or (time.monotonic() - weather_refresh) > 600:
        try:
            value = network.fetch_data(DATA_SOURCE, json_path=(DATA_LOCATION,))
            print("Response is", value)
            gfx.display_weather(value)
            weather_refresh = time.monotonic()
        except RuntimeError as e:
            print("Some error occured, retrying! -", e)
            continue

    gfx.scroll_next_label()
    # Pause between labels
    time.sleep(SCROLL_HOLD_TIME)


    try:
        mqtt.is_connected()
        mqtt.loop()
    except (MQTT.MMQTTException, RuntimeError):
        network.connect()
        mqtt.reconnect()

    time.sleep(3)