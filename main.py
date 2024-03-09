import requests
from itertools import count
import os
from terminaltables import AsciiTable
from dotenv import load_dotenv


def get_hh(lang, page=0):
    params = {
        'text': f'программист {lang}',
        'area': '1',
        'period': 30,
        'page': page
    }
    response = requests.get('https://api.hh.ru/vacancies', params=params)
    response.raise_for_status()
    return response.json()


def predict_rub_salary_for_hh():
    languages = ['Ruby', 'Python']
    info_vacancy = {}
    for lang in languages:
        all_salaries = []
        for page in count(0):
            vacancy = get_hh(lang, page=page)
            if page >= vacancy['pages'] - 1:
                break
            for item in vacancy['items']:
                salary = item.get('salary')
                if salary and salary['currency'] == 'RUR':
                    if salary['from'] is None:
                        all_salaries.append(salary['to'] * 0.8)
                    elif salary['to'] is None:
                        all_salaries.append(salary['from'] * 1.2)
                    else:
                        all_salaries.append((salary['from'] + salary['to']) / 2)
        info_vacancy[lang] = {
            'vacancies_found': vacancy['ncyfound'],
            'vacancies_processed': len(all_salaries),
            'average_salary': int(sum(all_salaries) / len(all_salaries))
        }        
    return info_vacancy


def get_sj(lang, sj_key, page=0):
    url = 'https://api.superjob.ru/2.0/vacancies'
    headers = {
        'X-Api-App-Id': sj_key
    }
    params = {
        'keyword' : f'программист {lang}',
        'town' : 'Moscow',
    }
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()
    

def predict_rub_salary_for_superJob(sj_key):
    languages = ['Go']
    info_vacancy = {}
    for lang in languages:
        all_salaries = []
        for page in count(0):
            vacancy = get_sj(lang, sj_key, page=page)
            if not vacancy['objects']:
                break
            for object in vacancy['objects']:
                if object['payment_to'] and object['payment_from']:
                    all_salaries.append((object['payment_from'] + object['payment_to']) / 2)
                elif object['payment_from'] is None:
                    all_salaries.append(object['payment_to'] * 0.8)
                elif object['payment_to'] is None:
                    all_salaries.append(object['payment_from'] * 1.2)
        average_salary = None
        if all_salaries:
            average_salary = int(sum(all_salaries) / len(all_salaries))
        info_vacancy[lang] = {
            "vacancies_found": vacancy['total'],
            "vacancies_processed": len(all_salaries),
            "average_salary": average_salary
            }
    return info_vacancy
    

def create_table(title, statistic):
    table_data = [
        ['Язык программирования', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зп']
    ]
    for lang, info in statistic.items():
        table_data.append([lang, info['vacancies_found'], info['vacancies_processed'], info['average_salary']])
    table = AsciiTable(table_data, title)
    return table.table
    

def main():
    load_dotenv()
    sj_key = os.environ['SJ_KEY']
    print(create_table('HeadHunter Moscow', predict_rub_salary_for_hh()))
    print(create_table('SuperJob Moscow',  predict_rub_salary_for_superJob(sj_key)))


if __name__ == '__main__':
    main()