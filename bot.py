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
from lib.nlu import NLU
from lib.daemon import Daemon
from lib.get_mem import GetMem
from lib.bot_config import TOKEN
from lib.api_bot import Conversation

myNLU = NLU()
myNLU.get_dataset()

class MyDaemon(Daemon):
    def run(self):
        loop = asyncio.get_event_loop()
        try:
            app = loop.run_until_complete(init_app(loop))
            context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
            context.load_cert_chain("cert/fullchain.pem", "cert/privkey.pem")
            web.run_app(app, host='192.168.1.2', port='88', ssl_context=context)
        except Exception as e:
            print('Error create server: %r' % e)
        finally:
            pass
        loop.close()

async def send_answer(self, message):
    try:
        if 'message' in message:
            if 'chat' in message['message'] and 'text' in message['message']:
                if not {'мем', 'mem','/мем', '/mem'}.isdisjoint(message['message']['text'].lower().split(' ')):
                    post = GetMem(message['message']['text'])
                    if post:
                        await self.sendPhoto(message['message']['chat']['id'], post[0], post[1])
                    else:
                        await self.sendMessage(message['message']['chat']['id'], "Мемы закончились")
                else:
                    await self.sendMessage(message['message']['chat']['id'], #474883644
                                            myNLU.get_answer(message['message']['text']))
    except:
        pass

class EchoConversation(Conversation):
    def __init__(self, token, loop):
        super().__init__(token, loop)

    async def _handler(self, message):
        await send_answer(self, message)

async def init_app(loop):
    app = web.Application(loop=loop, middlewares=[])
    echobot = EchoConversation(TOKEN, loop)
    app.router.add_post('/{}/api/v1'.format(TOKEN), echobot.handler)
    return app

if __name__ == '__main__':
    daemon = MyDaemon('tmp/daemon-example.pid')
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            daemon.start()
        elif 'stop' == sys.argv[1]:
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            daemon.restart()
        else:
            print("Unknown command")
            sys.exit(2)
        sys.exit(0)
    else:
        print("usage: %s start|stop|restart" % sys.argv[0])
        sys.exit(2)
