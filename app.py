from flask import Flask, request, jsonify
import discord
from discord.ext import commands

app = Flask(__name__)


bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@app.route('/send_message', methods=['POST'])
def send_message():
    content = request.json.get('content')
    channel_id = request.json.get('channel_id')
    channel = bot.get_channel(int(channel_id))
    bot.loop.create_task(channel.send(content))
    return jsonify({'status': 'Message sent'})

if __name__ == '__main__':
    app.run(port=5000)
