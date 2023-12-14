import telebot

from django.conf import settings


bot = telebot.TeleBot(settings.TG_API_TOKEN)


@bot.message_handler(commands=[])
def send_message(data: dict):
    message = ""
    for field, value in data.items():
        message += f"{field}: {value}\n"
    bot.send_message(settings.TG_ID_RECEIVER, message)
