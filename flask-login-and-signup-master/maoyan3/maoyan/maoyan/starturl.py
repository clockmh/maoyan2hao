import os


# create starturl and rule
class maoyan:
    def __init__(self, times):
        self.times = times

    def writefile(self):
        mov_loc = os.path.dirname(os.path.abspath(__file__)) + r'\spiders\movie.csv'
        gen_loc = os.path.dirname(os.path.abspath(__file__)) + r'\spiders\gender.csv'
        with open(mov_loc, 'w') as movie:
            print('clear movie.csv')
        with open(gen_loc, 'w') as gen:
            print('clear gender.csv')
        starturl = os.path.dirname(os.path.abspath(__file__)) + r'\starturl.txt'
        rule = os.getcwd() + r'\rule.txt'
        with open(starturl, 'w') as url_f:
            with open(rule, 'w') as rule_f:
                for time in self.times:
                    time_n = int(time[2:]) - 5
                    url_f.write('https://maoyan.com/films?showType=3&yearId=' + str(time_n) + '\n')
                    rule_f.write('showType=3&yearId=' + str(time_n) + '&offset=\d+' + '\n')