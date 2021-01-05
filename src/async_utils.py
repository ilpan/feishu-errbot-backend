#!/usr/bin/env python
# -*- coding: utf-8 -*-

import nest_asyncio

from asyncio import AbstractEventLoop, new_event_loop
from feishu_sdk.feishu_response import FeishuResponse
from typing import TypeVar, Awaitable

nest_asyncio.apply()

_T = TypeVar("_T")


def async_loop() -> AbstractEventLoop:
    return new_event_loop()


def async_default_response(coro: Awaitable[FeishuResponse]):
    return async_feishu_response(async_loop(), coro)


def async_feishu_response(loop: AbstractEventLoop,
                          coro: Awaitable[FeishuResponse]) -> FeishuResponse:
    return async_result(loop, coro)


def async_result(loop: AbstractEventLoop, coro) -> _T:
    task = loop.create_task(coro)
    loop.run_until_complete(task)
    return task.result()
