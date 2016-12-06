# -*- coding: utf-8 -*-
import json
import re

from calendar import timegm
from collections import OrderedDict
from datetime import datetime, timedelta
from random import randint

from six.moves.urllib.parse import urlparse, urlunparse

import dateparser
import scrapy
import requests


STARTED_AT = datetime.now()
DONEDEAL_FIELDS = (
    'county', 'currency', 'description', 'friendlyUrl', 'header', 'id',
    'publisherName', 'state', 'spotlight', 'section', 'wanted', 'userSaved',
    'publisherPhoneEnc', 'emailResponse', 'phoneResponse', 'views', 'seller')
DEALER_FIELDS = (
    'address', 'latitude', 'longitude', 'name', 'type', 'websiteURL'
)
SEARCH_URL = 'https://www.donedeal.ie/search/api/v4/find/'
HEADERS = {
    'Host': 'www.donedeal.ie',
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:49.0) Gecko/20100101 Firefox/49.0',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Content-Type': 'application/json;charset=utf-8',
    'Referer': 'https://www.donedeal.ie/cars',
}

POST_ARGS = OrderedDict([
    ("section", "cars"),
    ("adType", "forsale"),
    ("sort", "relevance desc"),
    ("priceType", "Euro"),
    ("mileageType", "Kilometres"),
    ("max", 30),
    ("start", 0)
])


class DonedealSpider(scrapy.Spider):
    name = 'donedeal'
    allowed_domains = ['donedeal.ie']

    def start_requests(self):
        while True:
            dumped = json.dumps(POST_ARGS)
            r = requests.post(SEARCH_URL, headers=HEADERS,
                              data=dumped)
            data = r.json()
            if not data.get('ads', []):
                return
            for ad in data.get('ads', []):
                url = urlunparse(urlparse(ad['friendlyUrl'])._replace(query=''))
                yield scrapy.Request(url, callback=self.parse_car)
            next_start = data.get('pagingCounts', {}).get('nextStart')
            if next_start == 0:
                break
            POST_ARGS['start'] = next_start

    def parse_car(self, response):
        script = response.xpath(
            '//script[contains(text(), "window.adDetails")]/text()'
        ).extract_first()
        jsondata = re.findall(r'window.adDetails\s=\s(.+)', script)
        if not jsondata:
            self.logger.warning('No ad details found for: %s' % response.url)
            return
        jsondata = jsondata[0].strip('; ')
        car_info = json.loads(jsondata)
        item = {}
        if car_info.get('age'):
            item['posted'] = dateparser.parse(car_info['age'])
        for attribute in car_info.get('displayAttributes', []):
            item[attribute['displayName']] = attribute['value']
        photos = [p['large'] for p in car_info.get('photos', [])]
        if photos:
            item['images'] = photos
        for key in DONEDEAL_FIELDS:
            value = car_info.get(key)
            if value:
                item[key] = value
        item['price'] = car_info.get('price', '').replace(',', '')
        if car_info.get('dealer'):
            for key in DEALER_FIELDS:
                value = car_info['dealer'].get(key)
                if value:
                    item[key] = value
        item['drop'] = 'state' in item and item['state'] == 'Published'
        item['crawl_at'] = recrawl_at(item)
        return item


def recrawl_at(item):
    try:
        posted = dateparser.parse(item['age'])
        if posted is None:
            raise ValueError
        time_since_posted = STARTED_AT - posted
        if time_since_posted < timedelta(1):
            next_crawl = posted + timedelta(1)
        elif time_since_posted < timedelta(7):
            next_crawl = STARTED_AT + timedelta(1)
        elif time_since_posted < timedelta(28):
            next_crawl = STARTED_AT + timedelta(randint(1, 4))
        elif time_since_posted < timedelta(56):
            next_crawl = STARTED_AT + timedelta(3) + timedelta(randint(1, 7))
        else:
            next_crawl = STARTED_AT + timedelta(8) + timedelta(randint(1, 7))
    except (KeyError, TypeError, ValueError):
        next_crawl = STARTED_AT + timedelta(8) + timedelta(randint(1, 7))
    return timegm(next_crawl.timetuple())
