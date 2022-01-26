import requests
from bs4 import BeautifulSoup
import pandas as pd

def parse_salary(salary):
    if salary:
        salary = salary.getText().replace('\u202f', '').replace('\xa0', '')
        salary_list = salary.split()
        if salary_list[0] == 'от':
            salary_min = int(salary_list[1])
            salary_max = None
            salary_currency = salary_list[-1]
        elif salary_list[0] == 'до':
            salary_min = None
            salary_max = int(salary_list[1])
            salary_currency = salary_list[-1]
        else:
            salary_min = int(salary_list[0])
            salary_max = int(salary_list[2])
            salary_currency = salary_list[-1]
    else:
        salary_min = None
        salary_max = None
        salary_currency = None
    return salary_min, salary_max, salary_currency


def parse_jobs(search_string):

    class pageIterator:

        def __iter__(self):
            self.x = 0
            return self

        def __next__(self):
            params['page'] = str(self.x)
            dom = BeautifulSoup(requests.get(uri, headers=headers,
                                             params=params).text, 'html.parser')
            job_list = dom.find_all(
                'div', {'class': ['vacancy-serp-item', 'vacancy-serp-item_redesigned']})
            self.x += 1
            return job_list


    pages = pageIterator()
    search_page = iter(pages)
    uri = 'https://hh.ru/search/vacancy'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36',
    }
    params = {
        'salary': '',
        'text': search_string,
        'page': '0'
    }
    jobs = []
    job_list = next(search_page)
    while job_list:
        for job in job_list:
            title = job.find('a', {'data-qa': 'vacancy-serp__vacancy-title'})
            job_dict = {'title': title.text}
            job_dict['link'] = title.get('href').split('?')[0]
            salary = job.find(
                'span', {'data-qa': 'vacancy-serp__vacancy-compensation'})
            job_dict['salary_min'], job_dict['salary_max'], job_dict['salary_currency'] = parse_salary(salary)
            job_dict['source'] = 'hh.ru'
            jobs.append(job_dict)
        job_list = next(search_page)
    return jobs


if __name__ == '__main__':
    jobs = parse_jobs('2D художник')
    df = pd.DataFrame(jobs)
    print(df.to_string())
