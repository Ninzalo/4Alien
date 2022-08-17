import vk_api
import requests
import time
import socket
import urllib3
import random
from vk_api.bot_longpoll import VkBotEventType, VkBotLongPoll
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from config import token_vk

vk_session = vk_api.VkApi(token=token_vk)
longpoll = VkBotLongPoll(vk_session, 209623260)
sender_id = 490937725   # alien id
# sender_id = 290711560   # my id


def sender(id, text):
    vk_session.method('messages.send', {'user_id': id, 'message': text, 'random_id': 0})


def chat_sender(id, text, keyboard=None):

    post = {
        "chat_id": id,
        "message": text,
        "random_id": 0
    }


    if keyboard != None:
        post["keyboard"] = keyboard.get_keyboard()
    else:
        post = post

    vk_session.method("messages.send", post)


while True:
    try:
        for event in longpoll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW and event.from_chat:

                msg = event.object.message['text'].lower()


                if msg == '/t':
                    id = event.chat_id
                    text = "Начать тест?"
                    keyboard = VkKeyboard()
                    keyboard.add_button("|Начать тест|", color=VkKeyboardColor.PRIMARY)
                    chat_sender(id, text, keyboard)

                if "|Начать тест|".lower() in msg:
                    started = "Тест запущен"
                    sender(id=sender_id, text=started)
                    id = event.chat_id

                    # set number of tasks
                    num_of_tasks = 20

                    true_values = []
                    mistakes_list = []
                    for iter in range(1, num_of_tasks + 1):
                        variation = random.randrange(1, 3)

                        # set number of tasks with variation = 1
                        var1_tasks = 4

                        if iter < var1_tasks + 1:
                            variation = 1
                        if variation == 1:
                            if iter < var1_tasks + 1:
                                a = random.randrange(2, 10)
                            else:
                                a = random.randrange(2, 100)
                            b = random.randrange(2, 10)
                            question = a * b
                            text = f"{iter}. {a} * {b} = ?"
                            quest = text.split('?')[0].split('.')[1]
                            chat_sender(id, text)
                            # sender(id=sender_id, text=text)
                            for eve in longpoll.listen():
                                if eve.type == VkBotEventType.MESSAGE_NEW and eve.from_chat:
                                    msg1 = eve.object.message['text'].lower()
                                    id = eve.chat_id

                                    try:
                                        try:
                                            msg1 = msg1.split("/")[1]
                                        except:
                                            pass
                                        msg1 = int(msg1)
                                        if int(msg1) == int(question):
                                            true_values.append(msg1)
                                        else:
                                            mistakes_list.append(f"{iter}.    {quest}{msg1} ({question})")
                                        # sender(id=sender_id, text=msg1)
                                    except:
                                        pass

                                    if not iter == num_of_tasks:
                                        # text = "Следующий вопрос"
                                        # chat_sender(id, text)
                                        break
                                    else:
                                        text = "Тест окончен"
                                        chat_sender(id, text)
                                        break
                        else:
                            while True:
                                a = random.randrange(2, 100)
                                b = random.randrange(2, 10)
                                if a % b == 0:
                                    question = a // b
                                    text = f"{iter}. {a} : {b} = ?"
                                    quest = text.split('?')[0].split('.')[1]
                                    chat_sender(id, text)
                                    # sender(id=sender_id, text=text)
                                    for eve in longpoll.listen():
                                        if eve.type == VkBotEventType.MESSAGE_NEW and eve.from_chat:
                                            msg1 = eve.object.message['text'].lower()
                                            id = eve.chat_id

                                            try:
                                                try:
                                                    msg1 = msg1.split("/")[1]
                                                except:
                                                    pass
                                                msg1 = int(msg1)
                                                if int(msg1) == int(question):
                                                    true_values.append(msg1)
                                                else:
                                                    mistakes_list.append(f"{iter}.    {quest}{msg1} ({question})")
                                                # sender(id=sender_id, text=msg1)
                                            except:
                                                pass

                                            if not iter == num_of_tasks:
                                                # text = "Следующий вопрос"
                                                # chat_sender(id, text)
                                                break
                                            else:
                                                text = "Тест окончен"
                                                chat_sender(id, text)
                                                break
                                    break

                        if iter == num_of_tasks:
                            break


                    text = f"Ваш результат: {len(true_values)}/{num_of_tasks}"
                    # chat_sender(id, text)
                    # sender(id=sender_id, text=text)
                    if not len(mistakes_list) == 0:
                        text = f"{text}\n\nОшибки: \n"

                        for item in mistakes_list:
                            text = f"{text}{item}\n"
                        chat_sender(id, text)
                        sender(id=sender_id, text=text)
                    else:
                        chat_sender(id, text)
                        sender(id=sender_id, text=text)

                    if len(true_values) == num_of_tasks:
                        text = f"Молодец!"
                        chat_sender(id, text)

                    if len(true_values) <= num_of_tasks/2:
                        text = f'Попробуй еще раз!'
                        chat_sender(id, text)



    except (requests.exceptions.ReadTimeout, socket.timeout, urllib3.exceptions.ReadTimeoutError, socket.gaierror, urllib3.exceptions.NewConnectionError, urllib3.exceptions.MaxRetryError, requests.exceptions.ConnectionError):
        time.sleep(1)
        print('_______Timeout______')