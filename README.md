# maoyan2hao
## 3组-项目说明  
### 1.依赖环境：  
>python3.7  
### 2.实现功能：  
>登陆/注册（密码加密），利用邮箱找回密码，爬虫读取数据，数据可视化（票房、票房占比、top电影、劳模演员），生成并下载报表（pdf）。  
### 3.实现技术：  
>使用flask框架，用HTML编写网页，echarts画图，python做数据处理以及本地数据库的实现，smtp实现发邮件（密码找回）  
### 4.相比检查时的新增功能：  
>将爬虫和前端连在一起，可以让用户自主选择爬取的数据的年份，并根据最新的数据更新图表；  
>实现了利用邮箱找回密码的功能；  
>完善了报错机制，提高了系统的稳定性。  
### 5.运行系统的方法：  
>第一步：先修改flask-login-and-signup-master文件夹中的app.py中的数据库地址，即修改app.config['SQLALCHEMY_DATABASE_URI']后面的地址。  
>第二步：用pycharm运行rg文件夹中的dataoperatenow.py。  
>第三步：用pycharm运行flask-login-and-signup-master文件夹中的app.py。两个文件运行起来后的端口是不同的。  
>第四步：根据app.py生成的url进入系统，开始使用即可。    
