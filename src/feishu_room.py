#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

from errbot.backends.base import Room

from src.async_utils import async_default_response
from src.feishu_room_occupant import FeishuRoomOccupant

log = logging.getLogger(__name__)


class FeishuRoom(Room):
    def __init__(self, chat_id: str = None, name: str = None, bot=None):
        self._chat_id = chat_id
        self._name = name
        self._bot = bot
        self.fc = bot.fc

        if self._chat_id:
            self._name = self._chat_info["name"]

    @property
    def chat_id(self):
        return self._chat_id

    @property
    def name(self):
        return self._name

    @property
    def _chat_info(self):
        chat_info_resp = async_default_response(self.fc.chat_info(
            self.chat_id))
        return chat_info_resp["data"]

    def __str__(self):
        return self._chat_id

    def join(self, username=None, password=None):
        pass

    def leave(self, reason=None):
        pass

    def create(self):
        pass

    def destroy(self):
        resp = async_default_response(self.fc.chat_disband(self.chat_id))
        log.info(f"room destroy resp: {resp}")

    def invite(self, *args):
        open_ids = [open_id for open_id in args]
        resp = async_default_response(
            self.fc.chat_chatter_add(self.chat_id, open_ids))
        log.info(f"room invite resp: {resp}")

    @property
    def exists(self):
        pass

    @property
    def joined(self):
        pass

    @property
    def topic(self):
        return self.name

    @topic.setter
    def topic(self, topic):
        resp = async_default_response(self.fc.chat_update(self.chat_id, topic))
        log.info(f"room update topic resp: {resp}")

    @property
    def occupants(self):
        members = self._chat_info["members"]
        return [
            FeishuRoomOccupant(self.fc, m["open_id"], self.chat_id, self._bot)
            for m in members
        ]
