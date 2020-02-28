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
    path = os.path.abspath(__file__)
    path = os.path.dirname(path)
    path = os.path.join(path, "static", "attachments")
    print(path)
    return os.path.join(path, name)


def delete_attachment(name):
    os.remove(get_system_path(name))
