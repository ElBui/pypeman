import json
import asyncio
import functools
from concurrent.futures import ThreadPoolExecutor
from .channels import Acknowledge, Nacknowledge

loop = asyncio.get_event_loop()



class BaseNode:

    def __init__(self, *args, **kwargs):
        self.blocking = kwargs.pop('blocking', True)
        self.immediate_ack = kwargs.pop('immediate_ack', False)

    @asyncio.coroutine
    def handle(self, msg):
        if not self.blocking:
            asyncio.async(asyncio.coroutine(self.process)(msg))

            if self.immediate_ack:
                raise Acknowledge()

            result = msg
        else:
            result = yield from asyncio.coroutine(self.process)(msg)

        return result

    def process(self, msg):
        return msg


class Log(BaseNode):
    def process(self, msg):
        print(msg.payload)
        return msg


class AcknowledgeNode(BaseNode):
    pass


class JsonToPython(BaseNode):
    def process(self, msg):
        msg.payload = json.loads(msg.payload)
        msg.content_type = 'application/python'
        return msg


class PythonToJson(BaseNode):
    def process(self, msg):
        msg.payload = json.dumps(msg.payload)
        msg.content_type = 'application/json'
        return msg


class Add1(BaseNode):
    def process(self, msg):
        msg.payload['sample'] += 1
        return msg


class ThreadNode(BaseNode):
    # Todo create class ThreadPool

    @asyncio.coroutine
    def handle(self, msg):
        with ThreadPoolExecutor(max_workers=1) as executor:
            result = yield from loop.run_in_executor(executor, self.process, msg)
            return result
