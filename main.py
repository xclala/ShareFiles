from os import system, path, urandom
_ = input("上传/下载（上传 1，下载 2）")
if _ == '1':
    from getpass import getpass
    system("title 上传文件")
    port = input("端口：（默认80端口）")
    h = input("需要上传文件的主机的ip地址：（0.0.0.0表示所有主机）（默认0.0.0.0）")
    pw = getpass("密码：")
    if port == '':
        print("在浏览器中输入您的ip地址即可上传。（80端口不需要输入冒号和端口）")
    else:
        print("在浏览器中输入您的ip地址:"+port+"即可上传。（80端口不需要输入冒号和端口）")
    from flask import Flask, render_template, request, session
    from flask_wtf.csrf import CSRFProtect
    from werkzeug.utils import secure_filename
    from uuid import uuid4

    app = Flask(__name__)
    app.config['SECRET_KEY'] = urandom(666)
    CSRFProtect(app)

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/', methods=['POST'])
    def success():
        if request.method == 'POST':
            if request.form.getlist('remember_password')==['on']:
                if session.get("password") is None:
                    p = request.form['passwd']
                    if p == pw:
                        for f in request.files.getlist('file'):
                            session['password'] = pw
                            if path.exists("上传的文件/"+secure_filename(f.filename)):
                                f.save("上传的文件/"+uuid4().hex +
                                    path.splitext(f.filename)[1])
                            else:
                                f.save("上传的文件/"+secure_filename(f.filename))
                            return render_template('upload.html', alert_message="文件成功上传！")
                    else:
                        return render_template('index.html', alert_message="密码错误！！！")
                else:
                    for f in request.files.getlist('file'):
                        if path.exists("上传的文件/"+secure_filename(f.filename)):
                            f.save("上传的文件/"+uuid4().hex +
                                path.splitext(f.filename)[1])
                        else:
                            f.save("上传的文件/"+secure_filename(f.filename))
                        return render_template('upload.html', alert_message="文件成功上传！")
            else:
                p = request.form['passwd']
                if p == pw:
                    for f in request.files.getlist('file'):
                        if path.exists("上传的文件/"+secure_filename(f.filename)):
                            f.save("上传的文件/"+uuid4().hex +
                                path.splitext(fs.filename)[1])
                        else:
                            f.save("上传的文件/"+secure_filename(f.filename))
                        return render_template('index.html', alert_message="文件成功上传！")
                else:
                    return render_template('index.html', alert_message="密码错误！！！")

    if port == '':
        if h == '':
            app.run(debug=False, port=80, host='0.0.0.0')
        else:
            app.run(debug=False, port=80, host=h)
    else:
        if h == '':
            app.run(debug=False, port=port, host='0.0.0.0')
        else:
            app.run(debug=False, port=port, host=h)
elif _ == '2':
    from os import system
    system("title 下载文件")
    pp = input("端口：（默认80端口）")
    hh = input("需要下载文件的主机的ip地址：（0.0.0.0表示所有主机）（默认0.0.0.0）")
    dd = input("目录：（默认本目录）")
    if pp == '':
        print("在浏览器中输入您的ip地址即可下载。（80端口不需要输入冒号和端口）")
    else:
        print("在浏览器中输入您的ip地址:"+pp+"即可下载。（80端口不需要输入冒号和端口）")
    if pp == '':
        if hh == '':
            if dd == '':
                system("server 80")
            else:
                system(f"server --directory {dd} 80")
        else:
            if dd == '':
                system(f"server --bind {hh} 80")
            else:
                system(f"server --bind {hh} --directory {dd} 80")
    else:
        if hh == '':
            if dd == '':
                system(f"server {pp}")
            else:
                system(f"server --directory {dd} {pp}")
        else:
            if dd == '':
                system(f"server --bind {hh} {pp}")
            else:
                system(f"server --bind {hh} --directory {dd} {pp}")
