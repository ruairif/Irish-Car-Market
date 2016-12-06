# -*- coding: utf-8 -*-
import scrapy
from itertools import chain
from six.moves.urllib.parse import urljoin


class CarsirelandSpider(scrapy.Spider):
    name = "carsireland"
    allowed_domains = ["www.carsireland.ie"]
    start_urls = (
        'http://www.carsireland.ie/search-results.php?max_price=120000&per_page=50/',
    )

    def parse(self, response):
        for url in response.css('h3 > a::attr(href)').extract():
            yield scrapy.Request(urljoin(response.url, url),
                                 callback=self.parse_car)
        for url in response.css('#pagination > a::attr(href)').extract():
            yield scrapy.Request(urljoin(response.url, url),
                                 callback=self.parse)

    def parse_car(self, response):
        item = {}
        for row in response.css('table tr'):
            name = row.css('th::text').extract_first()
            value = row.css('td::text').extract_first()
            if not (name and value):
                continue
            item[name.strip().strip(':')] = value.strip()
        item['price'] = response.css('#car-details > span::text').extract_first()
        item['details'] = response.css('#details-left p::text').extract_first()
        item['name'] = response.css('h1::text').extract_first()
        images = response.css('#gallery a::attr(href), #gallery img::attr(src)').extract()
        item['images'] = [i for i in images if not i.endswith('blank.gif')]
        item['url'] = response.url
        item['seller'] = {
            'address': list(filter(bool, (a.strip() for a in response.css('address::text').extract()))),
            'name': response.css('address > span::text').extract_first(),
            'numbers': [n.strip() for n in chain(*(t.split('/') for t in response.css('#contact dd::text').extract()))],
            'location': response.css('#sat_nav > p::text').extract(),
            'website': response.css('#contact a::text').extract_first()
        }
        return item
