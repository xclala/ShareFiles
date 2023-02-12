try:
    from tkinter import Tk, mainloop, Entry, Button, Label, StringVar, IntVar, Checkbutton
    from os import path, mkdir
    from argparse import ArgumentParser
    from tkinter.messagebox import showinfo
    from views import upload, download
    from waitress import serve

    if not path.isdir("共享的文件"):
        mkdir("共享的文件")
    parser = ArgumentParser()
    parser.add_argument('-p', '--port', type=int)
    parser.add_argument('-t', '--thread', type=int)
    parser.add_argument('--upload', action="store_true")
    parser.add_argument('--download', action="store_true")
    parser.add_argument('--debug', action="store_true")
    parser.add_argument('--file_can_be_deleted', action="store_true")
    file_can_be_deleted = parser.parse_args().file_can_be_deleted
    debug_mode = parser.parse_args().debug
    port = parser.parse_args().port
    threads = parser.parse_args().thread
    if parser.parse_args().upload and parser.parse_args().download:
        mode = 'upload_download'
    elif parser.parse_args().upload:
        mode = 'upload'
    elif parser.parse_args().download:
        mode = 'download'
    else:
        root = Tk()
        root.title("请选择")
        root.geometry("250x250")
        root.resizable(0, 0)
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
            t.insert(0, "6")
            threads = int(t.get())
        var1 = IntVar()
        var2 = IntVar()
        pw_temp = StringVar()
        Checkbutton(root, text="允许他人更改“共享的文件”文件夹", variable=var1).pack()
        Checkbutton(root, text="允许他人访问“共享的文件”文件夹", variable=var2).pack()
        if not file_can_be_deleted:
            file_can_be_deleted = StringVar()
            Checkbutton(root,
                        text="允许他人删除“共享的文件”文件夹中的文件",
                        variable=file_can_be_deleted, 
                        onvalue=True, offvalue=False).pack()
            file_can_be_deleted = file_can_be_deleted.get()
        Label(text="密码：").pack()
        Entry(textvariable=pw_temp, show="*").pack()
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
            showinfo("", "在浏览器中输入您的ip地址即可允许他人更改“共享的文件”文件夹")
        else:
            showinfo("", f"在浏览器中输入您的ip地址:{port}即可允许他人更改“共享的文件”文件夹")
        app = upload()
        app.config['mode'] = 'upload'
    elif mode == 'download':
        if port == 80:
            showinfo("", "在浏览器中输入您的ip地址即可允许他人访问“共享的文件”文件夹")
        else:
            showinfo("", f"在浏览器中输入您的ip地址:{port}即可允许他人访问“共享的文件”文件夹")
        app = download()
        app.config['mode'] = 'download'
        app.config['file_can_be_deleted'] = file_can_be_deleted
    else:
        if port == 80:
            showinfo("", "在浏览器中输入您的ip地址即可允许他人更改和访问“共享的文件”文件夹")
        else:
            showinfo("", f"在浏览器中输入您的ip地址:{port}即可允许他人更改和访问“共享的文件”文件夹")
        upload()
        app = download()
        app.config['mode'] = 'upload_download'
        app.config['file_can_be_deleted'] = file_can_be_deleted
    app.config['password'] = pw_temp.get()
    if debug_mode:
        app.run(port=port, debug=True, use_debugger=True, use_reloader=True)
    else:
        serve(app, port=port, threads=threads)
except Exception as e:
    print(e)