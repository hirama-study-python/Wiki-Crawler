# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


from elasticsearch import Elasticsearch, RequestsHttpConnection
from elasticsearch.exceptions import NotFoundError
from requests_aws4auth import AWS4Auth
import boto3

class ElasticsearchPipeline(object):

    def open_spider(self, spider):

        # 構築したElasticseachのドメイン情報
        host = 'search-kazuki-hirama-7lw5kfmmp5mbk2tniaddbaftpa.us-east-1.es.amazonaws.com'
        region = 'us-east-1'

        service = 'es'

        # 環境変数からAWSへの認証情報を作成する
        credentials = boto3.Session().get_credentials()
        awsauth = AWS4Auth( credentials.access_key , credentials.secret_key , region , service )

        # クライアントをAWS Elasticsearchに接続　

        self.es = Elasticsearch(
            hosts=[{'host': host, 'port': 443}],
            http_auth=awsauth,
            use_ssl=True,
            verify_certs=True,
            connection_class=RequestsHttpConnection
        )



    def process_item(self, item, spider):
        # 更新分のニュースを変数に代入
        update_news = item["news"]
        id = item["id"]

        # docker_volume上の要素を参照
        try:
            res_news = self.es.search( index="wiki-portal" , doc_type="news" , body={"query": {"match_all": {}}} )

            res_news_text = res_news["hits"]["hits"][0]["_source"]["news"]
            if update_news != res_news_text:
                # 対象のニュースがあるが、データの変更があった場合要素を更新
                self.es.index( index='wiki-portal' , doc_type='news' , id=id , body=item)

            else:
                # 対象のニュースがあり、データの変更がない場合なにも行わない
                pass

        except NotFoundError:
            # 対象のニュースデータがない場合DBに対象ニュースを追加
            self.es.index( index='wiki-portal' , doc_type='news' , id=id , body=item)

        return item




