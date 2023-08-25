import json
import re
import unicodedata
import fake_headers
import requests
from bs4 import BeautifulSoup
from pprint import pprint
from fake_headers import Headers

headers_gen = fake_headers.Headers(browser='chrome', os='win')
params = {
    'currency_code': 'USD',
    'items_on_page': 20
}
for page in range(0, 3):
    response = requests.get(f'https://spb.hh.ru/search/vacancy?text=python&area=1&area=2&page={page}', params=params,
                            headers=headers_gen.generate())
    html_data = response.text

    hh_main = BeautifulSoup(html_data, 'lxml')
    vacancy_list_tag = hh_main.find_all('div', class_='vacancy-serp-item__layout')

    vacancy_parsed = {}
    for vacancy_tag in vacancy_list_tag:
        header_tag = vacancy_tag.find('h3')
        a_tag = header_tag.find('a')
        link = a_tag['href']

        vacancy_compensation_tag = vacancy_tag.find('span', class_='bloko-header-section-2')
        if vacancy_compensation_tag == None:
            vacancy_compensation_text = 'Зарплата не указана'
        else:
            vacancy_compensation_text = unicodedata.normalize("NFKD", vacancy_compensation_tag.text)

        vacancy_responce = requests.get(link, headers=headers_gen.generate())
        vacancy = BeautifulSoup(vacancy_responce.text, 'lxml')
        vacancy_description_tag = vacancy.find('div', class_='g-user-content')
        if vacancy_description_tag != None:
            vacancy_description_text = vacancy_description_tag.text

        company_name_tag = vacancy.find('span', class_='vacancy-company-name')
        if company_name_tag != None:
            company_name_text = unicodedata.normalize("NFKD", company_name_tag.text)

        city_tag = vacancy.find(attrs={'data-qa': 'vacancy-view-location'})
        if city_tag == None:
            city_text = 'Город не указан'
        else:
            city_text = city_tag.text

        if re.search(r'\bDjango\b|\bFlask\b', vacancy_description_text):
            if '₽' in vacancy_compensation_text:
                vacancy_parsed[company_name_text] = {
                    "link": link,
                    'salary': vacancy_compensation_text,
                    'company': company_name_text,
                    'city': city_text
                }


with open('vacancy_parsed.json', 'w', encoding='utf-8') as f:
    json.dump(vacancy_parsed, f)

