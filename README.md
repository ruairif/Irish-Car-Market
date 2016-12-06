
Irish Car Market Analysis
=========================

Installation
------------

To install all required libraries for crawling, run:

    pip install -r requirements-crawl.txt

To install all required libraries for analysis, run:

    pip install -r requirements-analysis.txt

Crawling
--------

You can run a crawl locally by running:

    scrapy crawl donedeal -o donedeal.jl && \
    scrapy crawl carsireland -o carsireland.jl && \
    scrapy crawl autoevolution -o autoevolution.jl

You can also push these spiders to scrapinghub and running them there by using
the [shub](https://doc.scrapinghub.com/shub.html) tool and modifying
`scrapinghub.yml` to point to your own project.

Analysing
---------

You can run analysis on the data by running `jupyter notebook` and opening the
`Irish Car Market` notebook
