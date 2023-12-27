import telebot

from django.conf import settings


bot = telebot.TeleBot(settings.TG_API_TOKEN)


def send_fields_message(fields: dict):
    message = ""
    for field, value in fields.items():
        message += f"{field}: {value}\n"
    send_message(message)


@bot.message_handler(commands=[])
def send_message(message: str):
    bot.send_message(chat_id=settings.TG_ID_RECEIVER, text=message)
