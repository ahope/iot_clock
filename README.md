
# IoT Spotify Clock

### First pass

The clock was up and running fairly quickly. The hard part was figuring out how to connect to Spotify. After adding in some sample code to test the network connection and understand the request library, I realized that we can't do user authorization for Spotify because there is no UI/redirect URL. I *was* going consider utilizing MQTT as a second phase/upgrade, but I won't be able to get the access token via the ESP. 

### Second pass (PLAN)

Set up the matrix to utilize MQTT. The easy peasy first here: get the matrix subscribing to the MQTT broker. Set up IFTTT to listen to my Spotify listening, and publish to the broker. Then, the display updates. 

