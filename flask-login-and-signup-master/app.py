from flask import Flask, render_template, redirect, url_for, flash, Response,request,session , make_response
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField
from wtforms.validators import InputRequired, Email, Length, DataRequired
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import json
import random
import string
from PIL import Image, ImageFont, ImageDraw, ImageFilter
from io import BytesIO
import smtplib
from email.mime.text import MIMEText
import os
import subprocess
verify_code = ''
login_flag = 0
choice_year = ''
choice_season = ''
choice_month = ''
picflag = ''
flag_pachong = '0'

app = Flask(__name__)
app.config['SECRET_KEY'] = 'NOBODY-CAN-GUESS-THIS'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:\\Users\\dell\\Desktop\\flask-login-and-signup-master\\database.db'
Bootstrap(app)
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.session_protection = "strong"
login_manager.login_view = 'login'


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20))
    email = db.Column(db.String(30), unique=True)
    password = db.Column(db.String(80))






def rndColor():
    '''随机颜色'''
    return (random.randint(32, 127), random.randint(32, 127), random.randint(32, 127))

def gene_text():
    '''生成4位验证码'''
    return ''.join(random.sample(string.ascii_letters+string.digits, 4))


def draw_lines(draw, num, width, height):
    '''划线'''
    for num in range(num):
        x1 = random.randint(0, width / 2)
        y1 = random.randint(0, height / 2)
        x2 = random.randint(0, width)
        y2 = random.randint(height / 2, height)
        draw.line(((x1, y1), (x2, y2)), fill='black', width=1)


def get_verify_code():
    '''生成验证码图形'''
    code = gene_text()
    # 图片大小120×50
    width, height = 120, 50
    # 新图片对象
    im = Image.new('RGB',(width, height),'white')
    # 字体
    font = ImageFont.truetype('app/static/arial.ttf', 40)
    # draw对象
    draw = ImageDraw.Draw(im)
    # 绘制字符串
    for item in range(4):
        draw.text((5+random.randint(-3,3)+23*item, 5+random.randint(-3,3)),
                  text=code[item], fill=rndColor(),font=font )
    # 划线
    draw_lines(draw, 2, width, height)
    # 高斯模糊
    im = im.filter(ImageFilter.GaussianBlur(radius=1.5))
    return im, code

def send_email(receivers, content):
    mail_host = "smtp.sina.cn"  # SMTP服务器  #网易是 smtp.163.com     #腾讯是 smtp.qq.com
    mail_user = "perfectcrm@sina.cn"  # 用户名#新浪邮箱账号或者163和QQ 的邮箱账号
    mail_pass = "admin123456"  # 授权密码，非登录密码 #新浪是登陆密码 #163和QQ是授权密码

    sender = 'perfectcrm@sina.cn'  # 发件人邮箱(最好写全, 不然会失败)  #新浪邮箱账号或者163和QQ 的邮箱账号
    message = MIMEText(content, 'plain', 'utf-8')  # 内容, 格式, 编码
    message['From'] = "{}".format(sender)  # # 发件人邮箱(最好写全, 不然会失败)
    message['To'] = ",".join(receivers)  # # 接收邮件，可设置为你的QQ邮箱或者其他邮箱
    message['Subject'] = '密码找回'  # 邮件主题
    try:
        smtpObj = smtplib.SMTP_SSL(mail_host, 465)  # 启用SSL发信, 端口一般是465
        smtpObj.login(mail_user, mail_pass)  # 登录验证
        smtpObj.sendmail(sender, receivers, message.as_string())  # 发送
        print("已发送")
    except smtplib.SMTPException as e:
        print(e)  # 错误信息




def Response_headers(content):
    resp = Response(content)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

@app.before_first_request
def int_db():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class LoginForm(FlaskForm):
    username = StringField('username', validators=[InputRequired(), Length(min=2, max=20)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=3, max=80)])
    verify_code = StringField('verify_code', validators=[DataRequired()])
    remember = BooleanField('remember me')


class ChangePassword(FlaskForm):
    username = StringField('username', validators=[InputRequired(), Length(min=2, max=20)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=3, max=80)])
    new_password = PasswordField('new_password', validators=[InputRequired(), Length(min=3, max=80)])
    sure_password = PasswordField('sure_password', validators=[InputRequired(), Length(min=3, max=80)])


class FetchPassword(FlaskForm):
    username = StringField('username', validators=[InputRequired(), Length(min=2, max=20)])
    email = StringField('email', validators=[InputRequired(), Length(min=2, max=20)])


class ChangePasswordF(FlaskForm):
    username = StringField('username', validators=[InputRequired(), Length(min=2, max=20)])
    new_password = PasswordField('new_password', validators=[InputRequired(), Length(min=3, max=80)])
    sure_password = PasswordField('sure_password', validators=[InputRequired(), Length(min=3, max=80)])
    verify_code = StringField('verify_code', validators=[InputRequired(), Length(min=2, max=20)])

