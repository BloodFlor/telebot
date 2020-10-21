import re
import ssl
import nltk
import praw
import json
import urllib
import random
import asyncio
import aiohttp
import requests
import sys, time
from aiohttp import web

class Api(object):
    URL = 'https://api.telegram.org/bot%s/%s'

    def __init__(self, token, loop):
        self._token = token
        self._loop = loop

    async def _request(self, method, message):
        headers = {
            'Content-Type': 'application/json'
        }
        async with aiohttp.ClientSession(loop=self._loop) as session:
            async with session.post(self.URL % (self._token, method),
                                    data=json.dumps(message),
                                    headers=headers) as resp:
                try:
                    assert resp.status == 200
                except:
                    pass

    async def sendMessage(self, chatId, text):
        message = {
            'chat_id': chatId,
            'text': text
        }
        await self._request('sendMessage', message)

    async def sendPhoto(self, chatId, text, media):
        message = {
            'chat_id': chatId,
            'photo': media,
            'caption': text
        }
        await self._request('sendPhoto', message)


class Conversation(Api):
    def __init__(self, token, loop):
        super().__init__(token, loop)

    async def _handler(self, message):
        pass

    async def handler(self, request):
        message = await request.json()
        asyncio.ensure_future(self._handler(message))
        return aiohttp.web.Response(status=200)
