# Blueprints

 ##  1.蓝图详解

- **蓝图概念**

> 简单来说，Blueprint 是一个存储操作方法的容器，这些操作在这个Blueprint 被注册到一个应用之后就可以被调用，Flask 可以通过Blueprint来组织URL以及处理请求。
>
> Flask使用Blueprint让应用实现模块化，在Flask中，Blueprint具有如下属性：
>
> - 一个应用可以具有多个Blueprint
> - 可以将一个Blueprint注册到任何一个未使用的URL下比如 “/”、“/sample”或者子域名
> - 在一个应用中，一个模块可以注册多次
> - Blueprint可以单独具有自己的模板、静态文件或者其它的通用操作方法，它并不是必须要实现应用的视图和函数的
> - 在一个应用初始化时，就应该要注册需要使用的Blueprint
>
> 但是一个Blueprint并不是一个完整的应用，它不能独立于应用运行，而必须要注册到某一个应用中。

- **初识蓝图**

> 蓝图/Blueprint对象用起来和一个应用/Flask对象差不多，最大的区别在于一个 蓝图对象没有办法独立运行，必须将它注册到一个应用对象上才能生效
>
> 使用蓝图可以分为三个步骤
>
> 1,创建一个蓝图对象
>
> ```python
> admin``=``Blueprint(``'admin'``,__name__)　
> ```
>
> 2,在这个蓝图对象上进行操作,注册路由,指定静态文件夹,注册模版过滤器
>
> ```python
> @admin``.route(``'/'``)``def` `admin_home():``  ``return` `'admin_home'
> ```
>
> 3,在应用对象上注册这个蓝图对象
>
> ```python
> app.register_blueprint(admin,url\_prefix``=``'/admin'``)
> ```
>
> 当这个应用启动后,通过/admin/可以访问到蓝图中定义的视图函数

- **运行机制**

> 蓝图是保存了一组将来可以在应用对象上执行的操作，注册路由就是一种操作
>
> 当在应用对象上调用 route 装饰器注册路由时,这个操作将修改对象的url_map路由表
>
> 然而，蓝图对象根本没有路由表，当我们在蓝图对象上调用route装饰器注册路由时,它只是在内部的一个延迟操作记录列表defered_functions中添加了一个项
>
> 当执行应用对象的 register_blueprint() 方法时，应用对象将从蓝图对象的 defered_functions  列表中取出每一项，并以自身作为参数执行该匿名函数，即调用应用对象的 add_url_rule() 方法，这将真正的修改应用对象的路由表

## 2.代码实现

- lab.py

  ```python
  # -*- coding: utf-8 -*-
  """
  Created on Mon Jun  3 15:42:51 2019
  
  @author: Administrator
  """
  
  from flask import Flask, request
  from UseSqlite import InsertQuery
  from datetime import datetime
  
  from service import get_database_photos
  from upload import upload_bp
  from show import show_bp
  from search import search_bp
  from api import api_bp
  
  app = Flask(__name__)
  
  
  @app.route('/', methods=['POST', 'GET'])
  def main():
      if request.method == 'POST':
          uploaded_file = request.files['file']
          time_str = datetime.now().strftime('%Y%m%d%H%M%S')
          new_filename = time_str + '.jpg'
          uploaded_file.save('./static/upload/' + new_filename)
          time_info = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
          description = request.form['description']
          path = './static/upload/' + new_filename
          iq = InsertQuery('./static/RiskDB.db')
          iq.instructions("INSERT INTO photo Values('%s','%s','%s','%s')" % (time_info, description, path, new_filename))
          iq.do()
          return '<p>You have uploaded %s.<br/> <a href="/">Return</a>.' % (uploaded_file.filename)
      else:
          page = '''
              <a href='/upload'>upload</a>
              <a href='/search'>search</a>
              <a href='/show'>show</a>
              <a href='/api'>api</a>
          '''
          page += get_database_photos()
          return page
  
  
  app.register_blueprint(upload_bp)
  app.register_blueprint(show_bp)
  app.register_blueprint(search_bp)
  app.register_blueprint(api_bp)
  
  if __name__ == '__main__':
      app.run(debug=True)
  ```

- api.py

  ```python
  import json
  import os.path
  
  from flask import Blueprint
  from UseSqlite import RiskQuery
  
  api_bp = Blueprint('api', __name__)
  
  
  @api_bp.route('/api', methods=['POST', 'GET'])
  def api_json():
      rq = RiskQuery('./static/RiskDB.db')
      rq.instructions("SELECT * FROM photo ORDER By time desc")
      rq.do()
      lst = []
      page = ''
      i = 1
      for r in rq.format_results().split('\n\n'):
          photo = r.split(',')
          picture_time = photo[0]
          picture_description = photo[1]
          picture_path = photo[2].strip()
          photo_size = str(format((os.path.getsize(picture_path) / 1024), '.2f')) + 'KB'
          lst = [{'ID': i, 'upload_date': picture_time, 'description': picture_description, 'photo_size': photo_size}]
          lst2 = json.dumps(lst[0], sort_keys=True, indent=4, separators=(',', ':'))
          page += '%s' % lst2
          page += '<br>'
          i += 1
      return page
  ```

- search.py

  ```python
  from flask import Blueprint, request
  
  from service import get_description_photos
  
  search_bp = Blueprint('search', __name__)
  
  
  @search_bp.route('/search', methods=['POST', 'GET'])
  def search():
      page = '''<form action="/search/query-string"method="post"enctype="multipart/form-data">
                  <input name="description"><input type="submit"value="search"></form>'''
      return page
  
  
  @search_bp.route('/search/query-string', methods=['POST', 'GET'])
  def query_string():
      if request.method == 'POST':
          description = request.form['description']
          page = get_description_photos(description)
  
      return page
  ```

- show.py

  ```python
  from flask import Blueprint
  from service import get_database_photos
  show_bp = Blueprint('show', __name__)
  
  
  @show_bp.route('/show')
  def show():
      page = get_database_photos()
      return page
  ```

- upload.py

  ```python
  from flask import Blueprint
  
  upload_bp = Blueprint('upload', __name__)
  
  
  @upload_bp.route('/upload')
  def upload():
      page = '''<form action="/"method="post"enctype="multipart/form-data">
              <input type="file"name="file"><input name="description"><input type="submit"value="Upload"></form>'''
      return page
  ```

## 3.实际运行

详见网址【大三上软件体系结构lab2-哔哩哔哩】 https://b23.tv/VZQqqup

## 4. Bug发现

Bug：提交空文件后报错！
		原因：未对提交进行验证，用户空白提交后，直接在数据库加入元素，但因空白提交，无法在程序中找到文件，导致报错。

## 5.人员组成及分工

董泽翔——文本编写，bug发现，视频制作

周宇峰——代码实现，视频编辑，文档提交

徐毅——文本编写，视频编辑

段佐翼——视频编辑，代码注释

张祯辰——文献查找，代码编辑

## 6.实验心得

由于之前对Englishpal的后端进行代码重构的过程中也运用了蓝图这一工具，而且上一个实验的代码规模远大于本实验的代码故本次实验过程中我们小组并未遇到什么困难，而我们也在又一次在对蓝图的使用中加深了对此工具的理解，也更重视代码重构中的意义以及软件体系架构这门学科。

