from flask import Blueprint, render_template, request, session
from os import path
from werkzeug.utils import secure_filename
from uuid import uuid4
from getpass import getpass

app = Blueprint('upload', __name__)
pw = getpass("密码：")


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
                            f.save("别人上传的文件/" + secure_filename(f.filename))
                    else:
                        return render_template("index.html",
                                               alert_message="请先选择文件！")
                return render_template('upload.html', alert_message="文件成功上传！")
                #这个return与for循环缩进相同，这样才能保存完多个文件后再return，进而实现多文件上传
            else:
                return render_template('index.html', alert_message="密码错误！！！")
        else:
            for f in request.files.getlist('file'):
                if f.filename != "":
                    if path.exists("别人上传的文件/" + secure_filename(f.filename)):
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
