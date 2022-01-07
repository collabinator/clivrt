import argparse
import asyncio
import json
import logging
from datetime import datetime
from aiortc.sdp import candidate_from_sdp

from signaling import quarkus
from media import ascii

from prodict import Prodict

from aiortc import (
    RTCPeerConnection,
)
from aiortc.contrib.media import MediaBlackhole, MediaPlayer, MediaRecorder, MediaRelay
from aiortc.contrib.signaling import BYE, object_to_string

relay = MediaRelay()

async def run(pc, player, recorder, signaling, role):
    def add_tracks():
        if player and player.audio:
            pc.addTrack(player.audio)

        # TODO: Add my webcam stream here

    @pc.on("track")
    def on_track(track):
        print("Receiving %s" % track.kind)
        if track.kind == 'video':
            recorder.addTrack(ascii.VideoTransformTrack(
                relay.subscribe(track)
            ))
        # TODO: play audio

    # connect signaling
    await signaling._connect()

    if role == "offer":
        # send offer
        add_tracks()
        await pc.setLocalDescription(await pc.createOffer())
        msg_data = {
            'sdp': json.loads(object_to_string(pc.localDescription)),
            'target': 'jason', # TODO: figure out a way to make this dynamic
            'type': 'video-ofer',
            'name': 'cli', # TODO: grab this from args
            'date': str(datetime.now())
        }
        await signaling.send(json.dumps(msg_data))

    # consume signaling
    while True:
        message = await signaling.receive()
        msg_obj = Prodict.from_dict(json.loads(message))

        if msg_obj['type'] == 'video-offer' or msg_obj['type'] == 'video-answer':
            await pc.setRemoteDescription(msg_obj['sdp'])
            await recorder.start()

            if msg_obj['type'] == 'video-offer':
                # send answer
                add_tracks()
                await pc.setLocalDescription(await pc.createAnswer())
                msg_data = {
                    'sdp': json.loads(object_to_string(pc.localDescription)),
                    'target': msg_obj['name'],
                    'type': 'video-answer',
                    'name': 'cli', # TODO: grab this from args
                    'date': str(datetime.now())
                }
                await signaling.send(json.dumps(msg_data))
        elif msg_obj['type'] == 'new-ice-candidate':
            candidate = candidate_from_sdp(msg_obj["candidate"]["candidate"].split(":", 1)[1])
            candidate.sdpMid = msg_obj["candidate"]["sdpMid"]
            candidate.sdpMLineIndex = msg_obj["candidate"]["sdpMLineIndex"]
            await pc.addIceCandidate(candidate)
        else:
            print(message)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Video stream from the command line")
    parser.add_argument("role", choices=["offer", "answer"])
    parser.add_argument("--play-from", help="Read the media from a file and sent it."),
    parser.add_argument("--record-to", help="Write received media to a file."),
    parser.add_argument("--verbose", "-v", action="count")
    args = parser.parse_args()

    # TODO: Parameterize these vv
    args.signaling_protocol = 'ws'
    args.signaling_host = 'localhost'
    args.signaling_port = '8080'
    args.username = 'cli'

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)

    # create signaling and peer connection
    signaling = quarkus.QuarkusSocketSignaling(args.signaling_protocol, args.signaling_host, args.signaling_port, args.username)
    pc = RTCPeerConnection()
    # TODO: Add STUN Servers to pc

    # create media source
    # TODO: Remove if necessary. Maybe get webcam here?
    if args.play_from:
        player = MediaPlayer(args.play_from)
    else:
        player = None

    # create media sink
    if args.record_to:
        recorder = MediaRecorder(args.record_to) # TODO: Maybe discard this?
    else:
        recorder = MediaBlackhole()

    # run event loop
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(
            run(
                pc=pc,
                player=player,
                recorder=recorder,
                signaling=signaling,
                role=args.role,
            )
        )
    except KeyboardInterrupt:
        pass
    finally:
        # cleanup
        loop.run_until_complete(recorder.stop())
        loop.run_until_complete(signaling.close())
        loop.run_until_complete(pc.close())
