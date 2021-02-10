import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from rcibank.items import Article


class RciSpider(scrapy.Spider):
    name = 'rci'
    start_urls = ['http://www.rcibank.co.uk/inside-rci/blog']

    def parse(self, response):
        articles = response.xpath('//div[@class="col-12 col-md-4"]')
        for article in articles:
            link = article.xpath('.//a[@class="read-more-page"]/@href').get()
            date = article.xpath('.//div[@class="date"]//text()').get().strip()
            yield response.follow(link, self.parse_article, cb_kwargs=dict(date=date))

    def parse_article(self, response, date):
        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//div[@class="title-row-top"]/text()').get().strip()
        date = datetime.strptime(date, '%d %b %Y')
        date = date.strftime('%Y/%m/%d')
        content = response.xpath('//div[@class="body"]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
