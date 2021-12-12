from flask import Blueprint



upload_bp = Blueprint('upload', __name__)



@upload_bp.route('/upload')
def upload():
    page = '''<form action="/"method="post"enctype="multipart/form-data">
            <input type="file"name="file"><input name="description"><input type="submit"value="Upload"></form>'''
    return page
