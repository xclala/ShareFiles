try:
    from flask import Blueprint, render_template, abort, send_file, request
    from os import path, scandir

    app = Blueprint('download', __name__)

    @app.route('/', methods=['GET'])
    def file_list():
        filelist = []
        if request.method == 'GET':
            for fl in scandir("共享的文件"):
                if fl.is_file():
                    filelist.append(fl.name)
            return render_template("filelist.html", filelist=filelist)


    @app.route('/<filename>', methods=['GET'])
    def download_file(filename):
        if request.method == 'GET':
            filepath = path.join("共享的文件/", filename)
            if path.exists(filepath):
                if path.isfile(filepath):
                    return send_file(filepath)
            abort(404)
except Exception as e:
    print(e)