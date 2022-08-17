import requests
import json
import datetime
import time
import random
import os
from bs4 import BeautifulSoup



def schedule(cards_list, week_num):
    # week_num = 1
    url = f'https://mai.ru/education/studies/schedule/index.php?group=%D0%9C9%D0%9E-201%D0%91-20&week={week_num}'

    r = requests.get(url=url, verify=False)
    soup = BeautifulSoup(r.text, 'lxml')
    cards = soup.find('ul', class_='mb-5')
    cards = cards.find_all('li', class_='step-item')
    # cards_list = []
    for card in cards:
        card_data = {}
        date = card.find('div', class_='step-content').find('span', class_='text-body').text.strip().replace('\n', ' ').replace('\t', ' ')
        date = date.replace('&nbsp', ' ').replace('&nbsp;', ' ').replace('\xa0', ' ').lower()
        card_data['date'] = date
        subjects = card.find_all('div', class_='mb-4')
        card_data['lessons'] = []
        for subject in subjects:
            subject_name = ''
            subject_name_data = subject.find('div', class_='d-flex align-items-center justify-content-between')
            lesson_data = {}
            for item in subject_name_data:
                try:
                    name_part = item.text.replace('\n', '').replace('\t', '').strip()
                    if 'ЛК' in name_part:
                        name_part = name_part.replace('ЛК', '').strip()
                        lesson_data['type_of_lesson'] = 'ЛК'
                    elif 'ЛР' in name_part:
                        name_part = name_part.replace('ЛР', '').strip()
                        lesson_data['type_of_lesson'] = 'ЛР'
                    elif 'ПЗ' in name_part:
                        name_part = name_part.replace('ПЗ', '').strip()
                        lesson_data['type_of_lesson'] = 'ПЗ'
                    elif 'Зачет' in name_part:
                        name_part = name_part.replace('Зачет', '').strip()
                        lesson_data['type_of_lesson'] = 'Зачет'
                    elif 'Экзамен' in name_part:
                        name_part = name_part.replace('Экзамен', '').strip()
                        lesson_data['type_of_lesson'] = 'Экзамен'
                    subject_name += name_part
                except Exception as ex:
                    print(ex)
            lesson_data['subject_name'] = subject_name

            subject_time_and_room = subject.find('ul', class_='small')
            subject_time_and_room = subject_time_and_room.find_all('li')
            subject_time = subject_time_and_room[0].text.strip()
            subject_room = subject_time_and_room[-1].text.strip()
            # print(subject_time, subject_room)
            lesson_data['time'] = subject_time
            lesson_data['room'] = subject_room

            card_data['lessons'].append(lesson_data)
        cards_list.append(card_data)
    return cards_list


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
    today_date = datetime.datetime.today()
    # today_day, today_month = today_date.strftime('%d'), today_date.strftime('%m')
    dates = [str((datetime.datetime.today() + datetime.timedelta(delta)).strftime('%d.%m')) for delta in range(0, 100)]

    with open(f'{os.getcwd()}\\Files\\cards_list1.json') as f:
        cards =  json.load(f)
    
    days = []
    for card in cards:
        date = card['date']
        day, month = date_converter(date=date)
        if str(f'{day}.{month}') in dates:
            if len(days) < 5:
                days.append(date)
    return days


def main():
    cards_list = []
    all_weeks = 30
    # all_weeks = 1
    for week_num in range(1, all_weeks + 1):
        try:
            cards_list = schedule(cards_list=cards_list, week_num=week_num)
        except Exception as _ex:
            print(_ex)
        time.sleep(random.randrange(1, 2))
    with open(f'{os.getcwd()}\\Files\\cards_list.json', 'w') as f:
        json.dump(cards_list, f, indent=4, ensure_ascii=False)

    # closest_dates = get_closest_dates()
    # print(closest_dates)



if __name__ == "__main__":
    main()

