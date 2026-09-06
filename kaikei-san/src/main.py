"""kaikei-san のエントリポイント。bot初期化・コマンド登録・起動を行う。"""

import io
import logging
import os

import discord
from discord.commands import Option

import db
import formatting
import repository

TOKEN = os.environ["TOKEN"]
DB_PATH = os.environ.get("DB_PATH", "/workspace/data/kaikei.db")
GUILD_ID = os.environ.get("GUILD_ID")
DEBUG_GUILDS = [int(GUILD_ID)] if GUILD_ID else None
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()
CHANNEL_ID = os.environ.get("CHANNEL_ID")

logging.basicConfig(level=LOG_LEVEL, format="%(levelname)s %(message)s")
logger = logging.getLogger("kaikei_san")

bot = discord.Bot(
    intents=discord.Intents.default(),
    activity=discord.Game("貸し借りの記録"),
    debug_guilds=DEBUG_GUILDS,
)

connection = db.connect(DB_PATH)


async def notify_channel(message: str) -> None:
    if CHANNEL_ID is None:
        return
    channel = bot.get_channel(int(CHANNEL_ID))
    if channel is None:
        logger.warning("通知チャンネルが見つかりません channel_id=%s", CHANNEL_ID)
        return
    await channel.send(message)


_original_close = bot.close


async def _close_with_notice():
    await notify_channel("終了します")
    await _original_close()


bot.close = _close_with_notice


@bot.event
async def on_ready():
    logger.debug("会計さんを起動")
    await notify_channel("業務開始します")


@bot.command(name="lend", description="相手にお金を貸した記録を追加します")
async def lend(
    ctx: discord.ApplicationContext,
    user: Option(discord.SlashCommandOptionType.user, description="貸した相手"),  # type: ignore
    amount: Option(discord.SlashCommandOptionType.integer, description="金額"),  # type: ignore
    memo: Option(discord.SlashCommandOptionType.string, description="名目"),  # type: ignore
):  # type: ignore
    logger.info(
        "command=lend guild_id=%s user_id=%s target_user_id=%s amount=%s",
        ctx.guild_id,
        ctx.author.id,
        user.id,
        amount,
    )
    try:
        repository.add_lend(
            connection,
            guild_id=ctx.guild_id,
            lender_id=ctx.author.id,
            borrower_id=user.id,
            amount=amount,
            memo=memo,
        )
    except repository.InvalidTransactionError as error:
        await ctx.respond(f"記録できませんでした: {error}")
        return
    await ctx.respond(
        formatting.format_lend_confirmation(borrower_id=user.id, amount=amount, memo=memo)
    )


@bot.command(name="borrow", description="相手からお金を借りた記録を追加します")
async def borrow(
    ctx: discord.ApplicationContext,
    user: Option(discord.SlashCommandOptionType.user, description="借りた相手"),  # type: ignore
    amount: Option(discord.SlashCommandOptionType.integer, description="金額"),  # type: ignore
    memo: Option(discord.SlashCommandOptionType.string, description="名目"),  # type: ignore
):  # type: ignore
    logger.info(
        "command=borrow guild_id=%s user_id=%s target_user_id=%s amount=%s",
        ctx.guild_id,
        ctx.author.id,
        user.id,
        amount,
    )
    try:
        repository.add_borrow(
            connection,
            guild_id=ctx.guild_id,
            borrower_id=ctx.author.id,
            lender_id=user.id,
            amount=amount,
            memo=memo,
        )
    except repository.InvalidTransactionError as error:
        await ctx.respond(f"記録できませんでした: {error}")
        return
    await ctx.respond(
        formatting.format_borrow_confirmation(lender_id=user.id, amount=amount, memo=memo)
    )


@bot.command(name="kaikei", description="あなたの貸し借りサマリーを表示します")
async def kaikei(ctx: discord.ApplicationContext):
    logger.info("command=kaikei guild_id=%s user_id=%s", ctx.guild_id, ctx.author.id)
    entries = repository.get_summary(connection, guild_id=ctx.guild_id, user_id=ctx.author.id)
    await ctx.respond(formatting.format_summary(entries))


@bot.command(name="history", description="あなたが関与した貸し借り記録をファイルで出力します")
async def history(
    ctx: discord.ApplicationContext,
    month: Option(
        discord.SlashCommandOptionType.string,
        description="対象年月（省略時は直近30日、all で全件）",
        choices=formatting.build_month_choices(),
        required=False,
        default=None,
    ),  # type: ignore
):  # type: ignore
    logger.info(
        "command=history guild_id=%s user_id=%s month=%s", ctx.guild_id, ctx.author.id, month
    )

    if month is None:
        start_at, end_at = repository.recent_range_utc()
    elif month == formatting.MONTH_ALL:
        start_at, end_at = None, None
    else:
        year, mon = (int(part) for part in month.split("-"))
        start_at, end_at = repository.month_range_utc(year, mon)

    transactions = repository.get_user_history(
        connection,
        guild_id=ctx.guild_id,
        user_id=ctx.author.id,
        start_at=start_at,
        end_at=end_at,
    )
    if not transactions:
        await ctx.respond("記録がありません")
        return

    content = formatting.format_history_file(transactions, user_id=ctx.author.id)
    file = discord.File(io.BytesIO(content.encode("utf-8")), filename="kaikei_history.txt")
    await ctx.respond("貸し借り記録を添付しました", file=file)


if __name__ == "__main__":
    bot.run(TOKEN)
