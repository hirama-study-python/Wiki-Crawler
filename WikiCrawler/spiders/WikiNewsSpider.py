# -*- coding: utf-8 -*-
import scrapy
import re


class WikiNewsSpider(scrapy.Spider):
    name = 'WikiNewsSpider'
    allowed_domains = ['ja.wikipedia.org']
    start_urls = ['https://ja.wikipedia.org/wiki/Portal:最近の出来事']

    def parse(self, response):
        date_headlines_table = response.xpath("//div[@class='mw-parser-output']")
        for date_headline in date_headlines_table.xpath("//h3"):
            date_datail = date_headline.xpath("//span[@class='mw-headline']")
            newses = date_headline.next_sibling.string.next_sibling

            # <ui>タグ内の<li>タグを探す
            for news in newses.xpath("//li"):
                # カテゴリがない場合のエラー処理を実装
                try:
                    category = news.xpath("//i").extract()
                except AttributeError:
                    category = "-"

                re_news = re.sub('（[^）]*）', '', news.text)

                yield {
                        "date": date_datail,
                        "category": category,
                        "news": re_news
                        }