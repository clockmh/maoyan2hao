猫眼爬虫（maoyan.com)
scrapy框架
采用crawlspider，通过rules来筛选特定链接，完成自动全爬取
使用随机useragent,以及阿布云http通道获取代理ip来防止被ban（1h1rmb）（o(╥﹏╥)o）
针对猫眼的票房部分字体反爬技术，使用字形对比的方法来获取自定义编码的对应数据
存储为csv，对于不完整信息也进行存储

接口：
maoyan文件夹中的main.py中的类startscrapy，创建时传入爬取时间（字符串列表），start_from_one()函数开始执行

输出：
spiders文件夹的movie.csv

简单测试方法：
运行main.py，默认爬取2016-2017年，可手动更改传入字符串时间，由于未开启代理ip，不能长时间爬取数据，会被ban。┭┮﹏┭┮

from 钟明涵 2018.11.16 in hitsz 9
version 0.1