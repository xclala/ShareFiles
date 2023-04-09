from flask import Flask, render_template, request, session, abort, send_from_directory, flash, url_for, redirect
from flask_wtf.csrf import CSRFProtect
from secrets import token_urlsafe
from uuid import uuid4
from datetime import timedelta
from pathlib import Path
from typing import Optional, Iterable, Literal

app: Flask = Flask(__name__)
app.config['SECRET_KEY'] = token_urlsafe(64)
CSRFProtect(app)


def secure_filename(filename: str | Path | None) -> str:
    r"""传入文件名，它会返回其安全版本。
        此文件名可以用于指定文件系统的路径和用于路径拼接。

    >>> secure_filename("My cool movie.mov")
    'My_cool_movie.mov'
    >>> secure_filename("../../../etc/passwd")
    'etc_passwd'
    >>> secure_filename('i contain cool \xfcml\xe4uts.txt')
    'i_contain_cool_umlauts.txt'

    如果文件名整个都有问题，那么会返回随机文件名

    :参数 filename: 需要被安全处理的字符串或pathlib对象
    """
    from unicodedata import normalize
    from re import compile
    import os
    _filename_gbk_strip_re = compile(u"[^\u4e00-\u9fa5A-Za-z0-9_.-]")
    _windows_device_files: tuple[str, ...] = (
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
    filename = str(filename)
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

    if filename:
        return filename
    else:
        return uuid4().hex


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
        if app.config['download']:
            return redirect(url_for('filelist', filepath=''))
        return redirect(url_for('upload'))
    if request.method == 'POST':
        if request.form['passwd'] == app.config['password']:
            if request.form['session-lifetime'] != 'default':
                session.permanent = True
                app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(
                    days=int(request.form['session-lifetime']))
            session['password'] = request.form['passwd']
            if app.config['download']:
                return redirect(url_for('filelist', filepath=''))
            return redirect(url_for('upload'))
        else:
            flash("密码错误！")
    return render_template('login.html')


def upload():
    try:
        if request.method == 'POST':

            def save_files(f):
                if not f.filename:
                    flash("请先选择文件！")
                    return render_template("upload.html")
                path: Path = app.config['dir'] / secure_filename(f.filename)
                if path.exists():
                    f.save(app.config['dir'] / uuid4().hex + path.suffix)
                else:
                    f.save(path)

            map(save_files, request.files.getlist('file'))
            flash("文件成功上传！")
        if app.config['upload']:
            return render_template('upload.html')
        map(secure_rename, app.config['dir'].iterdir())
        fl: Iterable = map(lambda p: p.relative_to(app.config['dir']),
                           app.config['dir'].iterdir())
        return render_template('upload.html', filelist=fl, title="共享文件")
    except PermissionError:
        flash("权限不足！")
        return render_template("upload.html")


def delete_session():
    session.clear()
    session.pop("password", None)
    flash("成功退出登录！")
    return redirect(url_for('login'))


def filelist(filepath: str):
    try:
        path: Path = app.config['dir'] / filepath.replace("..", "")
        if path.is_file():
            return send_from_directory(app.config['dir'],
                                       path,
                                       as_attachment=True)
        if path.is_dir():
            map(secure_rename, path.iterdir())
            fl: Iterable = map(lambda p: p.relative_to(path), path.iterdir())
            return render_template("download.html",
                                   filelist=fl,
                                   filepath=filepath.replace("..", ""))
        abort(404)
    except PermissionError:
        abort(403)


def delete_file(filepath: str):
    if app.config['delete_permission']:
        p: Path = app.config['dir'] / filepath.replace("..", "")
        try:
            from win32com.shell import shell, shellcon
            shell.SHFileOperation(
                (0, shellcon.FO_DELETE, str(p), None, shellcon.FOF_SILENT
                 | shellcon.FOF_ALLOWUNDO | shellcon.FOF_NOCONFIRMATION))
        except PermissionError:
            flash("你没有删除文件的权限！")
        except:
            if p.is_file():
                p.unlink()
                flash("文件成功删除！")
            elif p.is_dir():
                from shutil import rmtree
                rmtree(p)
                flash("目录成功删除！")
            else:
                flash("文件不存在！")
    else:
        flash("你没有删除文件的权限！")
    return redirect("/")


def newfile(path: str):
    filepath: Path = app.config['dir'] / path.replace("..", "")
    try:
        filepath.touch(exist_ok=False)
    except PermissionError:
        flash("权限不足！")
        return redirect('/')
    except FileExistsError:
        return redirect(url_for('edit', path=path))
    else:
        return redirect(url_for('edit', path=path))


def edit(path: str):
    try:
        if app.config['upload']:
            raise PermissionError
        filepath: Path = app.config['dir'] / path.replace('..', '')
        if not filepath.is_file():
            abort(404)
        if is_binary_file(filepath):
            raise PermissionError
        file_content: str = filepath.read_text(encoding(filepath))
        if request.method == 'POST':
            if secure_filename(Path(request.form['filepath']).name):
                filepath.rename(app.config['dir'] /
                                (request.form['filepath']).replace("..", ""))
                filepath = app.config['dir'] / (
                    request.form['filepath']).replace("..", "")
            else:
                flash("请输入正确的路径！")
                return render_template('edit.html',
                                       filepath=filepath,
                                       file_content=file_content)
            path: Path = app.config['dir'] / request.form['filepath'].replace(
                "..", "")
            path.write_text(request.form['content'], encoding(filepath))
            return redirect('/')
        return render_template('edit.html',
                               filepath=path,
                               file_content=file_content)
    except PermissionError:
        flash("此文件不可被编辑！")
        return redirect('/')


def encoding(filepath: Path) -> Optional[str]:
    from chardet import detect
    data: bytes = filepath.read_bytes()
    return detect(data)["encoding"]


def is_binary_file(filepath: str | Path) -> bool:
    filepath = str(filepath)
    import codecs
    _TEXT_BOMS: tuple[Literal, Literal, Literal, Literal, Literal] = (
        codecs.BOM_UTF16_BE,
        codecs.BOM_UTF16_LE,
        codecs.BOM_UTF32_BE,
        codecs.BOM_UTF32_LE,
        codecs.BOM_UTF8,
    )
    with open(filepath, 'rb') as file:
        initial_bytes: bytes = file.read(8192)
        file.close()
        for bom in _TEXT_BOMS:
            if initial_bytes.startswith(bom):
                continue
            else:
                if b'\0' in initial_bytes:
                    return True
    return False


def secure_rename(filepath: Path):
    import os
    """将文件名送入secure_filename()，并将文件名更改为secure_filename()的返回值。
    在windows中，$RECYCLE.BIN会被忽略。
    """
    if os.name != 'nt' or filepath != '$RECYCLE.BIN':
        try:
            if filepath.is_file():
                filepath.rename(filepath.parent /
                                secure_filename(filepath.name))
        except FileExistsError:
            filepath.rename(uuid4().hex + filepath.suffix)


app.add_url_rule('/', view_func=login, methods=['GET', 'POST'])
app.add_url_rule('/del_session', view_func=delete_session, methods=['GET'])


def register_upload() -> Flask:
    app.add_url_rule('/upload', view_func=upload, methods=['GET', 'POST'])
    app.add_url_rule('/newfile/<path:path>',
                     view_func=newfile,
                     methods=['GET'])
    app.add_url_rule('/edit/<path:path>',
                     view_func=edit,
                     methods=['GET', 'POST'])
    return app


def register_download() -> Flask:
    app.add_url_rule("/filelist/",
                     view_func=lambda: filelist(''),
                     methods=['GET'])
    app.add_url_rule("/filelist/<path:filepath>",
                     view_func=filelist,
                     methods=['GET'])
    app.add_url_rule('/delete/<path:filepath>',
                     view_func=delete_file,
                     methods=['GET'])
    return app
