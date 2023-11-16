# monitorthief
Paper Link: Not yet announced <p>
Collect the channel state information (CSI) and analyze the wifi6 signal waveform to  monitor whether the thief is near or far away the Receiver<p>
* number of classes: 3
* classes: TR , RT, No-person (empty)

## Experimental Environment
* Two PC with Intel AX200 NIC (2Rx X 2Tx)
* Ubuntu 20.04
* collect the 5.18 GHz to 5.2 GHz , 802.11ax HE PHY
* 12.5 seconds for each action

## Explanation of Terms
* TR stands for the direction from TX to RX.
* RT stands for the direction from RX to TX.
  
## CSI tool
PicoScenes <p>
link: https://ps.zpj.io/index.html

## Code Reference
UT-HAR <p>
link: https://github.com/ermongroup/Wifi_Activity_Recognition
* number of classes : 7
* classes : lie down, fall, walk, pickup, run, sit down, stand up
