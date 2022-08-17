import requests
import datetime
import os
import json
import random
import time

from config import token_tg
from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils.markdown import hbold, hunderline, hcode, hlink, hitalic
from aiogram.dispatcher.filters import Text

bot = Bot(token=token_tg, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)

if not os.path.exists(f'{os.getcwd()}\\Data'):
    os.mkdir(f'{os.getcwd()}\\Data')

if not os.path.exists(f'{os.getcwd()}\\Data\\data.json'):
    with open(f'{os.getcwd()}\\Data\\data.json', 'w') as f:
        f.write(r'[]')

if not os.path.exists(f'{os.getcwd()}\\Data\\config.txt'):
    with open(f'{os.getcwd()}\\Data\\config.txt', 'w') as f:
        f.write(f'easy_questions = 8\nmax_range_in_divide = 200\nmax_range_in_multiply = 20\nmax_stages = 10')
    easy_questions = 8
    max_range_in_divide = 200
    max_range_in_multiply = 20
    max_stages = 10
else:
    with open(f'{os.getcwd()}\\Data\\config.txt', "r") as f:
        data_in_config = [row.strip() for row in f]
    easy_questions = 8
    max_range_in_divide = 200
    max_range_in_multiply = 20
    max_stages = 10
    for item in data_in_config:
        if 'easy_questions' in item:
            easy_questions = int(item.split(' =')[1].strip())
        if 'max_range_in_divide' in item:
            max_range_in_divide = int(item.split(' =')[1].strip())
        if "max_range_in_multiply" in item:
            max_range_in_multiply = int(item.split(' =')[1].strip())
        if 'max_stages' in item:
            max_stages = int(item.split(' =')[1].strip())

if not os.path.exists(f'{os.getcwd()}\\Data\\answers.txt'):
    with open(f'{os.getcwd()}\\Data\\answers.txt', 'w') as f:
        f.write('')

@dp.message_handler(commands="start")
async def start(message: types.Message):
    start_buttons = ["Начать тест"]
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*start_buttons)
    await message.answer("Начать тест?", reply_markup=keyboard, disable_notification=True)
    print(f"Пользователь {message.from_user.id} подключился")
    with open(f'{os.getcwd()}\\Data\\data.json', "r") as f:
        data = json.load(f)
        user_exists = 0
        for item in data:
            if item["user_id"] == message.from_user.id:
                user_exists += 1
        if user_exists == 0:
            print(f"Новый пользователь {message.from_user.id}")
            new_user = {
                "user_id": message.from_user.id,
                'stage': 0,
                'right_answers_amount': 0,
                'wrong_answers_amount': 0,
                'list_of_wrongs': []
            }
            data.append(new_user)

    with open(f'{os.getcwd()}\\Data\\data.json', "w") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


@dp.message_handler(Text(equals='Начать тест'))
async def start_test(message: types.Message):
    a = random.randrange(0, 10)
    b = random.randrange(0, 10)
    question_int = a * b
    question = f'{a} * {b}'
    with open(f'{os.getcwd()}\\Data\\data.json', 'r') as f:
        users_data = json.load(f)
    for user in users_data:
        if user['user_id'] == message.from_user.id:
            user['list_of_wrongs'] = []
            user['stage'] = 0
            user['right_answers_amount'] = 0
            user['wrong_answers_amount'] = 0
            user['right_answer'] = question_int
            user['question'] = question
            user['stage'] += 1
            await message.answer(f'{user["stage"]}. {question}', disable_notification=True)
    with open(f'{os.getcwd()}\\Data\\data.json', 'w') as f:
        json.dump(users_data, f, indent=4, ensure_ascii=False)


list_of_numbers = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]        
for number in list_of_numbers:
    @dp.message_handler(Text(contains=str(number)))
    async def testing(message: types.Message):
        with open(f'{os.getcwd()}\\Data\\data.json', 'r') as f:
            users_data = json.load(f)
        
        for user in users_data:
            if user['user_id'] == message.from_user.id:
                list_of_wrongs = user['list_of_wrongs']
                question = user['question']
                user['stage'] += 1 
                if user['right_answer'] == int(message.text):
                    user['right_answers_amount'] += 1
                else:
                    user['wrong_answers_amount'] += 1
                    list_of_wrongs.append(f'{user["stage"] - 1}. {user["question"]} = {user["right_answer"]} ({int(message.text)})')
                user['list_of_wrongs'] = list_of_wrongs
                
                if user['stage'] > max_stages:
                    text = f'Правильных ответов - {user["right_answers_amount"]}\n'\
                            f'Неправильных ответов - {user["wrong_answers_amount"]}\n\n'
                    if len(user['list_of_wrongs']) != 0:
                        text += 'Неправильные ответы:\n'
                    for item in user['list_of_wrongs']:
                        text += f'{item}\n'
                    if user['right_answers_amount'] / user['stage'] <= 0.5:
                        text += '\nПОПРОБУЙ ЕЩЕ РАЗ!\n'
                    if len(user['list_of_wrongs']) == 0:
                        text += 'Молодец!\n'
                    with open(f'{os.getcwd()}\\Data\\answers.txt', 'a') as file:
                        file.write(f'User id - {user["user_id"]}\n')
                        for item in user["list_of_wrongs"]:
                            file.write(f'{item}\n')
                        if len(user['list_of_wrongs']) == 0:
                            file.write('Ошибок нет\n')
                        file.write(f'------------------------\n')

                    text += '\nНажмите кнопку "Начать тест" для повтора'

                    await message.answer(text, disable_notification=True)
                    user['stage'] = 0
                else:
                    if user['stage'] < easy_questions + 1:
                        variation = 1
                    else:
                        variation = random.randrange(2, 4)
                    
                    if variation == 1:
                        a = random.randrange(0, 10)
                        b = random.randrange(0, 10)
                        question = f'{a} * {b}'
                        question_int = a * b
                        question_answer = f'{a} * {b} = {question_int}'
                    elif variation == 2:
                        a = random.randrange(11, max_range_in_multiply + 1)
                        b = random.randrange(0, 10)
                        question = f'{a} * {b}'
                        question_int = a * b
                        question_answer = f'{a} * {b} = {question_int}'
                    else:
                        while True:
                            a = random.randrange(0, max_range_in_divide + 1)
                            b = random.randrange(1, 21)
                            if a % b == 0:
                                question = f'{a} : {b}'
                                question_int = a // b
                                question_answer = f'{a} : {b} = {question_int}'
                                break
                    user['question'] = question
                    user['right_answer'] = question_int
                    await message.answer(f'{user["stage"]}. {question}', disable_notification=True)
        
                
    
    
        with open(f'{os.getcwd()}\\Data\\data.json', 'w') as f:
            json.dump(users_data, f, indent=4, ensure_ascii=False)
    
    
if __name__ == '__main__':
    executor.start_polling(dp)
