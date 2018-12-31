# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import csv
import os
import json
from maoyan.items import MaoyanItem
from maoyan.items import GenderItem
import re

# write csv
class MaoyanPipeline(object):
    def process_item(self, item, spider):
        if isinstance(item, MaoyanItem):
            with open ('rule.txt','r') as f:
                text = str(f.readline())
                s1 = r"(?<=Id=)\d+"
                p1 = re.compile(s1)
                matcher1 = re.search(p1, text)
                time = matcher1.group(0)
                dict = {'13':2018, '12':2017, '11':2016, '10':2015 }
                year = dict[time]
            store_file = os.path.dirname(__file__) + '/spiders/movie' + str(year) + '.csv'
            with open(store_file, 'a') as file:
                writer = csv.writer(file, delimiter=',')
                writer.writerow(
                    (item['title'], item['directors'], item['actors'], item['type'], item['time'], item['boxoffice']))
            return item
        if isinstance(item, GenderItem):
            store_file = os.path.dirname(__file__) + '/spiders/gender.csv'
            with open(store_file, 'a') as file:
                writer = csv.writer(file, delimiter=',')
                writer.writerow(
                    (item['name'], item['gender']))
            return item


# useless
class MaoyanPipeline_json(object):

    def __init__(self):
        self.file = open('movie.json', mode='wa', encoding='utf-8')

    def process_item(self, item, spider):
        line = json.dumps(dict(item), ensure_ascii=False) # , indent=4)
        self.file.write(line)
        self.file.write("\n")
        return item

    def close_spider(self, spider):
        self.file.close()


