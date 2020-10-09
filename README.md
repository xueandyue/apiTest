# apiTest
该接口自动化平台是基于对httprunner的封装开发，核心模块是httprunner 2.2.6 ,有支持httprunner的env,api，批量生成用例，报告导出成excel，导入用例或者api，定时执行，账号数据权限独立（看不到别人账号的数据）等功能

                接口测试自动化平台部署
                
    一、	安装mysql数据库服务端(推荐5.7+),并设置为utf-8编码，创建相应数据库，设置好相应用户名、密码，启动mysql

    二、修改: apiTest/ apiTest/settings.py里DATABASES字典和邮件发送账号相关配置
        DATABASES = {
             'default': {
             'ENGINE': 'django.db.backends.mysql',
             'NAME': ' apiTest',  # 数据库名
             'USER': '*****',  # 数据库登录名
             'PASSWORD': '******',  # 数据库登录密码
             'HOST': '127.0.0.1',  # 数据库所在服务器ip地址
             'PORT': '3306',  # 监听端口 默认3306即可
         }
     }
    EMAIL_SEND_USERNAME = 'username@163.com'  # 定时任务报告发送邮箱，支持163,139,sina,企业qq邮箱等，注意需要开通smtp服务
     EMAIL_SEND_PASSWORD = 'password'     # 邮箱密码

    三、安装rabbitmq消息中间件，启动服务，设置好用户名密码，默认是guest / guest 
     在linux的启动命令   service rabbitmq-server start


    四、修改: apiTest /apiTest /settings.py里worker相关配置
        djcelery.setup_loader()
        CELERY_ENABLE_UTC = True
        CELERY_TIMEZONE = 'Asia/Shanghai'
        BROKER_URL = 'amqp://guest:guest@127.0.0.1:5672//'  # 127.0.0.1即为rabbitmq-server所在服务器ip地址,guest,guest是用户名和密码
        CELERYBEAT_SCHEDULER = 'djcelery.schedulers.DatabaseScheduler'
        CELERY_RESULT_BACKEND = 'djcelery.backends.database:DatabaseBackend'
        CELERY_ACCEPT_CONTENT = ['application/json']
        CELERY_TASK_SERIALIZER = 'json'
        CELERY_RESULT_SERIALIZER = 'json'

        CELERY_TASK_RESULT_EXPIRES = 7200  # celery任务执行结果的超时时间，
        CELERYD_CONCURRENCY = 10  # celery worker的并发数 也是命令行-c指定的数目 根据服务器配置实际更改 默认10
        CELERYD_MAX_TASKS_PER_CHILD = 100  # 每个worker执行了多少任务就会死掉，我建议数量可以大一些，默认100


    五、安装python，需要python 3 以上的版本,最好是python 3.6.7版本


    六、进入代码apiTest 目录下执行以下命令
        pip install -r requirements.txt    #安装工程所依赖的库文件
        python manage.py makemigrations #生成数据迁移脚本
        python manage.py migrate  #应用到db生成数据表

    七、后台启动django
       进入代码apiTest 目录下执行以下命令
     nohup python manage.py runserver 0.0.0.0:88 >djo.out 2>&1 &

    八、后台启动worker, 如果选择同步执行并确保不会使用到定时任务，那么此步骤可忽略
       进入代码apiTest 目录下执行以下命令
    nohup python -u manage.py celery -A apiTest worker --loglevel=info   >worker.out 2>&1 &

    nohup python -u manage.py celery beat --loglevel=info  >beat.out 2>&1 &	


    九、后台启动相关的java服务

      进入代码apiTest 目录下执行以下命令

     nohup  java -jar Createtest.war --server.port=8888 &



    十、浏览器输入：http://ip地址/Login/login/

    十一、如果要提升性能，uwsgi+nginx部署参考：https://www.jianshu.com/p/d6f9138fab7b
    
    十二、在线展示 http://129.204.215.114:88/Login/login/
    
    
欢迎加群交流
         群名称：接口自动化平台交流群
        群   号：1044894017

![Image text](https://github.com/xueandyue/apiTest/blob/master/qun.png)
