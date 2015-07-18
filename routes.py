from flask import Blueprint, request, jsonify

from common import require_secret
from config import config
import secrets

module = Blueprint(config['module_name'], __name__)

@module.route('/')
@require_secret
def get_all_checkins():
    return jsonify(client.users.checkins())
    