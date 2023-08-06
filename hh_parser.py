import requests
from bs4 import BeautifulSoup
from fake_headers import Headers
import unicodedata
from pprint import pprint
import json


def get_headers():  # Получаем заголовки
	header_gen = Headers(browser='chrome', os='win')
	return header_gen.generate()


def get_job_list():  # Получаем список вакансий
	response = requests.get('https://spb.hh.ru/search/vacancy?text=python&area=1&area=2', headers=get_headers())
	hh_main = BeautifulSoup(response.text, features='lxml')
	job_list = hh_main.find('div', id='a11y-main-content')
	job_list_tags = job_list.find_all('div', class_='serp-item')
	return job_list_tags


def is_actual(vacansy_main):  # Проверяем вакансию на наличие требуемых ключевых слов
	keyword_tags = vacansy_main.find_all('span', class_='bloko-tag__section bloko-tag__section_text')
	for key in keyword_tags:
		if key.text == 'Django' or key.text == 'Flask':
			return True


def find_information(vacansy):  # Получаем всю нужную информацию по вакансиям
	title_tag = vacansy.find('a')
	title_text = title_tag.text
	link = title_tag['href']
	response2 = requests.get(link, headers=get_headers())
	vacansy_main = BeautifulSoup(response2.text, features='lxml')
	if is_actual(vacansy_main):
		zp = 'Не указано'
		direction = 'Не указан'
		zp_tag = vacansy.find('span', class_='bloko-header-section-2')
		company_tag = vacansy_main.find('span', class_='vacancy-company-name')
		company_name = company_tag.find('span', class_='bloko-header-section-2 bloko-header-section-2_lite').text
		direction_tag = vacansy_main.find('a', class_='bloko-link bloko-link_kind-tertiary bloko-link_disable-visited')
		if direction_tag:
			direction_tags = direction_tag.find_all('span')
			direction = ''
			for dir_ in direction_tags:
				if dir_.text not in direction:
					direction += dir_.text
		if zp_tag:
			zp = zp_tag.text
		return zp, title_text, company_name, direction, link
	else:
		return False


def get_result():  # Записываем полученные данные в словарь
	result = []
	job_list_tags = get_job_list()
	for vacansy in job_list_tags:
		if find_information(vacansy):
			zp, title_text, company_name, direction, link = find_information(vacansy)
			result.append({
				'Название': title_text,
				'Ссылка': link,
				'Зарплата': unicodedata.normalize("NFKD", zp),
				'Название компании': unicodedata.normalize("NFKD", company_name),
				'Адрес': unicodedata.normalize("NFKD", direction)
			})
	pprint(result)
	return result


def get_json():  # Полученный словарь записываем в Json
	with open('result.json', "w", encoding='utf-8') as file:
		result = get_result()
		json.dump(result, file, ensure_ascii=False)


if __name__ == '__main__':  # Ну тут собственно запуск программы
	get_json()
