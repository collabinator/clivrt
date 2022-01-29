# clivrt
CLI app to do video calls but from the terminal. Just fun little project that let's you chat with friends in a retro kidna way - while staying in your CLI. 
## How to use this
TBD

## CLI reference
TBD

## For Developers and Architects

### About WebRTC
This app utilizes WebRTC. [From mozilla](https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API/Signaling_and_video_calling): "WebRTC is a fully peer-to-peer technology for the real-time exchange of audio, video, and data, with one central caveat. A form of discovery and media format negotiation must take place, as discussed elsewhere, in order for two devices on different networks to locate one another. This process is called signaling and involves both devices connecting to a third, mutually agreed-upon server. Through this third server, the two devices can locate one another, and exchange negotiation messages."

The main reasons WebRTC was picked for this are:
1. peer-to-peer means we get great performance, not needing to send video through a server
2. it's an open standard with [W3C and IETF](https://www.w3.org/2021/01/pressrelease-webrtc-rec.html.en)

### Building the Code
The supported platform is currently just linux. If you're on windows you can use WSL.
This project uses pipenv for dependency management.

### Contributing
TBD

## Some other interesting things
- The architecture design [lives here in Miro](https://miro.com/app/board/uXjVOZLd2gQ=/)
- Concurrency in Python [a good reference here](https://realpython.com/python-concurrency/#what-is-concurrency)