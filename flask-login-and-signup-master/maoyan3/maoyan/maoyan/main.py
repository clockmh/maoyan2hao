from scrapy import cmdline
import sys
import os
sys.path.append(os.path.dirname((os.path.dirname(os.path.abspath(__file__)))))
from maoyan.starturl import maoyan


# start the scrapy
class startscrapy():
    def __init__(self, time):
        self.time = time

    def start_from_mult(self):  # useless
        for year in self.time:
            cmdcode = 'scrapy crawl maoyan' + year + '_spider'
            cmdline.execute(cmdcode.split())

    def start_from_one(self):
        mao = maoyan(self.time)
        mao.writefile()
        cmdline.execute('scrapy crawl maoyan_spider'.split())


# just for test
if __name__ == '__main__':
    default_time = ['2015', '2016', '2017', '2018']
    if len(sys.argv) == 1:
        st = startscrapy(default_time)
        st.start_from_one()
    elif len(sys.argv) > 5:
        print("too much parameter,add h for help")
        exit(0)
    else:
        for time in sys.argv[1:]:
            if len(time) > 5:
                print("long parameter,add h for help")
                exit(0)
            if time not in default_time:
                print("invalid input!!,add h for help")
                exit(0)
        st = startscrapy(sys.argv[1:])
        st.start_from_one()