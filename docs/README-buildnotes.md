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

## On missing OS dependencies
You might get some errors due to missing OS packages, here are some that have been seen:

1. ImportError: libGL.so.1: cannot open shared object file: No such file or directory

      > `apt-get install ffmpeg libsm6 libxext6  -y`

## Building on a Jetson Nano (arm64)
I've been experimenting with building this on a [NVIDIA Jetson Nano](https://developer.nvidia.com/embedded/jetson-nano-developer-kit). Here are some extra steps you'll need to take to get that going.
(Note: I'm not sure these are the *best* way to get it working, but it *is* what I did)


* Setup Python 3.8
```
sudo apt-get install python3-pip python3.8 python3.8-dev
sudo update-alternatives --install /usr/bin/python python /usr/bin/python3 1
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.8 2
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.6 3
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

There seems to be an issue on the jetson with a mismatch in dependencies with NVIDIA's ffmpeg and pyAv - [more details here](https://github.com/PyAV-Org/PyAV/issues/619), looks like I might need to build ffmpeg from source. The challenge will be to ensure I can still leverage any patches/build options NVIDIA added for leveraging their hardware performance.
```
sudo apt-get install libopus-dev libvpx-dev
```

* Build container - this is TBD but using these links might help
  * https://github.com/dusty-nv/jetson-containers#pre-built-container-images
  * https://github.com/NVIDIA/nvidia-docker/wiki/NVIDIA-Container-Runtime-on-Jetson


* Hardware support
The Jetson is a edge device with low computing capabilities - so using the dedicated hardware efficiently is important. If everything just uses CPU then we are doing it wrong. Using software libraries that can leverage the HW is important (encoding and decoding video). Initial research shows ffmpeg available for the Jetson might not support HW enc/dec - also H.264 might be required vs. other formats. See here for discussion/alternatives: 
  * https://forums.developer.nvidia.com/t/webrtc-low-performances-with-nvidia-encoder/115324
  * https://docs.nvidia.com/jetson/l4t/index.html#page/Tegra%20Linux%20Driver%20Package%20Development%20Guide/hardware_acceleration_in_webrtc.html#wwpID0E0OB0HA
