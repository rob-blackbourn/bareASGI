from typing import Mapping, Any
from asyncio.queues import Queue


class MockIO:

    def __init__(self) -> None:
        self._write_queue = Queue()
        self._read_queue = Queue()


    async def write(self, message: Mapping[str, Any]) -> None:
        await self._write_queue.put(message)


    async def read(self) -> Mapping[str, Any]:
        return await self._read_queue.get()


    async def send(self, message: Mapping[str, Any]) -> None:
        await self._read_queue.put(message)


    async def receive(self) -> Mapping[str, any]:
        return await self._write_queue.get()
