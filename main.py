from os import system, path, urandom, getcwd, mkdir
from flask import Flask, redirect
from flask_wtf.csrf import CSRFProtect
from waitress import serve
from argparse import ArgumentParser
from tkinter.messagebox import showinfo

app = Flask(__name__)
app.config['SECRET_KEY'] = urandom(666)
CSRFProtect(app)
parser = ArgumentParser()  
parser.add_argument('-p', '--port', type=int)  
parser.add_argument('-t', '--thread', type=int)  
parser.add_argument('--upload', action="store_true") 
parser.add_argument('--download',
                    action="store_true")  
port = parser.parse_args().port  
threads = parser.parse_args().thread 
if port is None:
    from tkinter.simpledialog import askinteger
    port = askinteger(title="请输入端口",prompt="请输入端口",initialvalue=80)
if threads is None:
    from tkinter.simpledialog import askinteger
    threads = askinteger(title="请输入线程数",prompt="请输入线程数",initialvalue=4)
if parser.parse_args().upload:
    if parser.parse_args().download:
        _ = '0'  
    else:
        _ = '1'  
if parser.parse_args().download:
    _ = '2'  
if not parser.parse_args().upload:
    if not parser.parse_args().download:
        from tkinter import Tk, Button, Checkbutton, IntVar, mainloop
        root = Tk()
        root.title("请选择")
        root.geometry("250x100")
        root.resizable(0, 0)
        root.protocol("WM_DELETE_WINDOW", lambda:...)
        var1 = IntVar()
        var2 = IntVar()
        Checkbutton(root, text="上传文件", variable=var1).pack()
        Checkbutton(root, text="下载文件", variable=var2).pack()
        Button(root, text="确定", command=root.destroy).pack()
        mainloop()
        if var1.get() == 1 and var2.get() == 1:
            _ = '0' #既上传又下载
        elif var1.get() == 1:
            _ = '1' #上传
        elif var2.get() == 1:
            _ = '2' #下载
        else:
            _ = '0'
#一定要在导入upload和download之前获取端口、线程数、上传或下载或上传又下载
if _ == '1':
    if not path.exists(path.join(getcwd(), "别人上传的文件")):
        mkdir("别人上传的文件")
    from upload import app as upload
    system("title 上传文件")

    @app.errorhandler(404)
    def notfound(_):
        return redirect("/")

    app.register_blueprint(upload)
    if port == '':
        showinfo("", "在浏览器中输入您的ip地址即可上传。")
    else:
        showinfo("", f"在浏览器中输入您的ip地址:{port}即可上传。")
elif _ == '2':
    if not path.exists(path.join(getcwd(), "让别人下载的文件")):
        mkdir("让别人下载的文件")
    from download import app as download
    system("title 下载文件")
    app.register_blueprint(download)
    if port == '':
        showinfo("", "在浏览器中输入您的ip地址即可下载。")
    else:
        showinfo("", f"在浏览器中输入您的ip地址:{port}即可下载。")
elif _ == '0':
    from upload import app as upload
    from download import app as download
    system("title 上传和下载文件")
    if not path.exists(path.join(getcwd(), "别人上传的文件")):
        mkdir("别人上传的文件")
    if not path.exists(path.join(getcwd(), "让别人下载的文件")):
        mkdir("让别人下载的文件")
    app.register_blueprint(upload)
    app.register_blueprint(download, url_prefix='/filelist')
    if port == '':
        showinfo("", "在浏览器中输入您的ip地址即可上传和下载。")
    else:
        showinfo("", f"在浏览器中输入您的ip地址:{port}即可上传和下载。")
if __name__ == "__main__":
    if port == '':
        if threads == '':
            serve(app, host='0.0.0.0', port=80)
        else:
            serve(app, host='0.0.0.0', port=80, threads=str(threads))
    else:
        if threads == '':
            serve(app, host='0.0.0.0', port=str(port))
        else:
            serve(app, host='0.0.0.0', port=str(port), threads=str(threads))
