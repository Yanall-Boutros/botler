import discord
import dotenv
import sys
import os
import pdb
import discord
import logging
pkey = dotenv.dotenv_values()['token']
class Client(discord.Client):
    async def on_ready(self):
        print(f'Logged on as {self.user}!')
    async def on_message(self, message):
        print(f'Message from {message.author}: {message.content}')
        if message.content.startswith('botler!'): await message.channel.send(f'echo {message.content}')

intents = discord.Intents.default()
intents.message_content = True
    
client = Client(intents=intents)

def main(): client.run(pkey)


if __name__ == '__main__': main()
