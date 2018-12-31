from fontTools.ttLib import TTFont
import os
# change the code to real number
class font():

    def t2n(self, str_ori):
        tmp_dic = {}
        self.creatdic(tmp_dic)  # creat dic for the customed coding
        return self.tff2n(str_ori, tmp_dic)  # to real number

    def tff2n(self, para_o, tmp_dic={}):  # to real number
        para = para_o.upper()
        for key, value in tmp_dic.items():
            para = para.replace(key, value)
        return para.replace(';', '')

    def creatdic(self, tmp_dic):
        woff1 = os.path.dirname(os.path.abspath(__file__)) + r'\1.woff'
        font1 = TTFont(woff1)
        # font0.saveXML('2.xml')  # for developer
        # obj_list1 = font1.getGlyphNames()[1:-1]  # same
        uni_list1 = font1.getGlyphOrder()[2:]  # all code except first and second

        # to get by eyes
        code_dict = {'uniE40E': '8', 'uniE113': '2', 'uniE33A': '1', 'uniED95': '9', 'uniF08A': '3', 'uniE101': '4',
                     'uniE10E': '0', 'uniF560': '7', 'uniEB8C': '5', 'uniE129': '6'}
        woff2 = os.path.dirname(os.path.abspath(__file__)) + r'\2.woff'
        font2 = TTFont(woff2)  # 2.ttf
        # obj_list2 = font2.getGlyphNames()[1:-1] developer
        uni_list2 = font2.getGlyphOrder()[2:]
        for uni2 in uni_list2:
            obj2 = font2['glyf'][uni2]
            for uni1 in uni_list1:
                obj1 = font1['glyf'][uni1]
                if obj1 == obj2:  # same symbol means same value
                    tmp_dic.update({uni2[3:]: code_dict[uni1]})  # get dic


