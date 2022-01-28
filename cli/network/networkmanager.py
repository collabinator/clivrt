import logging
import asyncio
import json
import aiohttp
from datetime import datetime
from attrs import define
from aiortc.sdp import candidate_from_sdp
import websockets
from cli.datamodel.session import Session

@define
class NetworkManager:
    session: Session

