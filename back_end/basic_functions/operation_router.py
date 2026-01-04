import logging
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Literal

from .playlist_operation import get_playlist_songs_information, get_playlist_collect_information
from .search_operation import get_searh_information

logger = logging.getLogger("basic_functions")

class PlaylistsCollect(BaseModel):
    user_id: str
    playlist_id: str
    action: Literal['collect', 'uncollect']

# /
router = APIRouter()

@router.get("/songslists/{playlist_id}/{user_id}")
async def get_playlist_songs(playlist_id: str | int, user_id: str | int):
    data = await get_playlist_songs_information(playlist_id, user_id)
    logger.info(f"歌单-歌曲{playlist_id}信息已发送[get_playlist_songs]")
    return data

@router.post("/playlists/collect")
async def post_playlists_collect(information: PlaylistsCollect):
    input_information = information.model_dump()
    data = await get_playlist_collect_information(input_information)
    logger.info(f"歌单信息{information['playlist_id']}已发送[post_playlists_collect]")
    return data

@router.get("/playlists/is_collected/{playlist_id}/{user_id}")
async def get_playlists_is_collected(playlist_id: str | int, user_id: str | int):
    data = await (playlist_id, user_id)
    logger.info(f"歌单{playlist_id}信息已发送[get_playlist_is_collected]")
    return data


