# Pycordを読み込む
import discord
from datetime import datetime
import time
import os
import asyncio
import random
import json
import requests
from enum import Enum

TOKEN = os.environ["TOKEN"]

appName = "天気ちゃん"
channelId = int(os.environ["CHANNEL_ID"])

weatherApiUrl = os.environ["WEATHER_APIURL"]

postHour = 20

kanjo = [
    "かなしかった",
    "しょんぼりした",
    "つらかった",
    "しんどかった",
    "うれしかった",
    "たのしかった",
    "しあわせだった",
    "よかった",
]
tenkichanStatus = ["晴れ", "よかった", len(kanjo) - 1]

wakeup = [
    "おきた...",
    "あさだ...",
    "ねてた...",
]


bot = discord.Bot(
    intents=discord.Intents.all(),
    activity=discord.Game("空の観察"),
)


class dateLabel(Enum):
    today = "今日"
    tomorrow = "明日"


def comment():
    feeling = random.random()
    meter = round(feeling * (len(kanjo) - 1))
    return [kanjo[meter], feeling - 0.5]


def getWeather():
    jsonForm: list = json.loads(requests.get(weatherApiUrl).text)

    weather: dict
    result: dict = {}
    for weather in jsonForm.get("forecasts"):
        todayDateLabel: dateLabel = weather.get("dateLabel")
        weatherEntry = weather.get("detail").get("weather")
        if weatherEntry is not None:
            weatherEntry: str
            result[todayDateLabel] = weatherEntry.split("　")[0]
    return result


async def main():
    global today
    weathers = ["晴れ", "くもっ", "雨だっ"]
    dt = datetime.today()
    print(f"today: {dt}")
    print("sub thread start")

    channel = bot.get_channel(channelId)

    ## 再起動時に表示
    awakeMessage = wakeup[int(round(random.random() * len(wakeup)))]
    print("Awaike message send: " + awakeMessage)
    await channel.send(awakeMessage)

    ## 間隔
    onlinetime = 60 * 5
    interval = 24 * 60 * 60 - onlinetime

    diffTime = (postHour * 60 - (dt.hour * 60 + dt.minute)) * 60
    # diffTime = 1 ## debug
    waitTime = diffTime if diffTime >= 0 else interval + diffTime

    while True:
        weather = getWeather()
        print(
            f"Wait next: {str(waitTime / 60)}min({str(round(waitTime / 60 / 60, 3))}h)..."
        )
        await bot.change_presence(status=discord.Status.idle)

        time.sleep(max(waitTime - onlinetime, 0))
        await bot.change_presence(status=discord.Status.online)
        ## 24時間後に投稿
        waitTime = interval
        tenkichanStatus = [weather.get("今日")] + comment()
        await channel.send(
            "今日は"
            + tenkichanStatus[0]
            + "で"
            + tenkichanStatus[1]
            + "。\n明日は"
            + weather.get("明日")
            + "の予報だ。"
            + weathers[round(random.random() * (len(weathers) - 1))]
            + "たらいいな..."
        )
        print(f"Status: {str(tenkichanStatus)}")
        time.sleep(max(onlinetime, 0))


@bot.event
async def on_ready():
    print("Start: " + appName)
    await bot.change_presence(status=discord.Status.idle)
    asyncio.run_coroutine_threadsafe(main(), bot.loop)


if __name__ == "__main__":
    bot.run(TOKEN)
