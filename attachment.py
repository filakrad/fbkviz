import os
from werkzeug.utils import secure_filename

ATTACHMENTS = "/static/attachments/"


def save_attachments(file):
    if file.filename == '':
        name = None
    else:
        name = secure_filename(file.filename)
        file.save(get_system_path(name))
    return name


def append_attachment(question):
    if question["attachments"]:
        question["attachments"] = get_url_path(question["attachments"])


def get_url_path(name):
    return ATTACHMENTS + name


def get_system_path(name):
    path = os.path.join(os.path.curdir, "static", "attachments")
    path = os.path.abspath(path)
    print(path)
    return os.path.join(path, name)


def delete_attachment(name):
    os.remove(get_system_path(name))
