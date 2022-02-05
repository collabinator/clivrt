# Build Notes
Some random notes on building - this is all in progess and subject to change

## About requirements.txt
We don't really use this anymore - switched to Pipfile. Keeping it here for posterity by running:
`pipenv lock -r > requirements.txt`

## Manually creating a release
2022-02-03: There were a bunch of odd errors using pyinstaller which look like bug with the latest release. For now I have switched to using the dev release, which you can see in the Pipfile (`pyinstaller = {file = "https://github.com/pyinstaller/pyinstaller/archive/develop.zip"}`)

The way to create a release:
`pyinstaller --add-data .clivrt:. --onefile clivrt.py`

Which dumps clivrt into `./dist/clivrt`

## Building on a Jetson Nano (arm64)
I've been experimenting with building this on a [NVIDIA Jetson Nano](https://developer.nvidia.com/embedded/jetson-nano-developer-kit). Here are some extra steps you'll need to take to get that going.
(Note: I'm not sure these are the *best* way to get it working, but it *is* what I did)


* Setup Python 3.8
```
sudo apt-get install python3-pip python3.8 python3.8-dev
sudo update-alternatives --install /usr/bin/python python /usr/bin/python3 1
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.8 2
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.6 1
sudo update-alternatives --config python3
sudo pip3 install pipenv
```
* Install newer ffmpeg > 4.2+ ([from notes here](https://forums.developer.nvidia.com/t/hardware-accelerated-video-playback-with-l4t-ffmpeg/154019))
```
echo "deb https://repo.download.nvidia.com/jetson/ffmpeg main main" |  sudo tee -a /etc/apt/sources.list
echo "deb-src https://repo.download.nvidia.com/jetson/ffmpeg main main" |  sudo tee -a /etc/apt/sources.list
sudo apt update
```

* Install dependencies for aiortc
```
sudo apt-get install libopus-dev libvpx-dev
```

