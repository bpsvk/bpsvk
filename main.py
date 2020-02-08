import requests
import hashlib

from flask import Flask, request
from settings import *

# Создаём экземпляр объекта Flask
app = Flask(__name__)

# Вызываем декоратор фласка и "оборачивем" нашу главную функцию в него
@app.route('/', methods = ['POST', 'GET'])
def main():
    # Получаем JSON из запроса к web-сервера
    json = request.get_json()
    # "Расшифровываем" для удобства обращения
    _type = json['type']
    _data = json['data']

    # Запрос типа 'confirm' выполняется при подключении веб-хука и возвращает MD5 строку VK ID + CM API Token
    if _type == 'confirm':
        confirmation_token = hashlib.md5(str(hash_obj).encode()).hexdigest()

        return confirmation_token

    # Запрос типа 'delete_for_all' удаляет сообщения для всех пользователей командой: !чистка
    # (подробнее: https://vk.com/@cm-callback-delete?anchor=pro-komandu)
    if _type == 'delete_for_all':
        ids = _data['conversation_message_ids']
        chat = _data['chat']
        ids2 = ','.join(map(str, ids))

        # Формируем строку 'code' для vk.execute
        code_str = "return API.messages.delete({delete_for_all: 1, message_ids: API.messages.getByConversationMessageId" \
                   "({peer_id: %d, conversation_message_ids: [%s]}).items@.id});" % (chat_ids[chat] + 2000000000, str(ids2))

        # Возвращаем результат исполнения запроса к API VK
        return str(requests.post('https://api.vk.com/method/execute', data={'v': '5.100', 'access_token': vk_token,
                                                                            'code': code_str}))

    if (_type == 'invite') or  (_type == 'ban_expired'):
        chat = chat_ids[_data['chat']]
        user = _data['user']

        # Формируем строку 'code' для vk.execute
        code_str = "if (API.friends.areFriends({user_ids: %s})[0].friend_status == 3)" \
                   "{return API.messages.addChatUser({chat_id: %s, user_id: %s});}return 0;" % (user, chat, user)

        # Возвращаем результат исполнения запроса к API VK
        return str(requests.post('https://api.vk.com/method/execute', data={'v': '5.100', 'access_token': vk_token,
                                                                            'code': code_str}))


if __name__ == '__main__':
    app.run(debug=False)