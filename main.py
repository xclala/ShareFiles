try:
    from tkinter import Tk, mainloop, Entry, Button, Label, StringVar, IntVar, Checkbutton
    from os import path, getcwd, mkdir
    from argparse import ArgumentParser
    from tkinter.messagebox import showinfo
    from views import upload, download, upload_download

    if not path.exists(path.join(getcwd(), "共享的文件")):
        mkdir("共享的文件")
    parser = ArgumentParser()
    parser.add_argument('-p', '--port', type=int)
    parser.add_argument('-t', '--thread', type=int)
    parser.add_argument('--upload', action="store_true")
    parser.add_argument('--download', action="store_true")
    port = parser.parse_args().port
    threads = parser.parse_args().thread
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
            root.geometry("250x250")
            root.resizable(0, 0)
            root.protocol("WM_DELETE_WINDOW", lambda: ...)
            if port is None:
                Label(text="端口：").pack()
                p = Entry()
                p.pack()
                p.insert(0, "80")
                port = int(p.get())
            if threads is None:
                Label(text="线程数：").pack()
                t = Entry()
                t.pack()
                t.insert(0, "4")
                threads = int(t.get())
            var1 = IntVar()
            var2 = IntVar()
            pw_temp = StringVar()
            Checkbutton(root, text="允许他人更改“共享的文件”文件夹", variable=var1).pack()
            Checkbutton(root, text="允许他人访问“共享的文件”文件夹", variable=var2).pack()
            Label(text="密码：").pack()
            Entry(textvariable=pw_temp, show="*").pack()
            Button(root, text="确定", command=root.destroy).pack()
            mainloop()
            if var1.get() == 1 and var2.get() == 1:
                _ = '0'  #既上传又下载
            elif var1.get() == 1:
                _ = '1'  #上传
            elif var2.get() == 1:
                _ = '2'  #下载
            else:
                _ = '0'
    if port is None or port <= 0:
        port = 80
    if threads is None or threads <= 0:
        threads = 4

    if _ == '1':
        if port == 80:
            showinfo("", "在浏览器中输入您的ip地址即可允许他人更改“共享的文件”文件夹")
        else:
            showinfo("", f"在浏览器中输入您的ip地址:{port}即可允许他人更改“共享的文件”文件夹")
        upload(port, threads, pw_temp.get())
    elif _ == '2':
        if port == 80:
            showinfo("", "在浏览器中输入您的ip地址即可允许他人访问“共享的文件”文件夹")
        else:
            showinfo("", f"在浏览器中输入您的ip地址:{port}即可允许他人访问“共享的文件”文件夹")
        download(port, threads, pw_temp.get())
    elif _ == '0':
        if port == 80:
            showinfo("", "在浏览器中输入您的ip地址即可允许他人更改和访问“共享的文件”文件夹")
        else:
            showinfo("", f"在浏览器中输入您的ip地址:{port}即可允许他人更改和访问“共享的文件”文件夹")
        upload_download(port, threads, pw_temp.get())
except Exception as e:
    print(e)
