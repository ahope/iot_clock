# Metro Matrix Clock
# Runs on Airlift Metro M4 with 64x32 RGB Matrix display & shield

import time
import board
import displayio
import terminalio
from adafruit_display_text.label import Label
from adafruit_bitmap_font import bitmap_font
from adafruit_matrixportal.network import Network
from adafruit_matrixportal.matrix import Matrix

import circuitpython_base64 as base64
import busio
from digitalio import DigitalInOut
import adafruit_requests as requests
import adafruit_esp32spi.adafruit_esp32spi_socket as socket
from adafruit_esp32spi import adafruit_esp32spi


DEBUG = False

# Get wifi details and more from a secrets.py file
try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise
print("    Metro Minimal Clock")
print("Time will be set for {}".format(secrets["timezone"]))

## TESTING REQUESTS via ESP

# If you are using a board with pre-defined ESP32 Pins:
esp32_cs = DigitalInOut(board.ESP_CS)
esp32_ready = DigitalInOut(board.ESP_BUSY)
esp32_reset = DigitalInOut(board.ESP_RESET)

# If you have an externally connected ESP32:
# esp32_cs = DigitalInOut(board.D9)
# esp32_ready = DigitalInOut(board.D10)
# esp32_reset = DigitalInOut(board.D5)

# If you have an AirLift Featherwing or ItsyBitsy Airlift:
# esp32_cs = DigitalInOut(board.D13)
# esp32_ready = DigitalInOut(board.D11)
# esp32_reset = DigitalInOut(board.D12)

spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)

print("Connecting to AP...")
while not esp.is_connected:
    try:
        esp.connect_AP(secrets["ssid"], secrets["password"])
    except RuntimeError as e:
        print("could not connect to AP, retrying: ", e)
        continue
print("Connected to", str(esp.ssid, "utf-8"), "\tRSSI:", esp.rssi)

# Initialize a requests object with a socket and esp32spi interface
socket.set_interface(esp)
requests.set_socket(socket, esp)

if (DEBUG): 

    TEXT_URL = "http://wifitest.adafruit.com/testwifi/index.html"
    JSON_GET_URL = "https://httpbin.org/get"
    JSON_POST_URL = "https://httpbin.org/post"

    print("Fetching text from %s" % TEXT_URL)
    response = requests.get(TEXT_URL)
    print("-" * 40)

    print("Text Response: ", response.text)
    print("-" * 40)
    response.close()

    print("Fetching JSON data from %s" % JSON_GET_URL)
    response = requests.get(JSON_GET_URL)
    print("-" * 40)

    print("JSON Response: ", response.json())
    print("-" * 40)
    response.close()

    data = "31F"
    print("POSTing data to {0}: {1}".format(JSON_POST_URL, data))
    response = requests.post(JSON_POST_URL, data=data)
    print("-" * 40)

    json_resp = response.json()
    # Parse out the 'data' key from json_resp dict.
    print("Data received from server:", json_resp["data"])
    print("-" * 40)
    response.close()

    json_data = {"Date": "July 25, 2019"}
    print("POSTing data to {0}: {1}".format(JSON_POST_URL, json_data))
    response = requests.post(JSON_POST_URL, json=json_data)
    print("-" * 40)

    json_resp = response.json()
    # Parse out the 'json' key from json_resp dict.
    print("JSON Data received from server:", json_resp["json"])
    print("-" * 40)
    response.close()


# ## Spotify Authorization
url = "https://accounts.spotify.com/api/token"
headers = {}
data = {}

# Encode as Base64
message = f"{secrets['spotify_client_id']}:{secrets['spotify_client_secret']}"
print("message to send to spotify: ")
print(message)

messageBytes = message.encode('ascii')
base64Bytes = base64.b64encode(messageBytes)
base64Message = base64Bytes.decode('ascii')


headers['Authorization'] = f"Basic {base64Message}"
data['grant_type'] = "client_credentials"
json_data_grant_type = {"grant_type" : "client_credentials"}

r = requests.post(url, headers=headers, json=json_data_grant_type) ##data=data)

print(r.text)
token = r.json()['access_token']

# # Step 2 - Use Access Token to call playlist endpoint

# playlistId = "myPlaylistId"
# playlistUrl = f"https://api.spotify.com/v1/playlists/{playlistId}"
# headers = {
#     "Authorization": "Bearer " + token
# }

# res = requests.get(url=playlistUrl, headers=headers)

# print(json.dumps(res.json(), indent=2))

## ===============

# bear = secrets['bearer_token']

# DATA_SOURCE = ('https://api.twitter.com/2/tweets/search/recent?query=#partyparrot to:blitzcitydiy')
# DATA_LOCATION = ["meta", "newest_id"]

# matrixportal = MatrixPortal(
#     url=DATA_SOURCE,
#     json_path=DATA_LOCATION,
#     status_neopixel=board.NEOPIXEL
# )




#### =============  CLOCK =========

BLINK = True




# --- Display setup ---
matrix = Matrix()
display = matrix.display
# network = Network(status_neopixel=board.NEOPIXEL, debug=False)

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

if not DEBUG:
    font = bitmap_font.load_font("/IBMPlexMono-Medium-24_jep.bdf")
else:
    font = terminalio.FONT

clock_label = Label(font)


def update_time(*, hours=None, minutes=None, show_colon=False):
    now = time.localtime()  # Get the time values we need
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
    bbx, bby, bbwidth, bbh = clock_label.bounding_box
    # Center the label
    clock_label.x = round(display.width / 2 - bbwidth / 2)
    clock_label.y = display.height // 2
    if DEBUG:
        print("Label bounding box: {},{},{},{}".format(bbx, bby, bbwidth, bbh))
        print("Label x: {} y: {}".format(clock_label.x, clock_label.y))


last_check = None
update_time(show_colon=True)  # Display whatever time is on the board
group.append(clock_label)  # add the clock label to the group

while True:
    if last_check is None or time.monotonic() > last_check + 3600:
        try:
            update_time(
                show_colon=True
            )  # Make sure a colon is displayed while updating
            # network.get_local_
            time()  # Synchronize Board's clock to Internet
            last_check = time.monotonic()
        except RuntimeError as e:
            print("Some error occured, retrying! -", e)

    update_time()
    time.sleep(1)
