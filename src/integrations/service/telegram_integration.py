import telebot

from django.conf import settings


bot = telebot.TeleBot(settings.TG_API_TOKEN)


def send_message_to_tg(fields: dict, receiver_id: str, is_double: bool):
    lead_type = settings.BITRIX_LEAD_TYPE[fields['lead_type']]
    lead_qualification = settings.BITRIX_LEAD_QUALIFICATION[fields['lead_qualification']]
    message = f"""Новый лид: {fields['lead_name']}_{fields['phone']};\n
Имя: {fields['lead_name']};\n
Телефон: {fields['phone']};\n
Комментарий: {fields['lead_comment']};\n
Доп. комментарий: {lead_type} | {lead_qualification};\n
Ссылка на запись: {fields['link_to_audio']};\n
Дата лида: {fields['date']};"""
    if is_double:
        message = "Дубль\n\n" + message
    send_message(message, receiver_id)


def send_message_to_dev(message: str):
    send_message(
        message,
        settings.TG_DEV_ACCOUNT
    )


def send_message_to_dev_chat(message: str):
    send_message(
        message,
        settings.TG_DEV_CHAT
    )


@bot.message_handler(commands=[])
def send_message(message: str, receiver_id: str):
    bot.send_message(chat_id=receiver_id, text=message)
