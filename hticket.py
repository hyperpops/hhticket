import os
import json
import discord
from discord.ext import commands
from dotenv import load_dotenv
from keep_alive import keep_alive

load_dotenv()

TOKEN = os.getenv("TOKEN")
COUNTER_FILE = "counter.json"
GREEN = 0x78E572

CRYPTOS = {
    "btc": ("Bitcoin", "<:btc:1546606873850023966>"),
    "eth": ("Ethereum", "<:eth:1546607067454902303>"),
    "ltc": ("Litecoin", "<:ltc:1546606840509632692>"),
    "sol": ("Solana", "<:sol:1546606824181211206>"),
    "usdt": ("USDT [ERC-20]", "<:usdt:1546606857437708299>")
}


def get_counter():
    if not os.path.exists(COUNTER_FILE):
        with open(COUNTER_FILE, "w") as f:
            json.dump(1994368, f)
        return 1994368

    with open(COUNTER_FILE, "r") as f:
        data = json.load(f)

    # Supports both the old integer format and {"count": number}.
    if isinstance(data, int):
        return data
    if isinstance(data, dict) and "count" in data:
        return int(data["count"])

    raise ValueError("counter.json has an invalid format")


def next_counter():
    count = get_counter()
    with open(COUNTER_FILE, "w") as f:
        json.dump(count + 1, f)
    return count


async def create_crypto_ticket(interaction: discord.Interaction, crypto: str):
    # Acknowledge the interaction immediately so Discord does not time it out
    # while the ticket channel is being created.
    await interaction.response.defer(ephemeral=True)

    number = next_counter()
    channel_name = f"auto-{crypto}{number}"

    overwrites = {
        interaction.guild.default_role: discord.PermissionOverwrite(
            view_channel=False
        ),
        interaction.user: discord.PermissionOverwrite(
            view_channel=True,
            send_messages=True,
            read_message_history=True
        ),
        interaction.guild.me: discord.PermissionOverwrite(
            view_channel=True,
            send_messages=True,
            manage_channels=True
        )
    }

    channel = await interaction.guild.create_text_channel(
        name=channel_name,
        overwrites=overwrites
    )

    ticket_created_embed = discord.Embed(
        title="Ticket Created",
        description=f"Ticket {channel.mention} created.",
        color=GREEN
    )

    await interaction.followup.send(
        embed=ticket_created_embed,
        ephemeral=True
    )


class CryptoStartButton(discord.ui.Button):
    def __init__(self, crypto: str):
        super().__init__(
            label="Start",
            style=discord.ButtonStyle.success,
            custom_id=f"crypto_ticket_{crypto}"
        )
        self.crypto = crypto

    async def callback(self, interaction: discord.Interaction):
        await create_crypto_ticket(interaction, self.crypto)


class CryptoPanelView(discord.ui.LayoutView):
    def __init__(self):
        super().__init__(timeout=None)

        crypto_container = discord.ui.Container(
            discord.ui.TextDisplay("# Start Cryptocurrency Deal"),
            discord.ui.TextDisplay(
                "Use the selection below to start a deal using the appropriate coin & network. "
                "Please be sure all deals abide by the [Terms of Service](https://www.halalmm.com/terms). "
                "Refer to our [website](https://www.halalmm.com/) for a detailed overview of "
                "**service fees & supported networks.**"
            ),
            discord.ui.Separator(),
            discord.ui.Section(
                f"### {CRYPTOS['btc'][1]} {CRYPTOS['btc'][0]}",
                accessory=CryptoStartButton("btc")
            ),
            discord.ui.Separator(),
            discord.ui.Section(
                f"### {CRYPTOS['eth'][1]} {CRYPTOS['eth'][0]}",
                accessory=CryptoStartButton("eth")
            ),
            discord.ui.Separator(),
            discord.ui.Section(
                f"### {CRYPTOS['ltc'][1]} {CRYPTOS['ltc'][0]}",
                accessory=CryptoStartButton("ltc")
            ),
            discord.ui.Separator(),
            discord.ui.Section(
                f"### {CRYPTOS['sol'][1]} {CRYPTOS['sol'][0]}",
                accessory=CryptoStartButton("sol")
            ),
            accent_color=GREEN
        )

        stablecoin_container = discord.ui.Container(
            discord.ui.TextDisplay("# Stablecoins"),
            discord.ui.TextDisplay(
                "Start a deal with USDT on the network that matches your wallet. "
                "Please be sure to select the correct network."
            ),
            discord.ui.Separator(),
            discord.ui.Section(
                f"### {CRYPTOS['usdt'][1]} {CRYPTOS['usdt'][0]}",
                accessory=CryptoStartButton("usdt")
            ),
            accent_color=GREEN
        )

        self.add_item(crypto_container)
        self.add_item(stablecoin_container)


intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    bot.add_view(CryptoPanelView())
    print(f"Logged in as {bot.user}")


@bot.command()
async def panel(ctx):
    await ctx.send(view=CryptoPanelView())


keep_alive()
bot.run(TOKEN)
