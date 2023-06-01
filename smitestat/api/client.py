from os import environ
from hashlib import md5

import aiohttp
import pendulum


# TODO: add a reminder or something if these keyerror
# DEV_ID = environ["HIREZ_devid"]
# AUTH_KEY = environ["HIREZ_authkey"]

DEV_ID = "1004"
AUTH_KEY = "23DF3C7E9BD14D84BF892AD206B6755C"

BASE_URL = "https://api.smitegame.com/smiteapi.svc"

class Client:
    def __init__(self):
        self.hirez_session: str | None = None

    @staticmethod
    def get_timestamp() -> str:
        now = pendulum.now("UTC")
        return now.strftime("%Y%m%d%H%M%S")

    @staticmethod
    def get_signature(method_name: str, timestamp: str):
        signature = DEV_ID + method_name + timestamp + AUTH_KEY
        return md5(signature.encode()).hexdigest()

    async def request(self, method_name: str):
        pass

    async def create_session(self):
        async with aiohttp.ClientSession() as session:
            timestamp = self.get_timestamp()
            signature = self.get_signature("createsession", timestamp)
            print(signature, f"/createsessionJson/{DEV_ID}/{signature}/{timestamp}")
            async with session.get(BASE_URL + f"/createsessionJson/{DEV_ID}/{signature}/{timestamp}") as response:
                response.raise_for_status()
                return await response.json()

    async def ping(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(BASE_URL + "/pingJson") as response:
                return await response.json()


if __name__ == "__main__":
    import asyncio

    async def _main():
        client = Client()
        print(await client.create_session())

    asyncio.run(_main())
