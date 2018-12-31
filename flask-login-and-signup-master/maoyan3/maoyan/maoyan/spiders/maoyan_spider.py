# -*- coding: utf-8 -*-
from scrapy.spiders import Rule, CrawlSpider
from scrapy.selector import Selector
from scrapy.linkextractors import LinkExtractor
from maoyan.items import MaoyanItem
from maoyan.items import GenderItem
from maoyan.font import font
from scrapy import Request
import os
import requests
import re


class MaoyanSpiderSpider(CrawlSpider):
    name = 'maoyan_spider'
    allowed_domains = ['maoyan.com']
    start_urls = []
    rules = []

    # rules and starturl append from file
    starturl = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + r'\starturl.txt'
    rule = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + r'\rule.txt'
    with open(starturl, 'r') as start_f:
        for line in start_f.readlines():
            line = line.strip('\n')
            start_urls.append(line)
    with open(rule, 'r') as rule_f:
        for line in rule_f.readlines():
            line = line.strip('\n')
            rules.append(Rule(LinkExtractor(allow=(line,), restrict_xpaths=("//a[contains(text(),'下一页')]",)),
                              follow=True))
    rules.append(Rule(LinkExtractor(allow=(r"/films/\d+", )), callback='parse_item'))

    # extract data by xpath
    def parse_item(self, response):
            maoyanitem = MaoyanItem()
            sel = Selector(response)

            maoyanitem['title'] = sel.xpath("//h3[@class='name']/text()").extract()
            maoyanitem['type'] = sel.xpath('/html/body/div[3]/div/div[2]/div[1]/ul/li[1]/text()').extract()
            maoyanitem['time'] = sel.xpath('/html/body/div[3]/div/div[2]/div[1]/ul/li[3]/text()').re('\d+')
            maoyanitem['directors'] = []
            maoyanitem['actors'] = []

            for director in sel.xpath(
                    '//div[@class ="celebrity-container clearfix"]//'
                    'div[@ class ="celebrity-group"][1]/ul/li/div/a/text()'
                    ).extract():
                maoyanitem['directors'].append(director.strip())

            for actor in sel.xpath(
                    '//div[@class ="celebrity-container clearfix"]//'
                    'div[@ class ="celebrity-group"][2]/ul/li/div/a/text()'
                    ).extract():
                maoyanitem['actors'].append(actor.strip())

            '''for url in sel.xpath(
                    '//div[@class ="celebrity-container clearfix"]//'
                    'div[@ class ="celebrity-group"][2]/ul/li/div/a/@href'
                    ).extract():
                next_url = 'https://maoyan.com' + url
                yield Request(next_url, callback=self.actorparse)'''

            maoyanitem['boxoffice'] = []
            # incomplete data
            if sel.xpath('/html/body/div[3]/div/div[2]/div[3]/div[2]/div/span[1]/text()').extract()[0] != '暂无':

                resp = sel.xpath('/html/head/style/text()').extract()[0]  # woff url
                down_woff(resp)  # download .woff

                unit_b = sel.xpath('/html/body/div[3]/div/div[2]/div[3]/div[2]/div/span[2]/text()').extract()[0]
                str_o = sel.xpath('/html/body/div[3]/div/div[2]/div[3]/div[2]/div/span[1]/text()').extract()[0]

                # change unicode to str
                str_un = str_o.encode('unicode_escape')
                str_st = str(str_un)
                str_ori = str_st[2:]
                p = re.compile(r'\\+u*')
                str_ori = p.sub('', str_ori)

                # translate customed code to real boxoffice
                num_b = font().t2n(str_ori[0:-1])
                maoyanitem['boxoffice'] = [num_b + unit_b, ]

            yield maoyanitem

    '''def actorparse(self, response):
        genderitem = GenderItem()
        sel = Selector(response)
        genderitem['name'] = sel.xpath('/html/body/div[3]/div/div[2]/div[1]/p[1]/text()').extract()
        for i in sel.xpath('//*[@id ="app"]/div/div[1]/div[1]/div[2]/div/div[1]/div/dl/dd/text()').extract():
            if '男' == i:
                genderitem['gender'] = ['男']
                break
            elif '女' == i:
                genderitem['gender'] = ['女']
                break
        if not genderitem['gender']:
            genderitem['gender'] = ['']
        yield genderitem'''


# download 1.woff and write to 2.woff
def down_woff(resp):
    ttfUrlRe = re.search("(//.*\.woff)", resp)
    ttfUrl = ""
    if ttfUrlRe:
        ttfUrl = "https:" + ttfUrlRe.group(0)
    if ttfUrl:
        ttfFileStream = requests.get(ttfUrl, stream=True)
        woff = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + r'\2.woff'
        with open(woff, "wb") as fp:
            for chunk in ttfFileStream.iter_content(chunk_size=1024):
                if chunk:
                    fp.write(chunk)