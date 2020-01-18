import os
from werkzeug.utils import secure_filename

ATTACHMENTS = "static/attachments"


def save_attachments(file):
    if file.filename == '':
        attachments = None
    else:
        attachments = secure_filename(file.filename)
        file.save(os.path.join(ATTACHMENTS, attachments))
    return attachments


def append_attachment(question):
    if question["attachments"]:
        question["attachments"] = os.path.join(ATTACHMENTS, question["attachments"])