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

# --- Display setup ---
matrixportal = MatrixPortal(status_neopixel=board.NEOPIXEL, debug=False)
network = matrixportal.network
network.connect()

# print(secrets["mqtt_username"])
# print(secrets["mqtt_key"])

mqtt = MQTT.MQTT(
    broker=secrets.get("mqtt_broker"),
    username=secrets["aio_username"],
    password=secrets["aio_key"],
    port=1883,
)

print("MQTT is:     ")
print(mqtt)


MQTT.set_socket(socket, network._wifi.esp)

# TEAM_1_COLOR = 0x00AA00
# TEAM_2_COLOR = 0xAAAAAA

# # Team 1 Score
# matrixportal.add_text(
#     text_font=terminalio.FONT,
#     text_position=(2, int(matrixportal.graphics.display.height * 0.75) - 3),
#     text_color=TEAM_1_COLOR,
#     text_scale=2,
# )

# # Team 2 Score
# matrixportal.add_text(
#     text_font=terminalio.FONT,
#     text_position=(40, int(matrixportal.graphics.display.height * 0.75) - 3),
#     text_color=TEAM_2_COLOR,
#     text_scale=2,
# )

# # Team 1 name
# matrixportal.add_text(
#     text_font=terminalio.FONT,
#     text_position=(2, int(matrixportal.graphics.display.height * 0.25) - 4),
#     text_color=TEAM_1_COLOR,
# )

# # Team 2 name
# matrixportal.add_text(
#     text_font=terminalio.FONT,
#     text_position=(40, int(matrixportal.graphics.display.height * 0.25) - 4),
#     text_color=TEAM_2_COLOR,
# )

# # Static 'Connecting' Text
# matrixportal.add_text(
#     text_font=terminalio.FONT,
#     text_position=(59, 0),
# )

# feeds = {
#     "SOME_FEED": "ahslaughter/feeds/spotify",
# }

last_data = {}

# matrixportal.set_text_color(TEAM_1_COLOR, 0)
# matrixportal.set_text_color(TEAM_2_COLOR, 1)


# def show_connecting(show):
#     if show:
#         matrixportal.set_text(".", 4)
#     else:
#         matrixportal.set_text(" ", 4)

matrixportal.add_text(text_wrap=15, 
                        text_maxlen=25, 
                        text_position=(2, 15),
                        scrolling=False)

matrixportal.add_text(text_color=0xFF8800,
                      text_position=(30,5))
now = time.localtime() 
matrixportal.set_text(now[3], 1)

matrixportal.set_text("waiting for update", 0)

def message_received(client, topic, message):
    print("Received {} for {}".format(message, topic))
    matrixportal.set_text(message, 0)
    matrixportal.scroll_text()
    # last_data[topic] = message
    # update_scores()
    # customize_team_names()


# group = displayio.Group()  # Create a Group
# bitmap = displayio.Bitmap(64, 32, 2)  # Create a bitmap object,width, height, bit depth
color = displayio.Palette(4)  # Create a color palette
color[0] = 0x000000  # black background
color[1] = 0xFF0000  # red
color[2] = 0xCC4000  # amber
color[3] = 0x85FF00  # greenish
font = bitmap_font.load_font("/IBMPlexMono-Medium-24_jep.bdf")
clock_label = Label(font)

BLINK = True


def update_time(*, hours=None, minutes=None, show_colon=False):
    now = time.localtime()  # Get the time values we need
    # struct_time(tm_year=2021, tm_mon=8, tm_mday=8, tm_hour=15, tm_min=20, tm_sec=16, tm_wday=6, tm_yday=220, tm_isdst=-1)
    # print(now)

    matrixportal.set_text('{0}:{1}'.format(now[3], now[4]), 
        1)

    # if hours is None:
    #     hours = now[3]
    # if hours >= 18 or hours < 6:  # evening hours to morning
    #     clock_label.color = color[1]
    # else:
    #     clock_label.color = color[3]  # daylight hours
    # if hours > 12:  # Handle times later than 12:59
    #     hours -= 12
    # elif not hours:  # Handle times between 0:00 and 0:59
    #     hours = 12

    # if minutes is None:
    #     minutes = now[4]

    # if BLINK:
    #     colon = ":" if show_colon or now[5] % 2 else " "
    # else:
    #     colon = ":"

    # clock_label.text = "{hours}{colon}{minutes:02d}".format(
    #     hours=hours, minutes=minutes, colon=colon
    # )
    # bbx, bby, bbwidth, bbh = clock_label.bounding_box
    # # Center the label
    # clock_label.x = 15##round(display.width / 2 - bbwidth / 2)
    # clock_label.y = 4 ## display.height // 2

def get_last_data(feed):
    feed_url = feeds.get(feed)
    return last_data.get(feed_url)


# def customize_team_names():
#     team_1 = "Red"
#     team_2 = "Blue"

#     global TEAM_1_COLOR
#     global TEAM_2_COLOR

#     show_connecting(True)
#     team_name = get_last_data("TEAM_1_FEED")
#     if team_name is not None:
#         print("Team {} is now Team {}".format(team_1, team_name))
#         team_1 = team_name
#     matrixportal.set_text(team_1, 2)
#     team_color = get_last_data("TEAM_1_COLOR_FEED")
#     if team_color is not None:
#         team_color = int(team_color.replace("#", "").strip(), 16)
#         print("Team {} is now Team {}".format(team_1, team_color))
#         TEAM_1_COLOR = team_color
#     matrixportal.set_text_color(TEAM_1_COLOR, 2)
#     matrixportal.set_text_color(TEAM_1_COLOR, 0)
#     team_name = get_last_data("TEAM_2_FEED")
#     if team_name is not None:
#         print("Team {} is now Team {}".format(team_2, team_name))
#         team_2 = team_name
#     matrixportal.set_text(team_2, 3)
#     team_color = get_last_data('TEAM_2_COLOR_FEED')
#     if team_color is not None:
#         team_color = int(team_color.replace("#", "").strip(), 16)
#         print("Team {} is now Team {}".format(team_2, team_color))
#         TEAM_2_COLOR = team_color
#     matrixportal.set_text_color(TEAM_2_COLOR, 3)
#     matrixportal.set_text_color(TEAM_2_COLOR, 1)
#     show_connecting(False)


# def update_scores():
#     print("Updating data from Adafruit IO")
#     show_connecting(True)

#     score_1 = get_last_data('SCORES_1_FEED')
#     if score_1 is None:
#         score_1 = 0
#     matrixportal.set_text(score_1, 0)

#     score_2 = get_last_data('SCORES_2_FEED')
#     if score_2 is None:
#         score_2 = 0
#     matrixportal.set_text(score_2, 1)
#     show_connecting(False)


def subscribe():
    try:
        mqtt.is_connected()
    except MQTT.MMQTTException:
        mqtt.connect()
    mqtt.on_message = message_received


subscribe()
mqtt.subscribe("ahslaughter/feeds/matrix-display-feeds.spotify") ##"ahslaughter/feeds/spotify")
mqtt.on_message = message_received
# customize_team_names()
# update_scores()

last_check = None

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


    try:
        mqtt.is_connected()
        mqtt.loop()
    except (MQTT.MMQTTException, RuntimeError):
        network.connect()
        mqtt.reconnect()

    time.sleep(3)