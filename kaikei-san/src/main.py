# Pycordを読み込む
import discord
from discord.commands import Option
import datetime
import os

TOKEN = os.environ["TOKEN"]

chouboId = int(os.environ["CHOUBO_ID"])


bot = discord.Bot(
    intents=discord.Intents.all(),
    activity=discord.Game("帳簿の集計"),
)


@bot.event
async def on_ready():
    print("会計さんを起動")


@bot.command(
    name="shiwake",
    description="仕訳を帳簿に追加します",
)
async def shiwake(
    ctx: discord.ApplicationContext,
    loanborrow: Option(
        discord.SlashCommandOptionType.string,
        choices=["貸", "借"],
        description="仕訳内容（貸 or 借）",
    ),  # type: ignore
    entry: Option(discord.SlashCommandOptionType.integer, description="金額"),  # type: ignore
    details: Option(discord.SlashCommandOptionType.string, description="内訳"),  # type: ignore
):  # type: ignore
    channel = bot.get_channel(chouboId)
    ## 帳簿追加内容
    result = f"{loanborrow} {entry} {details}"
    print("帳簿追加: " + result)
    await channel.send(result)
    await ctx.respond(
        f"帳簿に追加しました 仕訳「{loanborrow}」 金額「{format(entry, ',')}円」 名目「{details}」"
    )


@bot.command(name="kaikei", description="帳簿を会計します")
async def kaikei(ctx: discord.ApplicationContext):
    print("---会計コマンドを実行---")

    ## 帳簿チャンネル
    channel = bot.get_channel(chouboId)

    ## 帳簿件数
    count = 0
    ## 会計
    result = 0

    ## チャンネルメッセージ履歴を購読
    async for message in channel.history(limit=500):
        print("Read line:" + message.content)
        [
            loanBorrow,
            entry,
            _,
        ] = message.content.split(" ")

        if loanBorrow == "貸":
            result += int(entry)
        elif loanBorrow == "借":
            result -= int(entry)
        elif loanBorrow == "総":
            result += int(entry)
            print("以降は会計済み")
            break
        count += 1

    print(f"検索件数: {str(count + 1)}件")
    ## 結果メッセージ
    response = "帳簿計算したところ、"
    summary = ""
    if result != 0:
        response += format(abs(result), ",") + " 円"
        if result < 0:
            response += "貸していました"
        else:
            response += "借りていました"
        summary += (
            "総 "
            + str(abs(result))
            + " "
            + datetime.datetime.now().strftime("%Y/%m/%dまでの集計")
        )
        ## 総計エントリ以外が存在する場合は総計エントリを追加
        if count != 0:
            await channel.send(summary)
    else:
        response += "差し引き 0円でした"
    print("終了 ---------------")
    await ctx.respond(response)


bot.run(TOKEN)
