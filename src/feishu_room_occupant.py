#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

from errbot.backends.base import RoomOccupant
from feishu_sdk.feishu_client import FeishuClient

from src.feishu_person import FeishuPerson

log = logging.getLogger(__name__)


class FeishuRoomOccupant(RoomOccupant, FeishuPerson):
    def __init__(self, fc: FeishuClient, open_id: str, chat_id: str, bot):
        super().__init__(fc, open_id)
        from src.feishu_room import FeishuRoom
        self._room = FeishuRoom(chat_id=chat_id, bot=bot)

    @property
    def room(self):
        return self._room

    def __unicode__(self):
        return f'{self._open_id}:{self._room.chat_id}:group'

    def __str__(self):
        return self.__unicode__()

    def __eq__(self, other):
        if not isinstance(other, RoomOccupant):
            log.warning(
                'tried to compare a FeishuRoomOccupant with a FeishuPerson %s vs %s',
                self, other)
            return False
        return other.room.chat_id == self.room.chat_id and other.open_id == self.open_id