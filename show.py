from flask import Blueprint
from service import get_database_photos
show_bp = Blueprint('show', __name__)


@show_bp.route('/show')
def show():
    page = get_database_photos()
    return page