class choose (FlaskForm):
    year = SelectField(label='年份', choices=[(2015, '2015'), (2016, '2016'), (2017, '2017'),(2018),'2018'], validators=[DataRequired()], defalut=1, coerce=int)
    season = SelectField(label='季度', choices=[(1, '第一季度'), (2, '第二季度'), (3, '第三季度'), (4, '第四季度')], validators=[DataRequired()], defalut=1, coerce=int)
    month = SelectField(label='月份', choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5'), (6, '6'), (7, '7'), (8, '8'), (9, '9'), (10, '10'), (11, '11'), (12, '12')], validators=[DataRequired()], defalut=1, coerce=int)


class RegisterForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(message="Invalid Email"), Length(min=6, max=30)])
    username = StringField('username', validators=[InputRequired(), Length(min=2, max=20)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=3, max=80)])
    confirm_password = PasswordField('confirm_password', validators=[InputRequired(), Length(min=3, max=80)])


@app.route('/')
# @app.route('/index', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/post_login_state', methods=['POST', 'GET'])
def post_login_state():
    global login_flag
    datas = {'data': [{'login_flag': login_flag}]}
    content = json.dumps(datas)
    resp = Response_headers(content)
    return resp


@app.route('/get_code')
def get_code():
    image, code = get_verify_code()
    # 图片以二进制形式写入
    buf = BytesIO()
    image.save(buf, 'jpeg')
    buf_str = buf.getvalue()
    # 把buf_str作为response返回前端，并设置首部字段
    response = make_response(buf_str)
    response.headers['Content-Type'] = 'image/gif'
    # 将验证码字符串储存在session中
    session['image'] = code
    return response


@app.route('/receive_data', methods=['POST', 'GET'])
def receive_data():
    global choice_year
    global choice_season
    global choice_month
    data = request.get_json(force=True)  # 获取json数据
    choice_year = data['year']
    choice_season = data['season']
    choice_month = data['month']

    print(choice_season)
    print(choice_year)
    print(choice_month)


@app.route('/echarts', methods=['POST', 'GET'])
def echarts():
      # 获取json数据\
    global choice_year
    global choice_season
    global choice_month

    if choice_year == '1':
        datas = {
                "data": [
                    {"name": "allpe", "num": 100},
                    {"name": "peach", "num": 123},
                    {"name": "Pear", "num": 234},
                    {"name": "avocado", "num": 20},
                    {"name": "cantaloupe", "num": 1},
                    {"name": "Banana", "num": 77},
                    {"name": "Grape", "num": 43},
                    {"name": "apricot", "num": 0}
                ]
            }
    elif choice_year == '2':
        datas = {
            'data': [
                {"name": "allpe", "num": 100},
                {"name": "peach", "num": 123},
            ]
        }
    elif choice_year == '3':
        datas = {
            'data': [
                {"name": "allpe", "num": 10},
                {"name": "peach", "num": 123},
            ]
        }
    else:
        datas = {
            'data': [
                {"name": "allpe", "num": 10},
                {"name": "peach", "num": 123},
                {"name": "peach", "num": 80},
            ]
        }

    content = json.dumps(datas)
    resp = Response_headers(content)
    return resp


@app.route('/try1', methods=['GET', 'POST'])
def try1():
    return render_template('try.html')

@app.route('/spider', methods=['GET', 'POST'])
def spider():
    return render_template('spider.html')


@app.route('/annual_change', methods=['GET', 'POST'])
def annual_change():
    return render_template('annual_change.html')


@app.route('/model_actor', methods=['GET', 'POST'])
def model_actor():
    return render_template('model_actor.html')


@app.route('/movie_top', methods=['GET', 'POST'])
def movie_top():
    return render_template('movie_top.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    global login_flag
    login_flag = 0
    form = LoginForm()
    if form.validate_on_submit():
        flag = 0
        if session.get('image') != form.verify_code.data:
            print(session.get('image'))
            print(form.verify_code.data)
            flash('wrong verify code', 1)
            flag = 1
        if not flag:
            user = User.query.filter_by(username=form.username.data).first()
            if user:
                # compares the password hash in the db and the hash of the password typed in the form
                if check_password_hash(user.password, form.password.data):
                    login_user(user, remember=form.remember.data)
                    login_flag = 1
                    return redirect(url_for('Home'))
            flash( 'invalid username or password', 1)

    return render_template('login.html', form=form)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    global login_flag
    login_flag = 0
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        # add the user form input which is form.'field'.data into the column which is 'field'
        a = User.query.count()
        b = 1
        flag = 0
        while b <= a and flag == 0:
            # print(User.query.get(b).username)
            # print(form.username.data)
            if form.username.data == User.query.get(b).username:
                flag = 1
                flash('The account is existed, please input again!', '1')
                break
            elif form.email.data == User.query.get(b).email:
                flag = 1
                flash('The email address has used in register, please use another one!', '1')
                break
            b += 1
        if form.password.data != form.confirm_password.data and (not flag):
            print(form.confirm_password.data, '  ', form.password.data)
            flag = 1
            flash('The passwords entered twice are different, please input again!', '1')

        if not flag:
            new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))

    return render_template('signup.html', form=form)


