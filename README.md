# clivrt
CLI app to do video calls but from the terminal. Just fun little project that let's you chat with friends in a retro kidna way - while staying in your CLI. 

![Screenshot](docs/clivrtsmilethumbsup.png?raw=true)

## How to use this
TBD

## CLI reference
TBD

### Config File
If file is is located in the same folder as the cli executable and named `.clivrt`, it will be used for default config. Here's an example:
```
[DEFAULT]
signalinghosturl = wss://signaling-s-dudash-dev.apps.sandbox.x8i5.p1.openshiftapps.com
autoanswer = true
loglevel = WARN
videostyle = just-ascii
webcam = /dev/video0
framerate = 30
video_size = 800x600
```
* signalinghosturl = Which server to connect to for finding/connecting/chatting with peers (note once a peer connection is established this is no longer required for video chat). Must begin with ws:// or wss://
* loglevel = [INFO, DEBUG, WARN, ERROR, CRITICAL] how much log data to display
* videostyle = [just-ascii, ascii-color, filled-ascii]
* webcam = Path to your webcam. Some examples: [linux: /dev/video0, windows: video=Integrated Camera, mac: default:none]
* framerate = outgoing video framerate
* video_size = outgoing video resolution

## For Developers and Architects

### About WebRTC
This app utilizes WebRTC. [From mozilla](https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API/Signaling_and_video_calling): "WebRTC is a fully peer-to-peer technology for the real-time exchange of audio, video, and data, with one central caveat. A form of discovery and media format negotiation must take place, as discussed elsewhere, in order for two devices on different networks to locate one another. This process is called signaling and involves both devices connecting to a third, mutually agreed-upon server. Through this third server, the two devices can locate one another, and exchange negotiation messages."

The main reasons WebRTC was picked for this are:
1. peer-to-peer means we get great performance, not needing to send video through a server
2. it's an open standard with [W3C and IETF](https://www.w3.org/2021/01/pressrelease-webrtc-rec.html.en)

### Building the Code
The supported platform is currently just linux. If you're on windows you can use WSL.
This project uses pipenv for dependency management.

[even more info here](./docs/README-buildnotes.md)

### Contributing
TBD

## Built Upon
This project uses the awesome open source work from many other folks. There are a few key projects this wouldn't be possible without:
* [aiortc](https://github.com/aiortc/aiortc), a simple readable python library for WebRTC and ORTC
* [video_to_ascii](https://github.com/joelibaceta/video-to-ascii), simple python package to play videos in the terminal using characters as pixels
* [prompt_toolkit](https://python-prompt-toolkit.readthedocs.io/en/master/index.html), a library for building powerful interactive command line apps

## Some other interesting things
- The architecture design [lives here in Miro](https://miro.com/app/board/uXjVOZLd2gQ=/)
- Concurrency in Python [a good reference here](https://realpython.com/python-concurrency/#what-is-concurrency)