from flask import Flask, render_template, request, session, abort, send_from_directory, flash, url_for, redirect
from flask_wtf.csrf import CSRFProtect
from secrets import token_urlsafe
from uuid import uuid4
from datetime import timedelta

app = Flask(__name__)
app.config['SECRET_KEY'] = token_urlsafe(64)
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
    _filename_gbk_strip_re = compile(u"[^\u4e00-\u9fa5A-Za-z0-9_.-]")
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
    filename = filename.encode("utf-8", "ignore").decode("utf-8")

    for sep in os.path.sep, os.path.altsep:
        if sep:
            filename = filename.replace(sep, " ")
    filename = str(_filename_gbk_strip_re.sub("", "_".join(
        filename.split()))).strip("._")

    # on nt a couple of special files are present in each folder.  We
    # have to ensure that the target file is not such a filename.  In
    # this case we prepend an underline
    if (os.name == "nt" and filename
            and filename.split(".")[0].upper() in _windows_device_files):
        filename = f"_{filename}"

    return filename


@app.before_request
def is_login():
    if request.path == url_for('login'):
        return None
    if request.path == url_for('static', filename='style.css'):
        return None
    if request.path == url_for('static', filename='script.js'):
        return None
    if session.get("password") == app.config['password']:
        return None
    return redirect(url_for('login'))


def login():
    if session.get("password") == app.config['password']:
        if app.config['mode'] == 'download':
            return redirect(url_for('filelist_view'))
        return redirect(url_for('upload_view'))
    if request.method == 'POST':
        if request.form['passwd'] == app.config['password']:
            if request.form['session-lifetime'] != 'default':
                session.permanent = True
                app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(
                    days=int(request.form['session-lifetime']))
            session['password'] = request.form['passwd']
            if app.config['mode'] == 'download':
                return redirect(url_for('filelist_view'))
            return redirect(url_for('upload_view'))
        else:
            flash("密码错误！")
    return render_template('login.html')


def upload_view():
    if request.method == 'POST':
        for f in request.files.getlist('file'):
            if not secure_filename(f.filename):
                flash("请先选择文件！")
                return render_template("upload.html")
            path = app.config['dir'] / secure_filename(f.filename)
            if path.exists():
                f.save("共享的文件/" + uuid4().hex + path.suffix)
            else:
                f.save("共享的文件/" + secure_filename(f.filename))
        flash("文件成功上传！")
    if app.config['mode'] == 'upload':
        return render_template('upload.html')
    return render_template('upload.html', filelist=filelist(), title="共享文件")


def delete_session():
    session.clear()
    session.pop("password", None)
    flash("成功退出登录！")
    return redirect(url_for('login'))


def filelist():
    filelist = []
    for fl in app.config['dir'].iterdir():
        if fl.is_file():
            secure_rename(fl)
            filelist.append(secure_filename(str(fl)))
    return filelist


def filelist_view():
    return render_template("download.html", filelist=filelist())


def download_file(filename):
    return send_from_directory(str(app.config['dir']),
                               secure_filename(filename),
                               as_attachment=True)


def delete_file(filename):
    if app.config['file_can_be_deleted']:
        p = app.config['dir'] / secure_filename(filename)
        if p.isfile():
            p.unlink()
            flash("文件成功删除！")
        else:
            flash("文件不存在！")
    else:
        flash("此文件不可被删除！")
    return redirect(url_for('filelist_view'))


def newfile():
    if request.method == 'POST':
        if secure_filename(request.form['filename']):
            filepath = app.config['dir'] / secure_filename(
                request.form['filename'])
            filepath.write_text(request.form['content'], encoding="utf-8")
            flash("成功新建文件！")
            return redirect('/')
        flash("请输入正确的文件名！")
    return render_template('newfile.html')


def edit(filename):
    if app.config['mode'] == 'upload_download':
        filename = secure_filename(filename)
        filepath = app.config['dir'] / filename
        if not filepath.is_file():
            abort(404)
        if is_binary_file(filepath):
            flash("此文件不可被编辑！")
            return redirect('/')
        if request.method == 'POST':
            if secure_filename(request.form['filename']):
                secure_rename(request.form['filename'])
            else:
                flash("请输入正确的文件名！")
                return render_template('edit.html',
                                       filename=filename,
                                       file_content=file_content)
            path = app.config['dir'] / request.form['filename']
            path.write_text(request.form['content'], encoding(filepath))
            return redirect('/')
        file_content = filepath.read_text(encoding(filepath))
        return render_template('edit.html',
                               filename=filename,
                               file_content=file_content)
    flash("此文件不可被编辑！")
    return redirect('/')


def encoding(filepath):
    from chardet import detect
    data = filepath.read_bytes()
    return detect(data)["encoding"]


def is_binary_file(filepath):
    import codecs
    _TEXT_BOMS = (
        codecs.BOM_UTF16_BE,
        codecs.BOM_UTF16_LE,
        codecs.BOM_UTF32_BE,
        codecs.BOM_UTF32_LE,
        codecs.BOM_UTF8,
    )
    with open(filepath, 'rb') as file:
        initial_bytes = file.read(8192)
        file.close()
        for bom in _TEXT_BOMS:
            if initial_bytes.startswith(bom):
                continue
            else:
                if b'\0' in initial_bytes:
                    return True
    return False


def secure_rename(filename):
    a = app.config['dir'] / filename
    try:
        if secure_filename(str(filename)):
            a = app.config['dir'] / filename
            b = app.config['dir'] / secure_filename(str(filename))
            a.rename(b)
        else:
            raise FileExistsError
    except FileExistsError:
        c = app.config['dir'] / uuid4().hex / a.suffix
        a.rename(c)


app.add_url_rule('/', view_func=login, methods=['GET', 'POST'])
app.add_url_rule('/del_session', view_func=delete_session, methods=['GET'])


def upload():
    app.add_url_rule('/upload', view_func=upload_view, methods=['GET', 'POST'])
    app.add_url_rule('/newfile', view_func=newfile, methods=['GET', 'POST'])
    app.add_url_rule('/edit/<filename>',
                     view_func=edit,
                     methods=['GET', 'POST'])
    return app


def download():
    app.add_url_rule('/filelist',
                     view_func=filelist_view,
                     methods=['GET', 'POST'])
    app.add_url_rule("/filelist/<filename>",
                     view_func=download_file,
                     methods=['GET'])
    app.add_url_rule('/delete/<filename>',
                     view_func=delete_file,
                     methods=['GET'])
    return app
