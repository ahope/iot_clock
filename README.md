
# IoT Spotify Clock

My goal with this project was to become better acquainted with an [RGB LED Matrix](https://www.adafruit.com/product/5036) from AdaFruit. I wanted to be able to show two different things: 

* The time
* What I'm currently listening to on Spotify

I originally wanted to be able to swap between many different displays (e.g., weather), but simplified to better understand the capabilities and constraints before taking that step. 

The (current) final output is a voice-activated display. It starts by showing the time while waiting to update from Spotify. When a song is played, it displays 
the title and artist. At any point, I can swap between the clock display and the Spotify display. I can also ask to change the color of the primary display. 

![image](https://media.giphy.com/media/h0UTMkgSwvAoSCCqaU/giphy.gif?cid=790b76111a91e0a7643c755ff39486fa9b73d34ee3ace350&rid=giphy.gif)

The swapping of display and color is done using an Alexa skill: 


<img src="https://github.com/ahope/iot_clock/blob/master/alexa.png" width="200">

# Requirements

### Hardware

* Adafruit RGB LED Matrix: https://www.adafruit.com/product/2278
* Adafruit MatrixPortal board:  https://www.adafruit.com/product/4745

This project was based on AdaBox 016-- a 64x32 RGB LED Matrix, with the MatrixPortal M4 board. The board is CircuitPython friendly, but can also be used with the Arduino IDE for lower-level programming. 

### Software/Third Parties

* adafruit.io (MQTT Broker)
* IFTTT 
* Alexa (Either a device, or the app)
* Alexa Skill 
* Spotify
* Abode (not required-- I just added this for fun!)

## System Overview

Here's an overview of the entire system: 

<img src="https://github.com/ahope/iot_clock/blob/master/iot_clock_diagram_1.png" width="250">

To change the display via Alexa: 

* Tell Alexa to either change the color or the display. 
* The Alexa backend sends a message to the adafruit.io MQTT webhook. 
* The display is subscribed to the MQTT broker, and when notified of an update, either changes the display or the color of the display. 

To update the message/song on the display: 

* There are 2 applets on IFTTT: 
   * Spotify: Every hour, notify adafruit.io what songs have been played. 
   * Abode: When the system status changes, notify adafruit.io of the update.


## Details

#### Basic setup: 

* Initialize the display
* Initialize the network 
* Initialize the MQTT client
* Initialize the colors and fonts
* Set up the MQTT subscriptions for color and display changing

#### Enabling Clock Display: `set_display_clock()`

* Create a display Group
* Show the Group
* Create a label for the display
* Get the time (via the network-- ensure the chip clock matches the correct time zone)
* Figure out the correct placement based on size
* Add the label to the Group
* Remember that the clock is being displayed

#### Enabling Spotify Display: `set_display_spotify()`

* Create a display Group
* Create artist/title labels
* Set the default text for the two labels
* Set the correct placement for the labels
* Show the display group
* Remember that the spotify stuff is being displayed

#### The `run` loop: 

* If the clock is showing: 
    - Check if the time has changed (next minute-- roughly check every minute)
* If the spotify feed is showing: 
    - Scroll the labels
* Check for new MQTT messages
    - Check that we're still connected
    - Check if any messages have come in
* Sleep for a few seconds and keep repeating

#### When a message is received: 

* If it's a color update: 
    - Save the new current color. 
    - Next time the clock or spotify display updates, it changes the labels to the new color. 
* If it's a display update: 
    - Call either `set_display_clock` or `set_display_spotify`
* If it's a Spotify update: 
    - Parse out the title and the artist
    - Update the artist and title labels with the new info

# The Future

As I always say, I build to think. Playing around with technology helps me to think about the possibilities. Some ideas 
that have come up: 

* Well, of course, making the code nicer and designed to more easily add new displays. 
* Add a "Timer" feature
   *  In the short term, a clock count-down
   *  In the longer term, an hour-glass timer.
   *  In the LONG longer term, the clock vs hour-glass depends on the orientation of the display
*  Add in different layouts for different screen orientations
*  Create a fun "screen-saver" display that is really just playing with pixels.
*  Probably a different project, but create a Euchre scorekeeper! 
   *  I'm actually really excited about this one. Definitely want to incorporate this with Alexa for voice control. 
   *  Keep track of current score, current trump, maybe even display card values for the current trump. 


    
# Helpful Links: 

* Adafruit MatrixPortal Library https://circuitpython.readthedocs.io/projects/matrixportal/en/latest/api.html#adafruit-matrixportal-matrixportal
* Adafruit IO MQTT API https://io.adafruit.com/api/docs/mqtt.html#adafruit-io-mqtt-api
* Adafruit MiniMQTT Library https://circuitpython.readthedocs.io/projects/adafruit-circuitpython-minimqtt/en/latest/api.html
* Matrix Portal Scoreboard project https://github.com/seantibor/matrix_portal_scoreboard
* Adafruit Matrix Portal library overview and such https://learn.adafruit.com/adafruit-matrixportal-m4?view=all#circuitpython-ble
* CircuitPython libraries for Matrix Portal M4 https://circuitpython.org/board/matrixportal_m4/
