import discord
import time
import dotenv
import sys
import os
import pdb
import discord
import logging
import whisper
import subprocess as s
model = whisper.load_model("base")
pkey = dotenv.dotenv_values()['token']
class Client(discord.Client):
    msg = {}
    async def queue(self, cdr=""):
        await self.message.author.voice.channel.connect()
        with open(cdr, 'r') as f:
            for line in f.readlines():
                await self.message.channel.send(line)
                time.sleep(2)

    async def echo(self, cdr=""):
        await self.message.channel.send(cdr)
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

    async def on_message(self, message):
        print(f'Message from {message.author}: {message.content}')
        self.msg['obj'] = message
        if len(message.content) > 7 and message.content.startswith('botler!'):
            self.message = message
            await self.interpret()
    func_dict = {
            "echo" : echo,
            "q": queue,
            "transcribe": transcribe,
            }


check = lambda message: message.author.id == some_author_id

intents = discord.Intents.default()
intents.message_content = True
    
client = Client(intents=intents)

def main(): client.run(pkey)


if __name__ == '__main__': main()
