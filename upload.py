try:
    from flask import Blueprint, render_template, request, session
    from os import path
    from werkzeug.utils import secure_filename
    from uuid import uuid4
    from tkinter import Tk, mainloop, Entry, Button, Label, StringVar

    app = Blueprint('upload', __name__)
    root = Tk()
    root.title("请输入密码")
    root.geometry("250x100")
    root.resizable(0, 0)
    pw_temp = StringVar()
    root.protocol("WM_DELETE_WINDOW", lambda:...)
    Label(root, text="密码：").pack()
    Entry(root, textvariable=pw_temp, show="*").pack()
    Button(text="确定", command=root.destroy).pack()
    mainloop()
    pw = pw_temp.get()


    @app.route('/', methods=['GET', 'POST'])
    def index():
        if request.method != 'POST':
            return render_template('index.html')
        if session.get("password") is None:
            p = request.form['passwd']
            if p != pw:
                return render_template('index.html', alert_message="密码错误！！！")
            session['password'] = pw
        for f in request.files.getlist('file'):
            if f.filename == "":
                return render_template("index.html", alert_message="请先选择文件！")
            if path.exists("共享的文件/" + secure_filename(f.filename)):
                f.save("共享的文件/" + uuid4().hex +
                        path.splitext(f.filename)[1])
            else:
                f.save("共享的文件/" + secure_filename(f.filename))            
        return render_template('upload.html', alert_message="文件成功上传！")


    @app.route('/del_session', methods=['GET'])
    def delete_session():
        if request.method == 'GET':
            session.clear()
            session.pop("password", None)
            return render_template("index.html", alert_message="成功退出登录！")
except Exception as e:
    print(e)