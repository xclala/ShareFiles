try:
    from tkinter import Tk, mainloop, Entry, Button, Label, StringVar, IntVar, Checkbutton
    from os import path, getcwd, mkdir
    from argparse import ArgumentParser
    from tkinter.messagebox import showinfo
    from logic import Upload, Download, UploadDownload

    if not path.exists(path.join(getcwd(), "共享的文件")):
        mkdir("共享的文件")
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
        port = askinteger(title="请输入端口", prompt="请输入端口", initialvalue=80)
    if threads is None:
        from tkinter.simpledialog import askinteger
        threads = askinteger(title="请输入线程数", prompt="请输入线程数", initialvalue=4)
    if parser.parse_args().upload:
        if parser.parse_args().download:
            _ = '0'
        else:
            _ = '1'
    if parser.parse_args().download:
        _ = '2'
    if not parser.parse_args().upload:
        if not parser.parse_args().download:
            root = Tk()
            root.title("请选择")
            root.geometry("250x100")
            root.resizable(0, 0)
            root.protocol("WM_DELETE_WINDOW", lambda:...)
            var1 = IntVar()
            var2 = IntVar()
            Checkbutton(root, text="允许他人更改“共享的文件”文件夹", variable=var1).pack()
            Checkbutton(root, text="允许他人访问“共享的文件”文件夹", variable=var2).pack()
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
    if port is None or port <= 0:
        port = 80
    if threads is None or threads <= 0:
        threads = 4
    def enter_password():
        r = Tk()
        r.title("请输入密码")
        r.geometry("250x100")
        r.resizable(0, 0)
        pw_temp = StringVar()
        r.protocol("WM_DELETE_WINDOW", lambda:...)
        Label(r, text="密码：").pack()
        Entry(r, textvariable=pw_temp, show="*").pack()
        Button(text="确定", command=r.destroy).pack()
        mainloop()
        return pw_temp.get()
    if _ == '1':
        if port == 80:
            showinfo("", "在浏览器中输入您的ip地址即可允许他人更改“共享的文件”文件夹")
        else:
            showinfo("", f"在浏览器中输入您的ip地址:{port}即可允许他人更改“共享的文件”文件夹")
        Upload(port, threads, pw=enter_password())
    elif _ == '2':
        if port == 80:
            showinfo("", "在浏览器中输入您的ip地址即可允许他人访问“共享的文件”文件夹")
        else:
            showinfo("", f"在浏览器中输入您的ip地址:{port}即可允许他人访问“共享的文件”文件夹")
        Download(port, threads)
    elif _ == '0':
        if port == 80:
            showinfo("", "在浏览器中输入您的ip地址即可允许他人更改和访问“共享的文件”文件夹")
        else:
            showinfo("", f"在浏览器中输入您的ip地址:{port}即可允许他人更改和访问“共享的文件”文件夹")
        UploadDownload(port, threads, pw=enter_password(), prefix="/filelist")
except Exception as e:
    print(e)