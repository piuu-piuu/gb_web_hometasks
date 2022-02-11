import scrapy
from scrapy.http import HtmlResponse
from scrapy.loader import ItemLoader
from items import LMparserItem


class LmruSpider(scrapy.Spider):
    name = 'lmru'
    allowed_domains = ['leroymerlin.ru']
    start_urls = [
        'https://leroymerlin.ru/catalogue/pilomaterialy/']
    # 'https://leroymerlin.ru/catalogue/kuhonnye-smesiteli/']

    def parse(self, response: HtmlResponse):
        next_page = response.xpath(
            "//a[contains(@aria-label,'Следующая страница')]/@href").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

        links = response.xpath('//a[@data-qa="product-name"]/@href').getall()
        for link in links:
            yield response.follow(link, callback=self.item_parse)

    def item_parse(self, response: HtmlResponse):
        loader = ItemLoader(item=LMparserItem(), response=response)
        loader.add_xpath('name', "//h1/text()")
        loader.add_xpath('price', "//span[@slot='price']/text()")
        loader.add_xpath(
            'photos', "//picture[@slot='pictures']/source[contains(@media, '1024')]/@data-origin")
        loader.add_value('url', response.url)
        yield loader.load_item()
