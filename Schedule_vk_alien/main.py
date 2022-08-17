import vk_api
import requests
import datetime
import time
import socket
import urllib3
import os
import json
from bs4 import BeautifulSoup
from vk_api.bot_longpoll import VkBotEventType, VkBotLongPoll
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from config import token_vk, group_id

vk_session = vk_api.VkApi(token=token_vk)
vk = vk_session.get_api()
longpoll = VkBotLongPoll(vk_session, group_id)

if not os.path.exists(f'{os.getcwd()}\\Files'):
    os.mkdir(f'{os.getcwd()}\\Files')

if not os.path.exists(f'{os.getcwd()}\\Files\\List'):
    os.mkdir(f'{os.getcwd()}\\Files\\List')

if not os.path.exists(f'{os.getcwd()}\\Files\\Edits'):
    os.mkdir(f'{os.getcwd()}\\Files\\Edits')

if not os.path.exists(f"{os.getcwd()}\\Files\\Edits\\data.json"):
    with open(f"{os.getcwd()}\\Files\\Edits\\data.json", "w") as file:
        file.write('[]')

if not os.path.exists(f"{os.getcwd()}\\Files\\Edits\\users.json"):
    with open(f"{os.getcwd()}\\Files\\Edits\\users.json", "w") as file:
        file.write('["490937725"]')


def sender(id, text=None, preuploaded_doc=None, keyboard=None, inline_keyboard=None, attachments=None):
    post = {
        'user_id': id,
        'random_id': 0
    }

    if text is not None:
        post['message'] = text

    if keyboard is not None:
        post["keyboard"] = keyboard.get_keyboard()

    if inline_keyboard is not None:
        post['keyboard'] = inline_keyboard.get_keyboard()
    
    if keyboard is not None and inline_keyboard is not None:
        post['keyboard'] = keyboard.get_keyboard() and inline_keyboard.get_keyboard()

    if preuploaded_doc is not None:
        post['attachment'] = preuploaded_doc

    if attachments is not None and attachments != []:
        post['attachment'] = ''
        for attachment in attachments:
            type_of_attachment = attachment['type']
            if type_of_attachment == 'doc':
                post['message'] += f'\n\nФайл: "{attachment[f"{type_of_attachment}"]["title"]}"'\
                        f'\n{attachment[f"{type_of_attachment}"]["url"].split("&dl")[0]}'
            else:
                attachment_owner_id = attachment[f'{type_of_attachment}']['owner_id']
                attachment_id = attachment[f'{type_of_attachment}']['id']
                try:
                    attachment_access_key = attachment[f'{type_of_attachment}']['access_key']
                    post['attachment'] += f'{type_of_attachment}{attachment_owner_id}_{attachment_id}_{attachment_access_key},'
                except:
                    post['attachment'] += f'{type_of_attachment}{attachment_owner_id}_{attachment_id},'

    vk_session.method('messages.send', post)


def photo_uploader(doc):
    result = json.loads(requests.post(
        vk.docs.getMessagesUploadServer(type='doc', peer_id=event.object.message['peer_id'])['upload_url'],
        files={'file': open(doc, 'rb')}).text)
    jsonAnswer = vk.docs.save(file=result['file'], title='title', tags=[])

    photo = f"doc{jsonAnswer['doc']['owner_id']}_{jsonAnswer['doc']['id']}"
    return photo


def month_con(month):
    if 'января' in month:
        month = '01'
    elif 'февраля' in month:
        month = '02'
    elif 'март' in month:
        month = '03'
    elif 'апреля' in month:
        month = '04'
    elif 'мая' in month:
        month = '05'
    elif 'июня' in month:
        month = '06'
    elif 'июля' in month:
        month = '07'
    elif 'августа' in month:
        month = '08'
    elif 'сентября' in month:
        month = '09'
    elif 'октября' in month:
        month = '10'
    elif 'ноября' in month:
        month = '11'
    else:
        month = '12' 
    return month


def date_converter(date):
    day = date.split(' ')[1]
    month = date.split(' ')[-1]
    month = month_con(month=month)
    return day, month


def get_closest_dates():
    dates = [str((datetime.datetime.today() + datetime.timedelta(delta)).strftime('%d.%m')) for delta in range(0, 100)]

    with open(f'{os.getcwd()}\\Files\\cards_list.json') as f:
        cards =  json.load(f)
    
    days = []
    for card in cards:
        date = card['date']
        day, month = date_converter(date=date)
        if str(f'{day}.{month}') in dates:
            if len(days) < 5:
                days.append(date)
    return days


