import requests
from bs4 import BeautifulSoup
import pandas as pd

search_string = input('Input search terms or hit enter for default search:')
if not search_string:
    search_string = 'python парсинг'

uri = 'https://hh.ru/search/vacancy'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36',
}
params = {
    'salary' : '',
    'text' : search_string,
    'page' : '0'
}

dom = BeautifulSoup(requests.get(uri,headers=headers, params=params).text, 'html.parser')
job_list = dom.find_all('div', {'class': ['vacancy-serp-item', 'vacancy-serp-item_redesigned']})
jobs = []
page_num = 0

while job_list:
    for job in job_list:
        title = job.find('a', {'data-qa':'vacancy-serp__vacancy-title'})
        job_dict = {'title' : title.text.replace(',', ';')}
        job_dict['link'] = title.get('href').split('?')[0]
        salary = job.find('span', {'data-qa':'vacancy-serp__vacancy-compensation'})

        if salary:
            salary = salary.getText().replace('\u202f', '').replace('\xa0', '')
            salary_list = salary.split()
            if salary_list[0].isalpha():
                job_dict['salary_min'] = None
                job_dict['salary_max'] = int(salary_list[1])
                job_dict['salary_currency'] = salary_list[-1]
            else:
                job_dict['salary_min'] = int(salary_list[0])
                job_dict['salary_max'] = int(salary_list[2])
                job_dict['salary_currency'] = salary_list[-1]

        else:
            job_dict['salary_min'] = None
            job_dict['salary_max'] = None
            job_dict['salary_currency'] = None

        job_dict['source'] = 'hh.ru'
        jobs.append(job_dict)

    page_num += 1
    params['page'] = str(page_num)
    dom = BeautifulSoup(requests.get(uri, headers=headers, params=params).text, 'html.parser')
    job_list = dom.find_all('div', {'class': ['vacancy-serp-item', 'vacancy-serp-item_redesigned']})

df = pd.DataFrame(jobs)
print (df.to_string())
df.to_csv('output.csv', sep='\t', encoding='utf-8')