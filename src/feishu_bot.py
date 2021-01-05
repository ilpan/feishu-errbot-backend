#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

from feishu_sdk.feishu_client import FeishuClient

from src.async_utils import async_default_response
from src.feishu_person import FeishuPerson

log = logging.getLogger(__name__)


class FeishuBot(FeishuPerson):
    def __init__(self,
                 fc: FeishuClient,
                 open_id: str = None,
                 app_name: str = None):
        self._fc = fc
        if not (open_id and app_name):
            bot = self.bot_get()
            if not bot:
                raise RuntimeError(
                    "can't get bot info, please check your app_id && app_secret, and ensure your robot ability"
                )
            open_id = bot["open_id"]
            app_name = bot["app_name"]
        super().__init__(fc=fc, open_id=open_id)
        self._app_name = app_name

    @property
    def fullname(self):
        return self._app_name

    def bot_get(self):
        bot_resp = async_default_response(self._fc.bot_info())
        return bot_resp.data.get("bot", None)