def schedule_display(msg):
    dates = get_closest_dates()
    if msg in dates:
        with open(f'{os.getcwd()}\\Files\\cards_list.json') as f:
            cards =  json.load(f)
        text = ''
        for card in cards:
            if msg in card['date']:
                text += f'{card["date"]}\n\n'
                for lesson in card['lessons']:
                    text += f'{lesson["time"]}\n{lesson["subject_name"]} - {lesson["type_of_lesson"]}\n{lesson["room"]}'
                    text += f'\n\n'
    else:
        text = 'Нет расписания на эту дату'
    return text


def msg_check(msg):
    black_list = ['/del', '/add', '/a ' , '/а ' , '/h', '/res']
    for command in black_list:
        if command in msg:
            return False
    return True


while True:
    try:
        for event in longpoll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:

                msg = event.object.message['text'].lower()

                id = event.object.message['from_id']

                print(f'Пользователь {id} - {datetime.datetime.today().strftime("%H.%M")}')


                if 'список' == msg:
                    actual_list = os.listdir(f'{os.getcwd()}\\Files\\List')
                    for item in actual_list:
                        doc = f'{os.getcwd()}\\Files\\List\\{item}'
                        photo = photo_uploader(doc=doc)
                        sender(id, preuploaded_doc=photo)


                elif '/s' == msg or 'начать' == msg or 'назад' == msg:
                    text = 'Выберите: '
                    keyboard = VkKeyboard()
                    keyboard.add_button("Расписание", color=VkKeyboardColor.PRIMARY)
                    keyboard.add_line()
                    keyboard.add_button("Список", color=VkKeyboardColor.POSITIVE)
                    keyboard.add_button("Диск", color=VkKeyboardColor.POSITIVE)
                    keyboard.add_line()
                    keyboard.add_button("Где заказать справки?", color=VkKeyboardColor.NEGATIVE)

                    sender(id=id, text=text, keyboard=keyboard)

                    with open(f"{os.getcwd()}\\Files\\Edits\\users.json") as f:
                        users = json.load(f)

                    counter = 0
                    for user in users:
                        if user == str(id):
                            counter += 1
                    if counter == 0:
                        users.append(str(id))
                        print(f'Пользователь {id} подключился впервые')

                        with open(f"{os.getcwd()}\\Files\\Edits\\users.json", "w") as f:
                            json.dump(users, f, indent=4, ensure_ascii=False)


                # if "посещение" in msg:
                #     text = r'https://docs.google.com/spreadsheets/d/1UMgUdsYupA72H04ruNUOUiAArUc1S6fzJqjAlIqVvdI/edit?usp=sharing'
                #     sender(id=id, text=text)


                elif 'диск' == msg:
                    text = 'ВСЕ ФАЙЛЫ ТУТ \nhttps://drive.google.com/drive/folders/1UzmpRvli60j4MqSKPdEdi0MQDB144ABt?usp=sharing'
                    sender(id=id, text=text)


                elif '/list' in msg:
                    with open(f"{os.getcwd()}\\Files\\Edits\\users.json") as f:
                        users = json.load(f)
                    text = 'Список всех подключенных пользователей\n\n'
                    for user in users:
                        text = f'{text}@id{user}\n'
                    sender(id=id, text=text)


                elif 'где заказать справки?' == msg:
                    text = '❗ Поменялся алгоритм заказа справок с места учёбы. В настоящий момент сделать это можно в личном кабинете ' \
                            'на сайте my.mai.ru в разделе «Учебная часть» подразделе «Запросы», ‼ обязательно указывая ИНН организации, ' \
                            'для которой заказывается справка с места учебы. Получаем готовую справку как и прежде в дирекции института. \n\n' \
                            'ЗАБИРАЕМ ИЗ ДЕКАНАТА, НОЖКАМИ🏃‍♀🏃‍♂ \nГУК зона Б каб .435' \
                            'по предварительному телефонному звонку в деканат ☎ тел.+74991584961.' \
                            'Часы работы деканата уточняем у сотрудников.📞'

                    sender(id=id, text=text)


                elif 'расписание' == msg or 'обновить' == msg:
                    text = 'Выберите: '
                    if 'обновить' in msg:
                        text = "Даты обновлены"
                    keyboard = VkKeyboard()
                    closest_dates = get_closest_dates()
                    for date in closest_dates:
                        keyboard.add_button(f'{date}', color=VkKeyboardColor.PRIMARY)
                        keyboard.add_line()
                    keyboard.add_button("Обновить", color=VkKeyboardColor.PRIMARY)
                    keyboard.add_button("Назад", color=VkKeyboardColor.PRIMARY)

                    sender(id=id, text=text, keyboard=keyboard)


                elif ',' in msg and msg_check(msg):
                    try:
                        text = schedule_display(msg)
                        try:
                            with open(f"{os.getcwd()}\\Files\\Edits\\data.json") as f:
                                edits = json.load(f)
                            for edit in edits:
                                if edit['day'] in msg:
                                    text = f'{text}\n\n❗Изменения в расписании и дз:\n{edit["edit"]}'
                        except:
                            pass

                        sender(id=id, text=text)
                    except:
                        pass


                elif id == 290711560 or id == 490937725:
                    if '/add' in msg:
                        try:
                            edit = msg.split(" -")[1]
                            day = msg.split("/add ")[1].split("-")[0].strip()

                            data = {
                                "day": day,
                                "edit": f'* {edit}'
                            }
                            with open(f"{os.getcwd()}\\Files\\Edits\\data.json") as f:
                                edits = json.load(f)
                            counter = 0
                            for item in edits:
                                if item['day'] == day:
                                    counter += 1
                            if counter == 0:
                                edits.append(data)
                                with open(f"{os.getcwd()}\\Files\\Edits\\data.json", "w") as f:
                                    json.dump(edits, f, indent=4, ensure_ascii=False)
                                text = f'{data["day"]}\n{data["edit"]}'
                                sender(id=id, text=text)
                            else:
                                for item in edits:
                                    if item['day'] == day:
                                        item['edit'] += f'\n* {edit}'
                                        text = f'Комментарий на {item["day"]} уже существует\n\nОбновленный комментарий:\n{item["day"]}\n{item["edit"]}'
                                        sender(id=id, text=text)
                                with open(f"{os.getcwd()}\\Files\\Edits\\data.json", "w") as f:
                                    json.dump(edits, f, indent=4, ensure_ascii=False)
                        except:
                            text = 'Не получилось добавить комментарий, попробуйте еще раз'
                            sender(id=id, text=text)


                    elif "/del" in msg:
                        try:
                            text = 'Нечего удалять'
                            day = msg.split("/del ")[1]
                            with open(f"{os.getcwd()}\\Files\\Edits\\data.json") as f:
                                edits = json.load(f)

                            for item in edits:
                                if item['day'] == day:
                                    edits.remove(item)
                                    text = f'Комментарий на {day} удален'

                            with open(f"{os.getcwd()}\\Files\\Edits\\data.json", "w") as f:
                                json.dump(edits, f, indent=4, ensure_ascii=False)

                            sender(id=id, text=text)
                        except:
                            text = 'Не получилось удалить комментарий, попробуйте еще раз'
                            sender(id=id, text=text)


                    elif '/h' == msg:
                        text = 'Введите "/add дата(в формате день месяц) -комментарий" для добавления комментария' \
                               ' [ в самом комментарии нельзя писать " -" . Если нужно написать "-", ' \
                               'то "-" должен быть без пробела перед ним ]\n' \
                               'Пример: /add 17 января -Экзамен по предмету\n\n' \
                               'Введите "/del дата(в формате день месяц)" для удаления комментария\n' \
                               'Пример: /del 17 января\n\n' \
                               'Введите "/a текст уведомления"  [ в тексте уведомления нельзя писать "/a" ]\n' \
                               'Пример: /a уведомление\n\n' \
                               'Введите "/list", чтобы увидеть список всех подключенных пользователей\n\n' \
                               'Введите "/res" для сброса кнопок всем пользователям'
                        sender(id=id, text=text)


                    elif '/res' == msg:
                        with open(f"{os.getcwd()}\\Files\\Edits\\users.json") as f:
                            users = json.load(f)
                        keyboard = VkKeyboard()
                        keyboard.add_button("Расписание", color=VkKeyboardColor.PRIMARY)
                        keyboard.add_line()
                        keyboard.add_button("Список", color=VkKeyboardColor.PRIMARY)
                        keyboard.add_button("Диск", color=VkKeyboardColor.PRIMARY)
                        keyboard.add_line()
                        keyboard.add_button("Где заказать справки?", color=VkKeyboardColor.PRIMARY)
                        for user in users:
                            text = 'Кнопки сброшены'
                            sender(id=user, text=text, keyboard=keyboard)


                    elif '/a ' in msg or '/а ' in msg:
                        try:
                            if '/a ' in msg:
                                announcement = event.object.message['text'].split('/a ')[1]
                            else:
                                announcement = event.object.message['text'].split('/а ')[1]
                            attachments = []
                            if event.object.message['attachments'] != []:
                                attachments = event.object.message['attachments']
                            with open(f"{os.getcwd()}\\Files\\Edits\\users.json") as f:
                                users = json.load(f)
                            for user in users:
                                try:
                                    sender(id=user, text=announcement, attachments=attachments)
                                except:
                                    pass
                        except:
                            text = "Не получилось создать уведомление"
                            sender(id=id, text=text)



    except (requests.exceptions.ReadTimeout, socket.timeout, urllib3.exceptions.ReadTimeoutError, socket.gaierror, urllib3.exceptions.NewConnectionError, urllib3.exceptions.MaxRetryError, requests.exceptions.ConnectionError, vk_api.exceptions.ApiError):
        time.sleep(1)
        print('_______Timeout______')

