import discord
import os
from discord.ext import commands, tasks
from dotenv import load_dotenv
from coinbase.rest import RESTClient
from datetime import datetime, timedelta, timezone, time

load_dotenv()

DISCORD_TOKEN = os.getenv("BOT_TOKEN")
COINBASE_API_KEY = os.getenv("COINBASE_API_KEY")
COINBASE_API_SECRET = os.getenv("COINBASE_API_SECRET")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='*', intents=intents)
client = RESTClient(COINBASE_API_KEY, COINBASE_API_SECRET)

def get_data(token):

    #get the current price
    product = client.get_product(product_id=token)
    price = float(product["price"])

    if not price:
        price = 0

    #get the price from 24h ago and calculate the delta

    end_dt = datetime.now(timezone.utc)
    start_dt = end_dt - timedelta(hours=24)

    previous_prices_24h = client.get_candles(token, int(start_dt.timestamp()), int(end_dt.timestamp()), 'ONE_HOUR')

    candle_24h = previous_prices_24h["candles"][-1]

    if not candle_24h:
        raise RuntimeError("No candle data returned for 24 hours ago")

    price_24h = float(candle_24h["close"])

    delta_24h = (price - price_24h)/price_24h * 100
    delta_24h = round(delta_24h, 2)

    if not delta_24h:
        delta_24h = 0

    #get the price from a week ago and calculate the delta

    start_dt = end_dt - timedelta(hours=168)

    previous_prices_week = client.get_candles(token, int(start_dt.timestamp()), int(end_dt.timestamp()), 'ONE_HOUR')

    candle_week = previous_prices_week["candles"][-1]

    if not candle_week:
        raise RuntimeError("No candle data returned for a week ago")

    price_week = float(candle_week["close"])
    highest_week = previous_prices_week["candles"][0]["high"]
    lowest_week = previous_prices_week["candles"][0]["high"]

    for i in range(1,167):
        if previous_prices_week["candles"][i]["high"] > highest_week:
            highest_week = previous_prices_week['candles'][i]['high']
        else:
            if previous_prices_week["candles"][i]["low"] < lowest_week:
                lowest_week = previous_prices_week['candles'][i]['low']

    delta_week = (price - price_week)/price_week * 100
    delta_week = round(delta_week, 2)

    if not delta_week:
        delta_week = 0

    return price, delta_24h, highest_week, lowest_week, delta_week

def get_all_data(tokens):

    #temp lists
    prices = []
    deltas_24h = []
    highests_week = []
    lowests_week = []
    deltas_week = []

    #temporary variables
    price = float
    delta_24h = float
    highest_week = str
    lowest_week = str
    delta_week = float

    for i in range(0,4):
        price, delta_24h, highest_week, lowest_week, delta_week = get_data(tokens[i])
        prices.append(price)
        deltas_24h.append(delta_24h)
        highests_week.append(highest_week)
        lowests_week.append(lowest_week)
        deltas_week.append(delta_week)

    return prices, deltas_24h, highests_week, lowests_week, deltas_week

def make_embed():

    #lists
    prices = []
    deltas_24h = []
    highests_week = []
    lowests_week = []
    deltas_week = []

    #aquire data
    tokens = ['BTC-USD', 'SOL-USD', 'ETH-USD', 'DOGE-USD']
    prices, deltas_24h, highests_week, lowests_week, deltas_week = get_all_data(tokens)

    #make the embed
    embed = discord.Embed(title = "Coin Monitor's Daily Report", color = discord.Colour.from_rgb(244, 184, 22))

    #Bitcoin data
    embed.add_field(name = "<:btc_logo:1463568211877564562> Bitcoin (BTC)", value = '', inline = False)
    embed.add_field(name = 'current price', value = str(prices[0]) + '$', inline = True)
    embed.add_field(name = 'daily evolution', value = str(deltas_24h[0]) + '%', inline = True)
    embed.add_field(name = 'weekly evolution', value = str(deltas_week[0]) + '%', inline = True)
    embed.add_field(name = 'highest price in last week', value = str(highests_week[0]) + '$', inline = True)
    embed.add_field(name = 'lowest price in last week', value = str(lowests_week[0]) + '$', inline = True)

    #Solana data
    embed.add_field(name = "<:sol_logo:1463571460139257856> Solana (SOL)", value = '', inline = False)
    embed.add_field(name = 'current price', value = str(prices[1]) + '$', inline = True)
    embed.add_field(name = 'daily evolution', value = str(deltas_24h[1]) + '%', inline = True)
    embed.add_field(name = 'weekly evolution', value = str(deltas_week[1]) + '%', inline = True)
    embed.add_field(name = 'highest price in last week', value = str(highests_week[1]) + '$', inline = True)
    embed.add_field(name = 'lowest price in last week ', value = str(lowests_week[1]) + '$', inline = True)
    
    #Ethereum data
    embed.add_field(name = "<:eth_logo:1463572693105508523> Ethereum (ETH)", value = '', inline = False)
    embed.add_field(name = 'current price', value = str(prices[2]) + '$', inline = True)
    embed.add_field(name = 'daily evolution', value = str(deltas_24h[2]) + '%', inline = True)
    embed.add_field(name = 'weekly evolution', value = str(deltas_week[2]) + '%', inline = True)
    embed.add_field(name = 'highest price in last week', value = str(highests_week[2]) + '$', inline = True)
    embed.add_field(name = 'lowest price in last week ', value = str(lowests_week[2]) + '$', inline = True)
    
    #Dogecoin data
    embed.add_field(name = "<:doge_logo:1463573675738533908> Dogecoin (DOGE)", value = '', inline = False)
    embed.add_field(name = 'current price', value = str(prices[3]) + '$', inline = True)
    embed.add_field(name = 'daily evolution', value = str(deltas_24h[3]) + '%', inline = True)
    embed.add_field(name = 'weekly evolution', value = str(deltas_week[3]) + '%', inline = True)
    embed.add_field(name = 'highest price in last week', value = str(highests_week[3]) + '$', inline = True)
    embed.add_field(name = 'lowest price in last week ', value = str(lowests_week[3]) + '$', inline = True)

    embed.add_field(name = '', value = '*service brought to you by ffwm*', inline = False)

    return embed

#configures the bot when online
@bot.event
async def on_ready():
    print(f'Bot is online as {bot.user}')
    daily_report.start()

#defines a command to test the daily report
@bot.command()
async def test(ctx):
    embed = make_embed()
    await ctx.send(embed = embed)

#automatically sends the report at 19:00 CET
@tasks.loop(time=time(hour=19, minute=0, tzinfo = timezone(timedelta(hours=+1))))
async def daily_report():
    channel = bot.get_channel(your_channel_id)
    embed = make_embed()
    await channel.send(embed=embed)

bot.run(DISCORD_TOKEN)