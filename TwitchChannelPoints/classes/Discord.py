from textwrap import dedent

import requests

from TwitchChannelPointsMiner.classes.Settings import Events


class Discord(object):
    __slots__ = ["webhook_api", "events"]

    def __init__(self, webhook_api: str, events: list):
        self.webhook_api = webhook_api
        self.events = [str(e) for e in events]

    def send(self, message: str, event: Events) -> None:
        if str(event) in self.events:
            requests.post(
                url=self.webhook_api,
                data={
                    "content": dedent(message),
                    "username": "miau",
                    "avatar_url": "https://cdn.discordapp.com/attachments/1011810855895179354/1317598510534754465/IMG_3753.jpg?ex=675f44bc&is=675df33c&hm=c5b85b4773614e3ac51b4ed284b811fe637556655e30c36843a2bfaab63c883e&",
                },
            )
