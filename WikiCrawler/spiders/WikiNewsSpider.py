# -*- coding: utf-8 -*-
import scrapy
import re
from bs4 import BeautifulSoup


class WikiNewsSpider(scrapy.Spider):
    name = 'WikiNewsSpider'
    allowed_domains = ['ja.wikipedia.org']
    start_urls = ['https://ja.wikipedia.org/wiki/Portal:最近の出来事']

    custom_settings = {
        "DOWNLOAD_DELAY": 1.5,
    }

    # 一覧ページのパース用コールバック関数
    # Following Linksのクローリングも合わせて行なっている
    def parse(self, response):

        html = response.text
        soup = BeautifulSoup(html, 'html.parser')

        data = self.extract_data(soup)
        for d in data:
            yield d

        # ページ内のテーブルを取ってくる
        year_summaries = soup.find('table').find_all('table')[-1].find_all('ul')

        for year_summary in year_summaries:

            # <ul>タグの次の<dl>タグを取ってくる
            month_summary = year_summary.next_sibling.string.next_sibling

            for month_link_tag in month_summary.find_all("a"):
                next_page =  month_link_tag.get('href')

                if next_page is not None:
                    yield response.follow(next_page, self.parse_detail)

                break
            break

    # 詳細ページのパース用コールバック関数
    def parse_detail(self, response):
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')

        data = self.extract_data(soup)
        for d in data:
            yield d

    # Beautifulsoupインスタンスからデータ要素を抽出する関数
    # 抽出した結果はList形式で返却する
    def extract_data(self, soup):

        data = []

        date_headlines_table = soup.find('div', class_="mw-parser-output")

        # 見出しの日付を取得する
        date_headlines = date_headlines_table.find_all('h3')

        for date_headline in date_headlines:

            date_detail = date_headline.find('span', class_="mw-headline")
            # 日付見出しの次は必ず<ui>タグが設定されている
            newses = date_headline.next_sibling.string.next_sibling

            # <ui>タグ内の<li>タグを探す
            for i, news in enumerate(newses.find_all('li')):
                # カテゴリがない場合のエラー処理を実装
                try:
                    category = news.find("i").text
                except AttributeError:
                    category = "-"

                re_news = re.sub('（[^）]*）', '', news.text)

                data.append({
                    "date": date_detail.text,
                    "category": category,
                    "news": re_news
                })

        return data






