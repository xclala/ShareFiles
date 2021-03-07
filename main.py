_ = input("上传/下载（上传 1，下载 2）")
if _ == '1':
    from getpass import getpass
    port = input("端口：（默认80端口）")
    h = input("需要上传文件的主机的ip地址：（0.0.0.0表示所有主机）（默认0.0.0.0）")
    pw = getpass("密码：")
    if port == '':
        print("在浏览器中输入您的ip地址即可上传。（80端口不需要输入冒号和端口）")
    else:
        print("在浏览器中输入您的ip地址:"+p+"即可上传。（80端口不需要输入冒号和端口）")
    from flask import Flask, render_template, request
    from werkzeug.utils import secure_filename

    app = Flask(__name__)

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/', methods=['POST'])
    def success():
        if request.method == 'POST':
            p = request.form['passwd']
            if p == pw:
                f = request.files['file']
                f.save("上传的文件/"+secure_filename(f.filename))
                return render_template('success.html', name=f.filename)
            else:
                return render_template('wrong_password.html')

    if port == '':
        if h == '':
            app.run(debug=False, port=80, host='0.0.0.0')
        else:
            app.run(debug=False, port=80, host=h)
    else:
        if h == '':
            app.run(debug=False, port=p, host='0.0.0.0')
        else:
            app.run(debug=False, port=p, host=h)
elif _ == '2':
    from os import system
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
