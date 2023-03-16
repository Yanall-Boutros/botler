from __future__ import unicode_literals
import discord
from dateutil import parser
from discord.ext import tasks
from discord.ext import commands as c
import asyncio
from pytube import YouTube
import time
#import dotenv
import sys
import os
import numpy as np
import datetime
import pdb
import discord
import logging
import subprocess as s
import yt_dlp as youtube_dl
pkey = ""
with open(".env", "r") as key: pkey = key.read().strip()
class Client(discord.Client):
    msg = {}
    vc = None
    q = []
    timers = {}

    @tasks.loop(seconds=60)
    async def check_timers(self):
        print("Checking timers:")
        print(self.timers)
        now = datetime.datetime.now()
        key = f"{now.hour-8}:{now.minute}"
        print(key)
        if key in self.timers:
            for author, content in self.timers[key]:
                user = await self.fetch_user(author)
                print("DMing User", author, content)
                await user.send(content)

    async def remind(self, cdr):
        # cdr[0] = at what time in their timezone
        # cdr[1] = message to be reminded
        time = cdr.split()[0]
        utc = int(cdr.split()[1])
        content = cdr.split()[2:]
        author = self.message.author.id
        remtime=parser.parse(time)
        remtime = remtime.replace(hour=remtime.hour)
        k = f"{remtime.hour+utc}:{remtime.minute}"
        if k in self.timers: self.timers[k].append((author, " ".join(content)))
        else: self.timers[k] = [(author, " ".join(content))]
        await self.check_timers()


    async def queue(self, cdr=""):
        await self.message.author.voice.channel.connect()
        with open(cdr, 'r') as f:
            for line in f.readlines():
                await self.message.channel.send(line)
                time.sleep(2)

    async def echo(self, cdr=""):
        await self.message.channel.send(cdr)
        return

    async def penis(self, cdr=""):
        split = cdr.split()
        target = await self.message.guild.fetch_member(split[0])
        if len(split) == 1: await target.edit(nick="᲼")
        else: await target.edit(nick=" ".join(split[1:]))

    async def muffle(self, cdr=""):
        if not ("Support" in self.message.author.name or\
               "Spurley" in self.message.author.name): return
        try:
            target_name = cdr.split()[0]
            length = int(cdr.split()[1])
        except Exception as e:
            print(e)
            length = 10

        target_name = target_name.replace("<@", "")
        target_name = target_name.replace(">", "")
        while length>0:
            await asyncio.sleep(1)
            target = await self.message.guild.fetch_member(target_name)
            await target.edit(mute=True)
            length -= 1
        return
    async def rand_num(self, cdr=""):
        bottom, top = tuple(map(lambda x: int(x), cdr.split()))
        await self.message.channel.send(str(np.random.randint(bottom, top)))

    async def unmuffle(self, cdr=""):
        if not ("Support" in self.message.author.name or\
               "Spurley" in self.message.author.name): return
        cdr = cdr.replace("<@", "")
        cdr = cdr.replace(">", "")
        target = await self.message.guild.fetch_member(cdr)
        await target.edit(mute=False)
        return

    async def transcribe(self, cdr=""):
        files = []
        if len(self.message.attachments) == 0:
            await self.message.channel.send("No input!")
            return

        for atm in self.message.attachments:
            files.append(atm.filename)
            with open(f"./{atm.filename}", "w") as a: atm.save(a)

        for fl in files:
            fltype = str(s.run(["file", fl], capture_output=True).stdout, 'utf-8').strip()
            if all(list(map(lambda cnd: cnd in fltype, ["PCM", "mono", "16000"]))):
                data = model.transcribe(f"{fl}")
                with open(f"{fl}.txt", "w") as t: t.write(data['text'])
                with open(f"{fl}.txt", "rb") as t: await self.message.channel.send("Processed: ",
                        file=discord.File(t, f"{fl}.txt"))
            else:
                print(s.run(['./to_wav.sh', f'{fl}']).stdout)
                data = model.transcribe(f"{fl}.wav")
                with open(f"{fl}.wav.txt", "w") as t: t.write(data['text'])
                with open(f"{fl}.wav.txt", "rb") as t: await self.message.channel.send("Processed: ",
                        file=discord.File(t, f"{fl}.wav.txt"))


    async def interpret(self):
        inp = self.message.content[7:].strip().split()
        fnc = inp[0]
        if fnc not in self.func_dict:
            await self.message.channel.send(f"Unrecognized function {inp[0]}")
            return

        if len(inp) > 1:
            cdr = " ".join(inp[1:])
            await self.func_dict[fnc](self, cdr)
            return
        else:
            await self.func_dict[fnc](self)
            return

    async def on_ready(self):
        print(f'Logged on as {self.user}!')
        if not self.check_timers.is_running():
            self.check_timers.start()

    async def on_message(self, message):
        print(f'Message from {message.author}: {message.content}')
        self.msg['obj'] = message
        if len(message.content) > 7 and message.content.startswith('botler!'):
            self.message = message
            await self.interpret()

    async def clearq(self): self.q = []
    async def play(self, message):
        user = self.message.author
        voice_channel=user.voice.channel
        channel=None
        if len(self.q) == 0: self.q = [message]
        if voice_channel!=None:
            channel=voice_channel.name
            if self.vc is not None:
                self.q.append(message)
                await self.message.channel.send(f"+2q:{message}")
            else:
                self.vc = await voice_channel.connect()
                while(len(self.q)):
                    link = self.q.pop(0)
                    ydl_opts = {'format': 'bestaudio/best',
                                'postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '192'}]
                               }
                    filename=""
                    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                        info=ydl.extract_info(link, download=True)
                        filename = f"{ydl.prepare_filename(info)[:-5]}.mp3"
                    video = yt.streams.filter(only_audio=True).first()
                    await self.message.channel.send(f"Playing: {filename}")
                    s = discord.FFmpegPCMAudio(source=filename)
                    self.vc.play(source=s)
                    while self.vc.is_playing(): await asyncio.sleep(1)
                    os.remove(filename)
            await self.vc.disconnect()
            self.vc=None

    func_dict = {
            "echo" : echo,
            "q": queue,
            "transcribe": transcribe,
            "muffle": muffle,
            "unmuffle": unmuffle,
            "rand_num": rand_num,
            "strip_identity": penis,
            "play": play,
            "clearq": clearq,
            "remindme": remind,
            }


check = lambda message: message.author.id == some_author_id

intents = discord.Intents.default()
intents.message_content = True

client = Client(intents=intents)

def main(): client.run(pkey)


if __name__ == '__main__': main()
