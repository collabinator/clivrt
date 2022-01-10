FROM registry.access.redhat.com/ubi8/python-39:1-24

USER root

RUN pip3 install aiortc opencv-python prodict websockets git+https://github.com/collabinator/video-to-ascii.git \
    && yum install -y mesa-libGL

USER 1001