#!/usr/bin/python3

from flask import current_app


def allowed_file(filename):
    """
    Checks if the given filename is allowed based on its extension.

    Parameters:
        filename (str): The name of the file to check.

    Returns:
        bool: True if the file is allowed, False otherwise.
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']
