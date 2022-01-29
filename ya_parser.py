from pymongo import MongoClient
from lxml import html
from pprint import pprint
import requests

#  чтобы не раздражать Яндекс ))
def dump(url='https://yandex.ru/news'):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36',
    }
    response = requests.get(url, headers=headers).text
    with open("response.html", 'w', encoding='utf-8') as f:
        f.write(response)

def subparse(news):
    info = {}
    title = news.xpath(".//h2[@class='mg-card__title']/a/text()")[0].replace('\xa0',' ')
    time = news.xpath(".//span[@class='mg-card-source__time']/text()")[0]
    source = news.xpath(".//span[@class='mg-card-source__source']//a/text()")[0]
    link = news.xpath(".//h2[@class='mg-card__title']/a/@href")[0]
    # print(title, time, source, link)
    info['title'], info['time'], info['source'], info['link'] = title, time, source, link
    return info

def ya_parse():
    news_list = {}
    with open("response.html", 'r', encoding='utf-8') as f:
        response = str(f.read())
    dom = html.fromstring(response)
    sections = dom.xpath("//section[@aria-labelledby]")
    for section in sections:
        titles = section.xpath(".//h1//text()")
        for section_title in titles:
            info_list = []
            if section_title == 'Главное':
                main_info = section.xpath(".//div[contains(@class, 'mg-grid__col_xs_8')]")
                info_list.append(subparse(main_info[0]))
                news_info = section.xpath(".//div[contains(@class, 'mg-grid__col_xs_4')]")
                for news in news_info:
                    info_list.append(subparse(news))
                news_list[section_title] = info_list
            else:
                main_info = section.xpath(".//div[contains(@class, 'mg-grid__col_xs_4')]")
                info_list.append(subparse(main_info[0]))
                news_info = section.xpath(".//div[contains(@class, 'mg-grid__col_xs_6')]")
                for news in news_info:
                    info_list.append(subparse(news))
                news_list[section_title] = info_list
    return(news_list)


if __name__ == '__main__':
    dump()
    client = MongoClient('127.0.0.1', 27017)
    db = client['Yandex-News']
    topic = 'Пермь'
    result = ya_parse()[topic]
    # pprint(result)
    db.parsing_result.insert_many(result)
