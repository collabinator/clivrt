
from video_to_ascii import video_engine
from aiortc.contrib.media import MediaStreamTrack
import sys

PLATFORM = 0
if sys.platform != 'win32': PLATFORM = 1

class VideoTransformTrack(MediaStreamTrack):
    """
    A video stream track that transforms frames from an another track.
    """

    kind = "video"
    ve = None

    def __init__(self, track):
        super().__init__()
        self.track = track
        if PLATFORM: sys.stdout.write("echo -en '\033[2J' \n")
        else: sys.stdout.write('\033[2J')
        self.ve = video_engine.VideoEngine()

    async def recv(self):
        frame = await self.track.recv()
        # TODO into correct frame when we update prompt
        # currently each strategy does  sys.stdout.write(msg)
        await self.ve.render_strategy.render_frame(frame.to_ndarray(format="bgr24")) # why dont we use render()?
        return frame