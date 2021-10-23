from flask import Blueprint, render_template, abort, send_file, request
from os import path, walk

app = Blueprint('download', __name__)


@app.route('/', methods=['GET'])
def file_list():
    if request.method == 'GET':
        for ___, _________, fl in walk("让别人下载的文件"):
            if fl != []:
                return render_template("filelist.html", filelist=fl)
            else:
                return render_template("filelist.html", filelist="")


@app.route('/<filename>', methods=['GET'])
def download_file(filename):
    if request.method == 'GET':
        from io import BytesIO
        from mimetypes import guess_type
        filepath = path.join("让别人下载的文件/", filename)
        if path.exists(filepath):
            if path.isfile(filepath):
                return send_file(filepath)
            else:
                abort(404)
        else:
            abort(404)
