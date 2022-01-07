from video_to_ascii import video_engine
from aiortc.contrib.media import MediaStreamTrack

class VideoTransformTrack(MediaStreamTrack):
    """
    A video stream track that transforms frames from an another track.
    """

    kind = "video"

    def __init__(self, track):
        super().__init__()
        self.track = track

    async def recv(self):
        frame = await self.track.recv()

        ve = video_engine.VideoEngine("just-ascii")
        ve.render_strategy.render_frame(frame.to_ndarray(format="bgr24"))
        
        return frame
