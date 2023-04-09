from tkinter import Tk, mainloop, Entry, Button, Label, StringVar, IntVar, BooleanVar, Checkbutton
from tkinter.filedialog import askdirectory
from pathlib import Path
from argparse import ArgumentParser
from tkinter.messagebox import showinfo
from views import register_upload, register_download
from waitress import serve
from platform import python_version_tuple

assert python_version_tuple()[0] == '3' and int(
    python_version_tuple()[1]) > 10, "python版本太低，无法运行"

dir: Path = Path()
parser: ArgumentParser = ArgumentParser()
parser.add_argument('-p', '--port', type=int)
parser.add_argument('-t', '--thread', type=int)
parser.add_argument('--upload', action="store_true")
parser.add_argument('--download', action="store_true")
parser.add_argument('--debug', action="store_true")
parser.add_argument('--file_can_be_deleted', action="store_true")
delete_permission: bool | BooleanVar = parser.parse_args(
).file_can_be_deleted
debug_mode: bool = parser.parse_args().debug
port: int = parser.parse_args().port
threads: int = parser.parse_args().thread
upload: bool = parser.parse_args().upload
download: bool = parser.parse_args().download
if not parser.parse_args().upload and not parser.parse_args().download:
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
    root.resizable(False, False)
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
    var1: BooleanVar = BooleanVar()
    var2: BooleanVar = BooleanVar()
    pw_temp: StringVar = StringVar()
    var1.set(True)
    var2.set(True)
    Checkbutton(root, text="允许他人更改“共享的文件”文件夹", variable=var1).pack()
    Checkbutton(root, text="允许他人访问“共享的文件”文件夹", variable=var2).pack()
    if not delete_permission:
        delete_permission = BooleanVar()
        Checkbutton(root,
                    text="允许他人删除“共享的文件”文件夹中的文件",
                    variable=delete_permission).pack()
    Label(text="密码：").pack()
    Entry(textvariable=pw_temp, show="*").pack()
    Label(text="文件夹：").pack()
    Button(root, text="选择文件夹", command=ask_dir).pack()
    Button(root, text="确定", command=root.destroy).pack()
    mainloop()
    upload: bool = var1.get()
    download: bool = var2.get()
if port is None or port <= 0 or port >= 65535:
    port = 80
if threads is None or threads <= 0:
    threads = 6

if upload:
    if port == 80:
        showinfo("", f"在浏览器中输入您的ip地址即可允许他人更改{dir}")
    else:
        showinfo("", f"在浏览器中输入您的ip地址:{port}即可允许他人更改{dir}")
    app = register_upload()
if download:
    if port == 80:
        showinfo("", f"在浏览器中输入您的ip地址即可允许他人访问{dir}")
    else:
        showinfo("", f"在浏览器中输入您的ip地址:{port}即可允许他人访问{dir}")
    app = register_download()
    app.config['delete_permission'] = delete_permission.get()
if dir == Path():
    dir = Path("共享的文件")
app.config['dir'] = dir
app.config['upload'] = upload
app.config['download'] = download
app.config['password'] = pw_temp.get()
if debug_mode:
    app.run(port=port, debug=True, use_debugger=True, use_reloader=False)
else:
    serve(app, port=port, threads=threads)
