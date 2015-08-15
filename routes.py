import arrow
from flask import Blueprint, request, jsonify
import requests

from common import require_secret, dashboard_item
from config import config
import secrets

module = Blueprint(config['module_name'], __name__)

STREAK_EVENTS = ['CreateEvent', 'PushEvent']

@module.route('/')
@require_secret
def get_events():
    return jsonify({'response': requests.get('https://api.github.com/users/csu/events').json()})

def streak_complete():
    today = arrow.now().floor('day')
    events = requests.get('https://api.github.com/users/csu/events').json()

    occurred_today = []
    is_complete = False
    for event in events:
        if arrow.get(event["created_at"]) > today:
            is_complete = is_complete or (event["type"] in STREAK_EVENTS)

    return is_complete


@module.route('/streak')
@module.route('/streak/')
@require_secret
def check_streak():
    is_complete = streak_complete()
    
    if ((request.args.get('notify') != 'false') and
            ((not is_complete) or
                (not request.args.get('onlyNotifyWhenIncomplete')))):
        message = 'GitHub Streak: Done' if is_complete else 'GitHub Streak: Incomplete'
        notifier.send(message, title=message, source='modapi')

    return jsonify({
        'status': 'ok',
        'is_complete': is_complete
    })

@module.route('/streak/dashboard')
@module.route('/streak/dashboard/')
@require_secret
def check_streak_dashboard():
    is_complete = streak_complete()
    item = {
        'title': 'GitHub Commit',
        'body': 'Complete' if is_complete else 'Incomplete',
        'color': '#CAE2B0' if is_complete else '#FFCC80'
    }
    return dashboard_item(item)