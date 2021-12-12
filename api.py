
import json
import os.path

from flask import Blueprint
from UseSqlite import RiskQuery

api_bp = Blueprint('api', __name__)


@api_bp.route('/api', methods=['POST', 'GET'])
def api_json():
    rq = RiskQuery('./static/RiskDB.db')
    rq.instructions("SELECT * FROM photo ORDER By time desc")
    rq.do()
    lst = []
    page = ''
    i = 1
    for r in rq.format_results().split('\n\n'):
        photo = r.split(',')
        picture_time = photo[0]
        picture_description = photo[1]
        picture_path = photo[2].strip()
        photo_size = str(format((os.path.getsize(picture_path) / 1024), '.2f')) + 'KB'
        lst = [{'ID': i, 'upload_date': picture_time, 'description': picture_description, 'photo_size': photo_size}]
        lst2 = json.dumps(lst[0], sort_keys=True, indent=4, separators=(',', ':'))
        page += '%s' % lst2
        i += 1
    return page






