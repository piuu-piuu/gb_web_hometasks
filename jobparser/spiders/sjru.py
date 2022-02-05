import scrapy
from scrapy.http import HtmlResponse
from items import JobparserItem


class SjruSpider(scrapy.Spider):
    name = 'sjru'
    allowed_domains = ['superjob.ru']
    start_urls = [
        'https://russia.superjob.ru/vacancy/search/?keywords=Python%20junior']

    def parse(self, response: HtmlResponse):
        next_page = response.xpath(
            "//a[contains(@class,'dalshe')]/@href").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

        links = response.xpath(
            "//div[contains(@class,'vacancy-item')]//a[contains(@target,'_blank')]/@href").getall()
        for link in links:
            yield response.follow(link, callback=self.vacancy_parse)

    def vacancy_parse(self, response: HtmlResponse):
        name = response.xpath("//title/text()").get()
        salary = response.xpath(
            '//div[contains(@class, "vacancy-base-info")]/*/*/*/*/span/span/text()').getall()

        url = response.url
        yield JobparserItem(name=name, salary=salary, url=url)
