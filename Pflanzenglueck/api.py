# admin.py

from flask import Blueprint, render_template, url_for, request, jsonify,current_app
from flask_login import current_user, login_required
from werkzeug.security import check_password_hash
from markupsafe import escape
from werkzeug.utils import secure_filename
from .models import User
import json
from datetime import datetime,timedelta
import time

api = Blueprint('api', __name__)

@api.before_request
def setup():
    global storage
    storage = current_app.config['STORAGE_HANDLER']

def generate_actions(rule, now, array_size):
    start_time = datetime.strptime(rule["first_watering"], "%Y-%m-%dT%H:%M")
    end_time = start_time + timedelta(seconds=rule["action"]["duration"])
    action_type = 1 if rule['action']['description'] == 'high-for-duration' else 0
    actions = []
    
    while len(actions) < array_size*2:  # da jede Aktion zwei Einträge generiert (Anfang und Ende)
        if start_time > now:  # wenn Startzeit in der Zukunft
            actions.append((start_time, rule["action"]["pin"], action_type))
            actions.append((end_time, rule["action"]["pin"], 1 - action_type))
        elif start_time <= now and end_time > now:  # wenn Startzeit in der Vergangenheit, aber Endzeit in der Zukunft
            actions.append((now, rule["action"]["pin"], action_type))
            actions.append((end_time, rule["action"]["pin"], 1 - action_type))
        
        if not rule["repeat"]:
            break  # Wenn die Regel nicht wiederholt wird, brechen wir die Schleife nach der ersten Iteration ab
            
        unit = rule["repeat_interval"]["unit"]
        value = rule["repeat_interval"]["value"]
        if unit == "days":
            start_time += timedelta(days=value)
            end_time += timedelta(days=value)
        elif unit == "hours":
            start_time += timedelta(hours=value)
            end_time += timedelta(hours=value)

    return actions

@api.route('/api_precalc')
@login_required
def get_commands():
    array_size = 50
    try:
        array_size = int(request.args.get('array_size',100))
    except: 
        pass
    # Lade die vorhandenen Regeln aus der JSON-Datei
    rules_file_path = storage.path_join(current_user.name, 'rules.json')
    rules = json.loads(storage.read_file(rules_file_path))
    now = datetime.now() - timedelta(minutes=5)
    actions = []

    # Zu Beginn sollen alle Pins in ihren Anfangszustand versetzt werden
    available_pins = list(set([rule['action']['pin'] for rule in rules]))
    for pin in available_pins:
        is_high_for_duration = any(rule['action']['pin'] == pin and rule['action']['description'] == 'high-for-duration' for rule in rules)
        initial_state = 0 if is_high_for_duration else 1
        actions.append((now, pin, initial_state))

    for rule in rules:
        actions.extend(generate_actions(rule, now, array_size))
        
    # Sortieren der Aktionen nach der geplanten Zeit
    actions.sort(key=lambda x: x[0])

    # Begrenzen auf die ersten ((array_size)) Aktionen
    actions = actions[:array_size]

    # Konvertieren der Datums-/Zeitangaben in Unix-Timestamps und Aufteilen in separate Listen
    timestamps = [int(time.mktime(action[0].timetuple())) for action in actions]
    pins = [action[1] for action in actions]
    commands = [action[2] for action in actions]

    return jsonify({
        "timestamps": timestamps,
        "pins": pins,
        "commands": commands
    })