from tkinter import Tk, mainloop, Entry, Button, Label, StringVar, IntVar, BooleanVar, Checkbutton
from tkinter.filedialog import askdirectory
from pathlib import Path
from argparse import ArgumentParser
from tkinter.messagebox import showinfo
from views import upload, download
from waitress import serve
from platform import python_version_tuple

assert python_version_tuple()[0] == '3' and int(python_version_tuple()[1]) > 10, "python版本太低，无法运行"

dir: Path = Path()
parser: ArgumentParser = ArgumentParser()
parser.add_argument('-p', '--port', type=int)
parser.add_argument('-t', '--thread', type=int)
parser.add_argument('--upload', action="store_true")
parser.add_argument('--download', action="store_true")
parser.add_argument('--debug', action="store_true")
parser.add_argument('--file_can_be_deleted', action="store_true")
file_can_be_deleted: bool | BooleanVar = parser.parse_args().file_can_be_deleted
debug_mode: bool = parser.parse_args().debug
port: int = parser.parse_args().port
threads: int = parser.parse_args().thread
if parser.parse_args().upload and parser.parse_args().download:
    mode: str = 'upload_download'
elif parser.parse_args().upload:
    mode: str = 'upload'
elif parser.parse_args().download:
    mode: str = 'download'
else:

    def ask_dir():
        global dir
        path: str = askdirectory()
        if path:
            dir = Path(path)
        else:
            try:
                Path("共享的文件").mkdir()
            except FileExistsError:
                ...
            dir = Path("共享的文件")
        showinfo("已选择文件夹", "已选择文件夹！")

    root: Tk = Tk()
    root.title("请选择")
    root.geometry("300x300")
    root.resizable(0, 0)
    if port is None:
        Label(text="端口：").pack()
        p: Entry = Entry()
        p.pack()
        p.insert(0, "80")
        port = int(p.get())
    if threads is None:
        Label(text="线程数：").pack()
        t: Entry = Entry()
        t.pack()
        t.insert(0, "6")
        threads = int(t.get())
    var1: IntVar = IntVar()
    var2: IntVar = IntVar()
    pw_temp: StringVar = StringVar()
    Checkbutton(root, text="允许他人更改“共享的文件”文件夹", variable=var1).pack()
    Checkbutton(root, text="允许他人访问“共享的文件”文件夹", variable=var2).pack()
    if not file_can_be_deleted:
        file_can_be_deleted = BooleanVar()
        Checkbutton(root,
                    text="允许他人删除“共享的文件”文件夹中的文件",
                    variable=file_can_be_deleted).pack()
    Label(text="密码：").pack()
    Entry(textvariable=pw_temp, show="*").pack()
    Label(text="文件夹：").pack()
    Button(root, text="选择文件夹", command=ask_dir).pack()
    Button(root, text="确定", command=root.destroy).pack()
    mainloop()
    if var1.get() == 1 and var2.get() == 1:
        mode = 'upload_download'
    elif var1.get() == 1:
        mode = 'upload'
    elif var2.get() == 1:
        mode = 'download'
    else:
        mode = 'upload_download'
if port is None or port <= 0 or port >= 65535:
    port = 80
if threads is None or threads <= 0:
    threads = 4

if mode == 'upload':
    if port == 80:
        showinfo("", f"在浏览器中输入您的ip地址即可允许他人更改{dir}")
    else:
        showinfo("", f"在浏览器中输入您的ip地址:{port}即可允许他人更改{dir}")
    app = upload()
elif mode == 'download':
    if port == 80:
        showinfo("", f"在浏览器中输入您的ip地址即可允许他人访问{dir}")
    else:
        showinfo("", f"在浏览器中输入您的ip地址:{port}即可允许他人访问{dir}")
    app = download()
    app.config['file_can_be_deleted'] = file_can_be_deleted
else:
    if port == 80:
        showinfo("", f"在浏览器中输入您的ip地址即可允许他人更改和访问{dir}")
    else:
        showinfo("", f"在浏览器中输入您的ip地址:{port}即可允许他人更改和访问{dir}")
    upload()
    app = download()
    app.config['file_can_be_deleted'] = file_can_be_deleted
if not dir:
    dir = Path("共享的文件")
app.config['dir'] = dir
app.config['mode'] = mode
app.config['password'] = pw_temp.get()
if debug_mode:
    app.run(port=port, debug=True, use_debugger=True, use_reloader=False)
else:
    serve(app, port=port, threads=threads)
