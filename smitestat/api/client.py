from enum import Enum
from os import environ
from hashlib import md5

import aiohttp
import pendulum

# TODO: see what happens when we go over the request cap

# TODO: add a reminder or something if these keyerror
DEV_ID = environ["HIREZ_devid"]
AUTH_KEY = environ["HIREZ_authkey"]

# enables saving session id to file for testing
DEBUG = True

BASE_URL = "https://api.smitegame.com/smiteapi.svc"


# TODO: what are the challenge modes?
class SmiteQueue(Enum):
    conquest = 426
    arena = 435
    assault = 445
    joust = 448
    ranked_conquest = 451
    slash = 10189
    ranked_joust = 450
    ranked_duel = 440


LISTENED_QUEUES = list(SmiteQueue)


class Client:
    def __init__(self):
        if DEBUG:
            try:
                with open("debug_sessionid.txt") as fp:
                    self.hirez_session_id = fp.read()
            except FileNotFoundError:
                self.hirez_session_id = None
        else:
            self.hirez_session_id: str | None = None

    @staticmethod
    def get_timestamp() -> str:
        now = pendulum.now("UTC")
        return now.strftime("%Y%m%d%H%M%S")

    @staticmethod
    def get_date(
        when: pendulum.DateTime, # pyright: ignore[reportPrivateImportUsage]
    ) -> str:  
        return when.strftime("%Y%m%d")

    @staticmethod
    def get_signature(method_name: str, timestamp: str):
        signature = DEV_ID + method_name + AUTH_KEY + timestamp
        return md5(signature.encode()).hexdigest()

    async def request(self, method_name: str, *arguments: str):
        if self.hirez_session_id is None:
            self.hirez_session_id = await self.create_session()

            if DEBUG:
                with open("debug_sessionid.txt", "w+") as fp:
                    fp.write(self.hirez_session_id)

        async with aiohttp.ClientSession() as session:
            timestamp = self.get_timestamp()
            signature = self.get_signature(method_name, timestamp)

            if len(arguments) > 0:
                args = "/".join(arguments)
                url = (
                    BASE_URL
                    + f"/{method_name}Json/{DEV_ID}/{signature}/{self.hirez_session_id}/{timestamp}/"
                    + args
                )
            else:
                url = (
                    BASE_URL
                    + f"/{method_name}Json/{DEV_ID}/{signature}/{self.hirez_session_id}/{timestamp}"
                )

            async with session.get(url) as response:
                response.raise_for_status()
                response_json = await response.json()

                if isinstance(response_json, list):
                    if len(response_json) == 0:
                        return_message = "no results"
                    else:
                        return_message = response_json[0]["ret_msg"]
                else:
                    return_message = response_json["ret_msg"]

                if return_message == "Invalid session id.":
                    self.hirez_session_id = await self.create_session()
                    return await self.request(method_name, *arguments)

                return response_json

    async def create_session(self) -> str:
        async with aiohttp.ClientSession() as session:
            timestamp = self.get_timestamp()
            signature = self.get_signature("createsession", timestamp)
            async with session.get(
                BASE_URL + f"/createsessionJson/{DEV_ID}/{signature}/{timestamp}"
            ) as response:
                response.raise_for_status()
                return (await response.json())["session_id"]

    async def ping(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(BASE_URL + "/pingJson") as response:
                return await response.json()

    async def get_player(self, name: str):
        return await self.request("getplayer", name)

    async def get_data_used(self):
        return await self.request("getdataused")

    async def get_match_ids_by_queue(self, queue: SmiteQueue):
        date = self.get_date(pendulum.now("UTC"))

        return await self.request(
            "getmatchidsbyqueue",
            str(queue.value),
            date,
            "0",
        )

    async def get_match_details_batch(self, matches: list[int]):
        matches_arg = ",".join(map(str, matches))
        return await self.request("getmatchdetailsbatch", matches_arg)


if __name__ == "__main__":
    import asyncio
    import json

    async def _main():
        #test_match = 1309419737
        test_match = 1

        client = Client()
        x = await client.get_match_details_batch([test_match])

        q = json.dumps(x)
        print(q)

    asyncio.run(_main())