@app.route('/fetch_password', methods=['GET', 'POST'])
def fetch_password():
    form = FetchPassword()
    global verify_code
    if form.validate_on_submit():
        a = User.query.count()
        b = 1
        flag = 0
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            while b <= a and flag == 0:
                if form.username.data == User.query.get(b).username:
                    flag = 1
                    if form.email.data == User.query.get(b).email:
                        print(User.query.get(b).email)
                        email = form.email.data
                        temp_email = [email]
                        verify_code = gene_text()
                        print(temp_email, verify_code)
                        send_email(temp_email, verify_code)
                        return redirect(url_for('change_passwordf'))
                    else:
                        flash('The account is not matched with the email!', '1')
                b = b+1
        if flag == 0:
            flash('The account is not existed!', '1')
    return render_template('fetch_password.html', form=form)


@app.route('/change_passwordf', methods=['GET', 'POST'])
def change_passwordf():
    form = ChangePasswordF()
    global verify_code
    a = User.query.count()
    b = 1
    flag = 0
    user = User.query.filter_by(username=form.username.data).first()
    if user:
        while b <= a and flag == 0:
            if form.username.data == User.query.get(b).username:
                flag = 1
                if form.verify_code.data == verify_code:

                    if form.new_password.data == form.sure_password.data:
                        User.query.get(b).password = generate_password_hash(form.new_password.data, method='sha256')
                        db.session.commit()
                        flag = 2
                    else:
                        flash('The new_password is different to sure_password, please input again!', '1')
                else:
                    flash('The verify code is not correct', '1')
            b = b+1
        if flag == 0:
            flash('The account is not existed, please input again!', '1')
        elif flag == 2:
            return redirect(url_for('login'))
    return render_template('change_passwordf.html', form=form)


@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    form = ChangePassword()
    if form.validate_on_submit():
        # add the user form input which is form.'field'.data into the column which is 'field'
        a = User.query.count()
        b = 1
        flag = 0
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            while b <= a and flag == 0:
                # print(User.query.get(b).username)
                # print(form.username.data)
                if form.username.data == User.query.get(b).username:
                    flag = 1
                    if check_password_hash(user.password, form.password.data):
                        if form.password.data != form.new_password.data:  #新密码和原密码不一致
                            if form.new_password.data == form.sure_password.data:

                                User.query.get(b).password = generate_password_hash(form.new_password.data, method='sha256')
                                db.session.commit()

                                flag = 2
                            else:
                                flash('The new_password is different to sure_password, please input again!', '1')
                        else:
                            flash('The new_password is the same to the old_password, please input again!', '1')
                    else:
                        flash('The old_password is not correct, please input again!', '1')
                b += 1
        if flag == 0:
            flash('The account is not existed, please input again!', '1')
        elif flag == 2:
            return redirect(url_for('login'))

    return render_template('change_password.html', form=form)


@app.route('/Home', methods=['GET', 'POST'])

def Home():
    global login_flag
    if login_flag == 0:
        return render_template('Home.html', name='游客')
    else:
        return render_template('Home.html', name=current_user.username)

def pachong_dis(year):
    global child
    global flag_pachong
    flag_pachong = '1'
    basepath = os.getcwd()
    print(basepath)
    f = open("pachon.bat","w")
    f.write('cd ' + basepath + '\\maoyan3\\maoyan\\maoyan\n' + 'python ' + 'main.py ' + year)
    f.close()
    child = subprocess.Popen('pachon.bat')
    child.wait()
    flag_pachong = '0'

@app.route('/pachongflag',methods = ['POST','GET'])
def pachongflag():
    datas = {"data":[]}
    if request.method == 'GET':
        print('@@@@@@@@@@@@@@@@@@@@@@@')
        datas['data'].append({'name':flag_pachong})
        content = json.dumps(datas)
        resp = Response_headers(content)
        return resp

@app.route('/receive_spider',methods = ['POST' , 'GET'])
def receiveSpider():
    global spider
    global flag
    flag = 1
    data = request.get_json(force=True)
    spider = data['year']
    spider = str(int(spider) + 2014)
    pachong_dis(spider)

@app.route('/add_flag', methods=['GET', 'POST'])
def add_flag():
    global picflag
    data = request.get_json(force=True)
    picflag = data['picflag']
    print(picflag)


@app.route('/image_flag', methods=['GET', 'POST'])
def img_flag():
    global picflag
    datas = {"data" : [{'name': picflag}]}
    picflag = '0'
    content = json.dumps(datas)
    resp = Response_headers(content)
    return resp


@app.route('/download', methods=['GET', 'POST'])
# @login_required
def download():

    return render_template('download.html')

@app.route('/logout')
@login_required
def logout():
    global login_flag
    login_flag = 0
    logout_user()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.debug=True
    app.run(debug=False, threaded=True, port=5000)