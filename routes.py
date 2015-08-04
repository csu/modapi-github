import arrow
from flask import Blueprint, request, jsonify
import requests

from common import require_secret
from config import config
import secrets

module = Blueprint(config['module_name'], __name__)

STREAK_EVENTS = ['CreateEvent', 'PushEvent']

@module.route('/')
@require_secret
def get_events():
    return jsonify({'response': requests.get('https://api.github.com/users/csu/events').json()})

@module.route('/streak')
@module.route('/streak/')
@require_secret
def check_streak():
    today = arrow.now().floor('day')
    events = requests.get('https://api.github.com/users/csu/events').json()

    occurred_today = []
    is_complete = False
    for event in events:
        if arrow.get(event["created_at"]) > today:
            is_complete = is_complete or (event["type"] in STREAK_EVENTS)
    
    message = 'GitHub Streak: Done' if is_complete else 'GitHub Streak: Incomplete'

    if not is_complete or not request.args.get('onlyNotifyWhenIncomplete'):
        notifier.send(message, title=message, source='modapi')

    return jsonify({'status': 'ok', 'is_complete': is_complete})