from os import abort, system, path, urandom, getcwd, mkdir, listdir, walk
from flask import Flask, render_template, request, session, send_file, abort
from flask_wtf.csrf import CSRFProtect
from werkzeug.utils import secure_filename
from uuid import uuid4
from waitress import serve

app = Flask(__name__)
app.config['SECRET_KEY'] = urandom(666)
CSRFProtect(app)
port = input("端口：（默认80端口）")
_ = input("让别人上传输入 1，让别人下载输入 2：")
if _ == '1':
    from getpass import getpass
    system("title 上传文件")
    pw = getpass("密码：")
    if port == '':
        print("在浏览器中输入您的ip地址即可上传。（80端口不需要输入冒号和端口）")
    else:
        print("在浏览器中输入您的ip地址:" + port + "即可上传。（80端口不需要输入冒号和端口）")
    if not path.exists(path.join(getcwd(), "别人上传的文件")):
        mkdir("别人上传的文件")
    @app.route('/', methods=['GET', 'POST'])
    def index():
        if request.method == 'POST':
            if session.get("password") is None:
                p = request.form['passwd']
                if p == pw:
                    for f in request.files.getlist('file'):
                        session['password'] = pw
                        if f.filename != "":
                            if path.exists("别人上传的文件/" +
                                           secure_filename(f.filename)):
                                f.save("别人上传的文件/" + uuid4().hex +
                                       path.splitext(f.filename)[1])
                            else:
                                f.save("别人上传的文件/" +
                                       secure_filename(f.filename))
                        else:
                            return render_template("index.html",
                                                   alert_message="请先选择文件！")
                    return render_template('upload.html',
                                           alert_message="文件成功上传！")
                    #这个return与for循环缩进相同，这样才能保存完多个文件后再return，进而实现多文件上传
                else:
                    return render_template('index.html',
                                           alert_message="密码错误！！！")
            else:
                for f in request.files.getlist('file'):
                    if f.filename != "":
                        if path.exists("别人上传的文件/" +
                                       secure_filename(f.filename)):
                            f.save("别人上传的文件/" + uuid4().hex +
                                   path.splitext(f.filename)[1])
                        else:
                            f.save("别人上传的文件/" + secure_filename(f.filename))
                    else:
                        return render_template("index.html",
                                               alert_message="请先选择文件！")
                return render_template('upload.html', alert_message="文件成功上传！")
                #这个return与for循环缩进相同，这样才能保存完多个文件后再return，进而实现多文件上传
        else:
            return render_template('index.html')

    @app.route('/del_session', methods=['GET'])
    def delete_session():
        if request.method == 'GET':
            session.clear()
            session.pop("password", None)
            return render_template("index.html", alert_message="成功退出登录！")
elif _ == '2':

    @app.route('/', methods=['GET'])
    def file_list():
        if request.method == 'GET':
            for ___, _________, fl in walk("让别人下载的文件"):
                if fl != []:
                    return render_template("filelist.html", filelist=fl)
                else:
                    return render_template("filelist.html", filelist="")

    @app.route('/<filename>', methods=['GET'])
    def download_file(filename):
        if request.method == 'GET':
            from io import BytesIO
            from mimetypes import guess_type
            filepath = path.join("让别人下载的文件/", filename)
            if path.exists(filepath):
                if path.isfile(filepath):
                    with open(filepath, 'rb') as file_object:
                        return send_file(BytesIO(file_object.read()),
                                         mimetype=guess_type(filepath)[0])
                else:
                    abort(404)
            else:
                abort(404)


if port == '':
    serve(app, host='0.0.0.0', port=80)

else:
    serve(app, host='0.0.0.0', port=port)
