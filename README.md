# Experimental app clivrt
CLI app to display video real-time. 
## How to use this
```bash
python3 -m pip install aiortc opencv-python git+https://github.com/collabinator/video-to-ascii.git
python3 clivrt.py answer

# Then call the cli user from the browser
# Eventually we'll want to do some offer workflows too (python3 clivrt.py offer)
```

## CLI reference
TBD

## For Developers and Architects

### About WebRTC
This app utilizes WebRTC. [From mozilla](https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API/Signaling_and_video_calling): "WebRTC is a fully peer-to-peer technology for the real-time exchange of audio, video, and data, with one central caveat. A form of discovery and media format negotiation must take place, as discussed elsewhere, in order for two devices on different networks to locate one another. This process is called signaling and involves both devices connecting to a third, mutually agreed-upon server. Through this third server, the two devices can locate one another, and exchange negotiation messages."

The main reasons WebRTC was picked for this are:
1. peer-to-peer means we get great performance, not needing to send video through a server
2. it's an open standard with [W3C and IETF](https://www.w3.org/2021/01/pressrelease-webrtc-rec.html.en)

### Building the Code
TBD

### Contributing
TBD

## Some other interesting things
- The architecture design [lives here in Miro](https://miro.com/app/board/uXjVOZLd2gQ=/)