from flask import Flask, render_template, redirect, url_for, flash, Response,request
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField
from wtforms.validators import InputRequired, Email, Length, DataRequired
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import json
login_flag = 0
choice_year = ''
choice_season = ''
choice_month = ''

app = Flask(__name__)
app.config['SECRET_KEY'] = 'NOBODY-CAN-GUESS-THIS'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:\\Users\\dell\\Desktop\\flask-login-and-signup-master\\database.db'
Bootstrap(app)
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20))
    email = db.Column(db.String(30), unique=True)
    password = db.Column(db.String(80))

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
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=20)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=5, max=80)])
    remember = BooleanField('remember me')


class choose (FlaskForm):
    year = SelectField(label='年份', choices=[(2015, '2015'), (2016, '2016'), (2017, '2017'),(2018),'2018'], validators=[DataRequired()], defalut=1, coerce=int)
    season = SelectField(label='季度', choices=[(1, '第一季度'), (2, '第二季度'), (3, '第三季度'), (4, '第四季度')], validators=[DataRequired()], defalut=1, coerce=int)
    month = SelectField(label='月份', choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5'), (6, '6'), (7, '7'), (8, '8'), (9, '9'), (10, '10'), (11, '11'), (12, '12')], validators=[DataRequired()], defalut=1, coerce=int)


class RegisterForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(message="Invalid Email"), Length(min=6, max=30)])
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=20)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=5, max=80)])
    confirm_password = PasswordField('confirm_password', validators=[InputRequired(), Length(min=5, max=80)])


@app.route('/')
# @app.route('/index', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


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


@app.route('/login', methods=['GET', 'POST'])
def login():
    global login_flag
    login_flag = 0
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            # compares the password hash in the db and the hash of the password typed in the form
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                login_flag = 1
                return redirect(url_for('Home'))
        return 'invalid username or password'

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

@app.route('/')
@app.route('/Home', methods=['GET', 'POST'])
# @login_required
def Home():
    global login_flag
    if login_flag == 0:
        return render_template('Home.html', name='游客')
    else:
        return render_template('Home.html', name=current_user.username)


@app.route('/logout')
@login_required
def logout():
    global login_flag
    login_flag = 0
    logout_user()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.debug=True
    app.run(debug=True, port=8080)