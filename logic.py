from flask import Flask, render_template, request, session, abort, send_file, redirect
from flask_wtf.csrf import CSRFProtect
from waitress import serve
from os import path, urandom, scandir
from werkzeug.utils import secure_filename
from uuid import uuid4
app = Flask(__name__)
app.config['SECRET_KEY'] = urandom(666)
CSRFProtect(app)
class Base:
    global url_prefix
    url_prefix = ''
    def __init__(self, port, thread, pw=None, prefix=None):
        self.password = pw
        if prefix:
            url_prefix = prefix
        serve(app, host='0.0.0.0', port=port, threads=thread)

    @app.errorhandler(404)
    def notfound(error):
        return redirect("/")
class Upload(Base):
    @app.route('/', methods=['GET', 'POST'])
    def index(self):
        pw = self.password
        if request.method != 'POST':
            return render_template('index.html')
        if session.get("password") is None:
            p = request.form['passwd']
            if p != pw:
                return render_template('index.html', alert_message="密码错误！！！")
            session['password'] = pw
        if session.get("password") == pw:
            for f in request.files.getlist('file'):
                if f.filename == "":
                    return render_template("index.html", alert_message="请先选择文件！")
                if path.exists("共享的文件/" + secure_filename(f.filename)):
                    f.save("共享的文件/" + uuid4().hex +
                            path.splitext(f.filename)[1])
                else:
                    f.save("共享的文件/" + secure_filename(f.filename))            
            return render_template('upload.html', alert_message="文件成功上传！")
        return render_template('index.html', alert_message="密码错误！！！")

    @app.route('/del_session', methods=['GET'])
    def delete_session():
        if request.method == 'GET':
            session.clear()
            session.pop("password", None)
            return render_template("index.html", alert_message="成功退出登录！")
class Download(Base):
    @app.route(f'{url_prefix}/', methods=['GET'])
    def file_list():
        filelist = []
        if request.method == 'GET':
            for fl in scandir("共享的文件"):
                if fl.is_file():
                    filelist.append(fl.name)
            return render_template("filelist.html", filelist=filelist)


    @app.route(f'{url_prefix}/<filename>', methods=['GET'])
    def download_file(filename):
        if request.method == 'GET':
            filepath = path.join("共享的文件/", filename)
            if path.exists(filepath):
                if path.isfile(filepath):
                    return send_file(filepath)
            abort(404)
class UploadDownload(Upload, Download):
    ...