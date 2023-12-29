import telebot

from django.conf import settings


bot = telebot.TeleBot(settings.TG_API_TOKEN)


def send_fields_message(fields: dict, receiver_id: int):
    lead_type = settings.BITRIX_LEAD_TYPE[fields['lead_type']]
    lead_qualification = settings.BITRIX_LEAD_QUALIFICATION[fields['lead_qualification']]
    message = f"""Новый лид: {fields['lead_name']}_{fields['phone']};\n
Имя: {fields['lead_name']};\n
Телефон: {fields['phone']};\n
Комментарий: {fields['lead_comment']};\n
Доп. комментарии: {lead_type} | {lead_qualification};\n
Ссылка на запись: {fields['link_to_audio']};\n
Дата лида: {fields['date']};"""
    send_message(message, receiver_id)


@bot.message_handler(commands=[])
def send_message(message: str, receiver_id: int):
    bot.send_message(chat_id=receiver_id, text=message)
