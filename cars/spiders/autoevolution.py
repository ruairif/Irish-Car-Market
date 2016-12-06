# -*- coding: utf-8 -*-
import scrapy


class AutoevolutionSpider(scrapy.Spider):
    name = "autoevolution"
    allowed_domains = ["autoevolution.com"]
    start_urls = (
        'http://www.autoevolution.com/cars',
    )

    def parse(self, response):
        for brand in response.css('h5 > a::attr(href)').extract():
            yield scrapy.Request(brand, callback=self.parse_models)

    def parse_models(self, response):
        for model in response.css('.carmod > div > a::attr(href)').extract():
            yield scrapy.Request(model, callback=self.parse_cars)

    def parse_cars(self, response):
        for car in response.css('.carmodel > div > a.upcase::attr(href)').extract():
            yield scrapy.Request(car, callback=self.parse_car)

    def parse_car(self, response):
        item = {}
        for section in response.css('dl'):
            names = section.css('dt > em::text').extract()
            values = section.css('dd')
            for name, value in zip(names, values):
                value = value.css('*::text').extract()
                if value:
                    value = value[-1].strip()
                if not value or value == '-':
                    continue
                item[name] = value
        item['brochures'] = response.css('.brosuri > a::attr(href)').extract()
        item['engines'] = response.css('li[onclick]::text').extract()
        item['news'] = ' '.join(response.css('.newstext *::text').extract())
        item['image_urls'] = response.css('.vslide > a::attr(href)').extract()
        item['url'] = response.css('h1.seriestitle > a::attr(href)').extract()
        item['title'] = response.css('h1.seriestitle > a::text').extract()
        item['years'] = response.css('h1.seriestitle > a > span::text').extract()
        item['brand'] = response.css('.breadcrumb2 > span > span > a[itemprop="item"]::attr(title)').extract()[-1]
        item = {k: v[0].strip() if isinstance(v, list) and len(v) == 1 else v
                for k, v in item.items() if v}
        return item
