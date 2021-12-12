from flask import Blueprint, request

from service import get_description_photos

search_bp = Blueprint('search', __name__)


@search_bp.route('/search', methods=['POST', 'GET'])
def search():
    page = '''<form action="/search/query-string"method="post"enctype="multipart/form-data">
                <input name="description"><input type="submit"value="search"></form>'''
    return page


@search_bp.route('/search/query-string', methods=['POST', 'GET'])
def query_string():
    if request.method == 'POST':
        description = request.form['description']
        page = get_description_photos(description)

    return page
