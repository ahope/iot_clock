
# IoT Spotify Clock

This project was based on AdaBox 016-- a 64x32 RGB LED Matrix, with the MatrixPortal M4 board. The board is CircuitPython friendly, but can also be used with the Arduino IDE for lower-level programming. 

It's easy to get projects up and running with the code and instructions provided by Adafruit, but I'm more interested in learning how to push my understanding than just getting a project up and running. 

My goal with this project was to give me a field to explore and learn. I tried pushing the project in a number of ways, just to see what could be done, what was easy, what was hard. 


## Things to do

- [x] Scroll the Spotify Display
- [ ] Clean up the code
- [ ] Modify MQTT to keep a list of messages, showing one at a time. 
- [ ] Add error checking for values from MQTT
- [ ] Publish the Alexa skill for voice control
    - [ ] Add capabilities to Alexa for: 
        - [ ]  Changing the display
    - [ ] Make sure values match between Alexa and the 
- [ ] The IFTTT applet for Spotify is polling, which means it updates ~once per hour. That's all well and fine, but it's not quite timely, and when it does update, it updates a bunch of songs all at once. Investigate other options. 
    - [ ] Zapier
    - [ ] Custom-built Spotify updater (Lambda?)



### First pass

The clock was up and running fairly quickly. The hard part was figuring out how to connect to Spotify. After adding in some sample code to test the network connection and understand the request library, I realized that we can't do user authorization for Spotify because there is no UI/redirect URL. I *was* going consider utilizing MQTT as a second phase/upgrade, but I won't be able to get the access token via the ESP. 

### Second pass (PLAN)

Set up the matrix to utilize MQTT. The easy peasy first here: get the matrix subscribing to the MQTT broker. Set up IFTTT to listen to my Spotify listening, and publish to the broker. Then, the display updates. 

Done! Also set up a channel to change the color of the display, and to display when the security system is set to "Home" status. 

### Third pass

Now I've got a display with a clock and some messages providing info about Spotify and the alarm system. 

I want to add in the weather display. Adafruit has a cool weather display. I started by copying and pasting the relevant code into the same code file. 

#### Challenge 1: Different Projects using Different Classes/Constructs

The Clock and Scoreboard implementations use MatrixPortal for graphics, while hte Weather used the lower level Matrix class for graphics. Took me a little while to figure out the relationship between all of them. I understood the theoretical relationship from the diagram on the library overview page, but I had to dig into the source code to really understand. But, once I did that it was obvious and easy. 

Thus, I got the weather part of the app running too. 

#### Challenge 2: Memory!!! 

Finally! I shoved enough on the board and was sloppy enough with the planning that we ran out of memory! I knew this would happen, but wasn't quite sure when. So, now that we've got all the pieces, time to organize it so we can swap things out rather than keep in memory all the time. 

### Finalizing

I'm having tons of ideas for now, and just want something working with loose ends tied up. So I'm not going to debug the complex weather thing, I'm just going to make what I have work by cleaning it up. 

That means I end up with: 

* 2 Displays: One for Spotify, one for the clock
* 3 data sources: 
    - Display: which thing to display
    - color: which color to show things in
    - spotify: the messages coming from MQTT/IFTTT




# Debugging

I started thinking about how I go about debugging this project. There are a few options: 

* Software Profiling
* Hardware Profiling via a GPIO pin and an oscilloscop
* SWD-- ARM's version of JTAG. 

## Software Profiling

This is the embedded version of ```printf```. Write a ```profile``` function that stores some info about what is happening when into an array. For every function you want to profile, call the ```profile``` function when it gets called. When the array is full, stop running and dump out the data to be analyzed.

* This is a great way to see how long it takes a function to run, as well as how many times it's called. 
* It could be really fun to pull this up in R or a Jupyter notebook and visualize the data over time. Not sure it's worth it though! 
* This isn't really non-intrusive profiling. It takes space, and so won't be helpful to help debug memory issues. 
* This approach is easy to turn profiling on/off without having to touch many lines of code. 

## Hardware Profiling

In this case, we use one of the GPIO pins on the board. For every function we want to profile, turn the GPIO pin on at the start of the function, and off when the function is over. Then, we read the voltage on that IO pin, and pull the stats from that. 

* We can use a different IO pin for different functions, and that could help isolate the profile channels. 
* We need a way to read the data on that pin. The easiest is probably with an oscilloscope. Then, the features of your oscilloscope limit what you can do with the data. Some oscilloscopes can read multiple channels at a time; some oscilloscopes can record traces. I know my oscilloscope is at school, so while I love the idea of this approach, it's not always the most available. 

## SWD: Serial Wire Debug

This is a feature available on ARM chips. It provides a serial interface to the board for debugging. It's like JTAG, but instead of requiring 4 wires, it only requires 2, so it's less complex on the board. 

I've got a bit to figure out here, but one upside is that there *is* a Python library [https://github.com/pfalcon/PySWD] that likely helps. 




# Helpful Links: 

* Adafruit MatrixPortal Library https://circuitpython.readthedocs.io/projects/matrixportal/en/latest/api.html#adafruit-matrixportal-matrixportal
* Adafruit IO MQTT API https://io.adafruit.com/api/docs/mqtt.html#adafruit-io-mqtt-api
* Adafruit MiniMQTT Library https://circuitpython.readthedocs.io/projects/adafruit-circuitpython-minimqtt/en/latest/api.html
* Matrix Portal Scoreboard project https://github.com/seantibor/matrix_portal_scoreboard
* Adafruit Matrix Portal library overview and such https://learn.adafruit.com/adafruit-matrixportal-m4?view=all#circuitpython-ble
* CircuitPython libraries for Matrix Portal M4 https://circuitpython.org/board/matrixportal_m4/
* 
