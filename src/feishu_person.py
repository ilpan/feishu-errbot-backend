#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

from errbot.backends.base import Person
from feishu_sdk import FeishuClient

from src.async_utils import async_default_response

log = logging.getLogger(__name__)


class FeishuPerson(Person):
    def __init__(self, fc: FeishuClient, open_id: str):
        self._fc = fc
        self._open_id = open_id

    @property
    def open_id(self):
        return self._open_id

    @property
    def client(self):
        return "feishu"

    @property
    def fullname(self):
        user = self.user_get(self._open_id)
        if not user:
            log.error(f"Can't get user with open_id:{self._open_id}")
            return f"<{self._open_id}>"
        return user["name"]

    def user_get(self, open_id):
        users_resp = async_default_response(self._fc.user_batch_get([open_id]))
        user_infos = users_resp.data.get("user_infos", None)
        return user_infos[0] if user_infos else None

    person = open_id
    aclattr = open_id
    nick = fullname

    def __unicode__(self):
        return f"{self.open_id}"

    def __str__(self):
        return self.__unicode__()

    def __eq__(self, other):
        if not isinstance(other, FeishuPerson):
            log.warning(
                f"tried to compare a FeishuPerson with a {type(other)}")
            return False
        return other.open_id == self.open_id

    def __hash__(self):
        return self.open_id.__hash__()
