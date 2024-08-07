import requests
from itertools import count
import os
from terminaltables import AsciiTable
from dotenv import load_dotenv


def get_salary(salary_from=None, salary_to=None):
    if salary_from and salary_to:
        salary = (salary_from + salary_to) / 2
    elif salary_from:
        salary = salary_from * 1.2
    elif salary_to:
        salary = salary_to * 0.8
    else:
        salary = None
    return salary


def get_vacancies_hh(lang, page=0):
    city = '1'
    period = 30
    params = {
        'text': f'программист {lang}',
        'area': city,
        'period': period,
        'page': page
    }
    response = requests.get('https://api.hh.ru/vacancies', params=params)
    response.raise_for_status()
    return response.json()


def predict_rub_salary_for_hh():
    languages = ['Ruby', 'Python']
    vacancy_statistics = {}
    for lang in languages:
        all_salaries = []
        for page in count(0):
            vacancies = get_vacancies_hh(lang, page=page)
            if page >= vacancies['pages'] - 1:
                break
            for vacancy in vacancies['items']:
                salary = vacancy.get('salary')
                if salary and salary['currency'] == 'RUR':
                    hh_salary = get_salary(salary['from'], salary['to'])
                    if hh_salary:
                        all_salaries.append(hh_salary)
        average_salary = None
        if all_salaries:
            average_salary = int(sum(all_salaries) / len(all_salaries))
        vacancy_statistics[lang] = {
            'vacancies_found': vacancies['found'],
            'vacancies_processed': len(all_salaries),
            'average_salary': average_salary
        }        
    return vacancy_statistics


def get_vacancies_sj(lang, sj_key, page=0):
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
    languages = ['C']
    vacancy_statistics = {}
    for lang in languages:
        all_salaries = []
        for page in count(0, 1):
            vacancies = get_vacancies_sj(lang, sj_key, page=page)
            if not vacancies['objects']:
                break
            for vacancy in vacancies['objects']:
                sj_salary = get_salary(vacancy['payment_from'], vacancy['payment_to'])
                if sj_salary:
                    all_salaries.append(sj_salary)
        average_salary = None
        if all_salaries:
            average_salary = int(sum(all_salaries) / len(all_salaries))
        vacancy_statistics[lang] = {
            "vacancies_found": vacancies['total'],
            "vacancies_processed": len(all_salaries),
            "average_salary": average_salary
        }
    return vacancy_statistics


def create_table(title, statistic):
    statistics_table = [
        ['Язык программирования', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зп']
    ]
    for lang, table_content in statistic.items():
        statistics_table.append(
            [
                lang, 
                table_content['vacancies_found'], 
                table_content['vacancies_processed'], 
                table_content['average_salary']
            ]
        )
    table = AsciiTable(statistics_table, title)
    return table.table
    

def main():
    load_dotenv()
    sj_key = os.environ['SJ_KEY']
    print(create_table('HeadHunter Moscow', predict_rub_salary_for_hh()))
    print(create_table('SuperJob Moscow',  predict_rub_salary_for_superJob(sj_key)))


if __name__ == '__main__':
    main()
