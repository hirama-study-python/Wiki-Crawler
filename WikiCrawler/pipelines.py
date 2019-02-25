# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


from elasticsearch import Elasticsearch

class ElasticsearchPipeline(object):

    def open_spider(self, spider):
        self.es = Elasticsearch()

    def process_item(self, item, spider):
        # 更新分のニュースを変数に代入
        update_news = item["news"]
        id = item["id"]

        # docker_volume上の要素を参照
        res_news = self.es.search( index="wiki-portal" , doc_type="news" , body={"query": {"match_all": {}}} )

        if id not in res_news:
            # 対象のニュースデータがない場合DBに対象ニュースを追加
            self.es.index( index='wiki-portal' , doc_type='news' , id=id , body=item)

        elif update_news.text != res_news.text:
            # 対象のニュースがあるが、データの変更があった場合要素を更新
            self.es.update( index='wiki-portal' , doc_type='news' , id=id , body=item)

        else:
            # 対象のニュースがあり、データの変更がない場合なにも行わない
            pass

        return item




