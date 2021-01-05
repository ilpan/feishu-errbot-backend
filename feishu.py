#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import pprint
import sys

from errbot.core import ErrBot, Identifier
from errbot.backends.base import Person, Room, Message, RoomOccupant
from feishu_sdk import FeishuClient
from feishu_sdk.feishu_server import FeishuServer
from typing import Sequence

from src.async_utils import async_default_response
from src.feishu_bot import FeishuBot
from src.feishu_room_occupant import FeishuRoomOccupant
from src.feishu_person import FeishuPerson
from src.feishu_room import FeishuRoom

log = logging.getLogger(__name__)


class FeishuBackend(ErrBot, FeishuServer):
    def __init__(self, bot_config):
        ErrBot.__init__(self, bot_config)
        identity = bot_config.BOT_IDENTITY
        FeishuServer.__init__(self, identity)
        self.app_id = identity.get("app_id", None)
        self.app_secret = identity.get("app_secret", None)
        if not (self.app_id and self.app_secret):
            log.error("App Id and App Secert must be provided in the BOT_IDENTITY setting in your configuration")
            sys.exit(1)
        self.fc = None  # will be initialized in serve_once

    def serve_once(self):
        self.fc = FeishuClient(app_id=self.app_id, app_secret=self.app_secret)
        self.bot_identifier = FeishuBot(self.fc)
        try:
            self.connect_callback()  # notify that the connection occured
            self.run()
        except KeyboardInterrupt:
            log.info("Interrupt received, shutting down..")
            return True
        except Exception:
            log.exception("Error running feishu server!")
        finally:
            log.debug("Triggering disconnect callback")
            self.disconnect_callback()

    def _message_callback_event_handler(self, event: dict):
        """Callback event handler for the 'message' event"""
        log.debug("Saw an event: %s", pprint.pformat(event))

        msg_type = event.get("msg_type", "")
        if msg_type != "text":
            log.warning("only support 'text' msg_type from now on, got:{msg_type}")
            return
        text = event.get("text_without_at_bot", "").strip()
        chat_type = event.get("chat_type", "").strip()
        msg = Message(text, extras={"feishu_event": event})
        if chat_type == 'private':
            msg.frm = FeishuPerson(self.fc, event.get("open_id"))
            msg.to = self.bot_identifier
        elif chat_type == "group":
            msg.frm = FeishuRoomOccupant(self.fc, event.get("open_id"), event.get("open_chat_id"), self)
            msg.to = FeishuRoom(event.get("open_chat_id"), bot=self)
        else:
            log.error(
                f"unknown chat_type:{chat_type} not in ['private', 'group']")

        self.callback_message(msg)

    # implements/override methos from base.Backend/core.Errbot
    def send_message(self, msg: Message):
        super().send_message(msg)

        if msg.parent:
            msg.extras["root_id"] = self._msg_id_for_message(msg.parent)

        to_humanreadable = "<unknown>"
        to_open_id = None
        to_chat_id = None
        try:
            if msg.is_group:
                to_chat_id = msg.to.chat_id
                to_humanreadable = msg.to.name
            else:
                if isinstance(msg.to, RoomOccupant):
                    to_chat_id = msg.to.room.chat_id
                    to_humanreadable = msg.to.room.name
                else:
                    to_open_id = msg.to.person
                    to_humanreadable = msg.to.fullname

            msgtype = "direct" if msg.is_direct else "channel"
            # chat_id > open_id
            log.debug('Sending %s message to %s (%s).', msgtype, to_humanreadable, to_chat_id or to_open_id)
            body = msg.body
            log.debug('Message size: %d.', len(body))

            async_default_response(self.fc.message_md_send(md=body, open_id=to_open_id, chat_id=to_chat_id, root_id=msg.extras.get("root_id", None)))
            # async_default_response(self.fc.message_text_send(text=body, open_id=to_open_id, chat_id=to_chat_id, root_id=msg.extras.get("root_id", None)))
        except Exception:
            log.exception(f'An exception occurred while trying to send the following message '
                f'to {to_humanreadable}: {msg.body}.')

    def _msg_id_for_message(self, msg: Message):
        return msg.extras["feishu_event"]["open_message_id"]

    def change_presence(self, status: str, message: str) -> None:
        super().change_presence(status=status, message=message)
        pass

    def build_reply(self,
                    msg: Message,
                    text: str = None,
                    private: bool = False,
                    threaded: bool = False):
        response = self.build_message(text)
        response.parent = msg
        response.frm = self.bot_identifier
        if private:
            response.to = msg.frm
        else:
            response.to = msg.frm.room if isinstance(msg.frm, RoomOccupant) else msg.frm
        return response

    def prefix_groupchat_reply(self, message: Message, identifier: Person):
        super().prefix_groupchat_reply(message, identifier)
        message.body = f'@{identifier.nick}: {message.body}'  # nick == fullname

    def build_identifier(self, txt_rep: str) -> Identifier:
        """
        txt_rep: {open_id}:{open_chat_id}:{chat_type}
        """
        # only open_id can be used to identify a unique person
        open_id, open_chat_id, chat_type = self._extract_identifiers_from_str(txt_rep)
        if open_id and chat_type == "private":
            return FeishuPerson(fc=self.fc, open_id=open_id)
        if open_id and open_chat_id and chat_type == "group":
            return FeishuRoomOccupant(fc=self.fc, open_id=open_id, chat_id=open_chat_id, bot=self)
        if open_chat_id:
            return FeishuRoom(chat_id=open_chat_id, bot=self)

        raise Exception(
            "You found a bug. I expected at least one of open_id, open_chat_id, or chat_type "
            "to be resolved but none of them were. This shouldn't happen so, please file a bug."
        )

    @staticmethod
    def _extract_identifiers_from_str(text):
        """
        text: {open_id}:{open_chat_id}:{chat_type}
        """
        exception_message = "invalid identifiers str, except:oc_xxx/oc_xxx/[private|group]"
        text = text.strip()
        if not text:
            raise ValueError(exception_message)

        open_id = None
        open_chat_id = None
        chat_type = "private"
        chat_types = ["private", "group"]
        items = text.split(":")
        for item in items:
            item_ = item.strip()
            if item_.startswith("ou_"):
                open_id = item_
            elif item_.startswith("oc_"):
                open_chat_id = item_
            elif item_ in chat_types:
                chat_type = item_
            else:
                raise ValueError(exception_message)
        return open_id, open_chat_id, chat_type

    def query_room(self, room: str) -> Room:
        pass

    @property
    def mode(self):
        return "feishu"

    @property
    def rooms(self) -> Sequence[Room]:
        # just return <=100 rooms
        chat_list_resp = async_default_response(self.fc.chat_list())
        chat_groups = chat_list_resp.data.get("groups", None)
        return [FeishuRoom(chat_id=group["chat_id"], bot=self) for group in chat_groups] if chat_groups else []
