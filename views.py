from flask import Flask, render_template, request, session, abort, send_file, flash
from flask_wtf.csrf import CSRFProtect
from waitress import serve
from os import path, urandom, scandir
from uuid import uuid4

app = Flask(__name__)
app.config['SECRET_KEY'] = urandom(666)
CSRFProtect(app)


def secure_filename(filename):
    r"""Pass it a filename and it will return a secure version of it.  This
    filename can then safely be stored on a regular file system and passed
    to :func:`os.path.join`.

    On windows systems the function also makes sure that the file is not
    named after one of the special device files.

    >>> secure_filename("My cool movie.mov")
    'My_cool_movie.mov'
    >>> secure_filename("../../../etc/passwd")
    'etc_passwd'
    >>> secure_filename('i contain cool \xfcml\xe4uts.txt')
    'i_contain_cool_umlauts.txt'

    The function might return an empty filename.  It's your responsibility
    to ensure that the filename is unique and that you abort or
    generate a random filename if the function returned an empty one.

    :param filename: the filename to secure
    """
    from unicodedata import normalize
    from re import compile
    import os
    _filename_ascii_strip_re = compile(r"[^A-Za-z0-9_\u4E00-\u9FBF.-]")
    _windows_device_files = (
        "CON",
        "AUX",
        "COM1",
        "COM2",
        "COM3",
        "COM4",
        "LPT1",
        "LPT2",
        "LPT3",
        "PRN",
        "NUL",
    )
    filename = normalize("NFKD", filename)
    filename = filename.encode("ascii", "ignore").decode("utf-8")

    for sep in path.sep, path.altsep:
        if sep:
            filename = filename.replace(sep, " ")
    filename = str(_filename_ascii_strip_re.sub("", "_".join(
        filename.split()))).strip("._")

    # on nt a couple of special files are present in each folder.  We
    # have to ensure that the target file is not such a filename.  In
    # this case we prepend an underline
    if (os.name == "nt" and filename
            and filename.split(".")[0].upper() in _windows_device_files):
        filename = f"_{filename}"

    return filename


def upload_view():
    if request.method == 'POST':
        password = app.config['password']
        if session.get("password") is None:
            p = request.form['passwd']
            if p != password:
                flash("密码错误！！！")
                return render_template('index.html')
            session['password'] = password
        if session.get("password") == password:
            for f in request.files.getlist('file'):
                if secure_filename(f.filename) == "":
                    flash("请先选择文件！")
                    return render_template("index.html")
                if path.exists("共享的文件/" + secure_filename(f.filename)):
                    f.save("共享的文件/" + uuid4().hex +
                           path.splitext(f.filename)[1])
                else:
                    f.save("共享的文件/" + secure_filename(f.filename))
            flash("文件成功上传！")
            return render_template('upload.html')
        flash("密码错误！！！")
        return render_template('index.html')
    else:
        return render_template('index.html')


def delete_session():
    session.clear()
    session.pop("password", None)
    flash("成功退出登录！")
    return render_template(app.config['del_session_template'])


def filelist():
    password = app.config['password']
    if request.method == 'GET':
        if session.get("password") == password:
            filelist = []
            for fl in scandir("共享的文件"):
                if fl.is_file():
                    filelist.append(fl.name)
            return render_template("download.html", filelist=filelist)
        elif session.get("password") is None:
            return render_template("filelist.html",
                                   filelist='')
    if request.method == 'POST':
        if request.form['passwd'] == password:
            session['password'] = request.form['passwd']
            filelist = []
            for fl in scandir("共享的文件"):
                if fl.is_file():
                    filelist.append(fl.name)
            return render_template("download.html", filelist=filelist)
    flash("密码错误！")
    return render_template("filelist.html",
                            filelist='')


def download_file(filename):
    password = app.config['password']
    if password == session.get('password'):
        filepath = path.join("共享的文件/", secure_filename(filename))
        if path.exists(filepath) and path.isfile(filepath):
            return send_file(filepath)
        abort(404)
    flash("密码错误！")
    return render_template("filelist.html",
                            filelist='')


def upload(port, thread, pw):
    app.config['password'] = pw
    app.config['del_session_template'] = "index.html"
    app.add_url_rule('/', view_func=upload_view)
    app.add_url_rule('/del_session', view_func=delete_session)
    serve(app, port=port, threads=thread)


def download(port, thread, pw):
    app.config['password'] = pw
    app.config['del_session_template'] = "filelist.html"
    app.add_url_rule("/", view_func=filelist)
    app.add_url_rule("/filelist/<filename>", view_func=download_file)
    app.add_url_rule('/del_session', view_func=delete_session)
    serve(app, port=port, threads=thread)


def upload_download(port, thread, pw):
    app.config['password'] = pw
    app.add_url_rule("/filelist", view_func=filelist)
    app.add_url_rule("/filelist/<filename>", view_func=download_file)
    upload(port, thread, pw)
