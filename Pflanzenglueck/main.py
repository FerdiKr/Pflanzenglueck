from flask import Blueprint, jsonify, render_template, request, redirect, url_for, current_app, send_from_directory
from flask_login import login_required, current_user
from markupsafe import escape
from werkzeug.utils import secure_filename
import datetime
import json
from .models import User

main = Blueprint('main', __name__)

@main.before_request
def setup():
    global storage
    storage = current_app.config['STORAGE_HANDLER']

@main.route('/save_rule', methods=['POST'])
@login_required
def save_rule():
    rule_id = request.form.get('rule-id')  # Holen der Regel-ID aus dem Formular
    rule_name = request.form.get('rule-name')
    first_watering = request.form.get('first-watering')
    repeat_radio = request.form.get('repeat-radio')
    repeat = request.form.get('repeat')
    repeat_unit = request.form.get('repeat-unit')
    pin = request.form.get('pin')
    duration = request.form.get('duration')
    action_description = request.form.get('action-description')

    # Prüfe auf Vollständigkeit und Richtigkeit der Daten
    if not all([rule_name, first_watering, repeat_radio, pin, duration, action_description]):
        return jsonify({'error': 'Nicht alle Felder wurden ausgefüllt.'}), 400

    # Prüfe Gültigkeit des Datums
    try:
        datetime.datetime.strptime(first_watering, '%Y-%m-%dT%H:%M')
    except ValueError:
        return jsonify({'error': 'Ungültiges Datum- oder Uhrzeitformat.'}), 400

    # Prüfe Gültigkeit der ausgewählten Werte
    valid_repeat_radio_values = ['no-repeat', 'repeat']
    valid_repeat_unit_values = ['days', 'hours']
    valid_action_description_values = ['high-for-duration', 'low-for-duration']

    if repeat_radio not in valid_repeat_radio_values:
        return jsonify({'error': 'Ungültiger Wert für Gießen Wiederholen.'}), 400

    if repeat_unit not in valid_repeat_unit_values:
        return jsonify({'error': 'Ungültige Einheit für Wiederholung.'}), 400

    if action_description not in valid_action_description_values:
        return jsonify({'error': 'Ungültige Aktion zum Gießen.'}), 400

    try:
        repeat = int(repeat)
        pin = int(pin)
        duration = int(duration)

        if repeat <= 0:
            return jsonify({'error': 'Wiederholung muss größer als 0 sein.'}), 400

        if duration <= 0:
            return jsonify({'error': 'Dauer muss größer als 0 sein.'}), 400

        if pin < 0:
            return jsonify({'error': 'Pin muss größer oder gleich 0 sein.'}), 400

    except ValueError:
        return jsonify({'error': 'Ungültige Zahlenwerte wurden eingegeben.'}), 400

    # Lade die vorhandenen Regeln aus der JSON-Datei
    rules_file_path = storage.path_join(current_user.name, 'rules.json')
    rules = json.loads(storage.read_file(rules_file_path))

    if rule_id:  # Falls eine Regel-ID vorhanden ist...
        for rule in rules:
            if rule['id'] == rule_id:  # ...finde die Regel mit dieser ID...
                # ...und aktualisiere die Regel.
                rule['name'] = rule_name
                rule['first_watering'] = first_watering
                rule['repeat'] = repeat_radio == 'repeat'
                rule['repeat_interval'] = {
                    'value': repeat,
                    'unit': repeat_unit
                }
                rule['action'] = {
                    'pin': pin,
                    'duration': duration,
                    'description': action_description
                }
                message = 'Regel erfolgreich aktualisiert.'  # Passen Sie die Erfolgsmeldung an
                break
        else:
            return jsonify({'error': 'Keine Regel mit dieser ID gefunden.'}), 404
    else:  # Falls keine Regel-ID vorhanden ist...

        # Ermittle die höchste vorhandene ID
        try:
            max_id = max([int(rule['id']) for rule in rules])
        except ValueError:
            max_id = 0

        # Generiere eine eindeutige ID für die neue Regel
        new_id = str(max_id + 1)

        # Speichere die Daten in der JSON-Datei
        rule_data = {
            'id': new_id,
            'name': rule_name,
            'first_watering': first_watering,
            'repeat': repeat_radio == 'repeat',
            'repeat_interval': {
                'value': repeat,
                'unit': repeat_unit
            },
            'action': {
                'pin': pin,
                'duration': duration,
                'description': action_description
            }
        }
        rules.append(rule_data)
        message = 'Regel erfolgreich erstellt.'

    # Jetzt prüfen wir auf Konflikte, nachdem die Regel aktualisiert bzw. erstellt wurde
    conflicting_rule = next((rule for rule in rules if rule['action']['pin'] == pin and rule['action']['description'] != action_description), None)
    if conflicting_rule:
        return jsonify({'error': f'Für Pin {pin} existiert bereits eine Regel ("{conflicting_rule["name"]}") mit einer Aktion ("{conflicting_rule["action"]["description"]}"), die mit dieser im Widerspruch steht.'}), 400

    storage.write_file(rules_file_path, json.dumps(rules))

    return jsonify({'message': message})

@main.route('/get_rules', methods=['GET'])
@login_required
def get_rules():
    rules_file_path = storage.path_join(current_user.name, 'rules.json')
    rules = json.loads(storage.read_file(rules_file_path))

    formatted_rules = []
    for rule in rules:
        formatted_rule = {
            'id': rule['id'],
            'name': rule['name'],
            'first_watering': rule['first_watering'],
            'repeat': rule['repeat'],
            'repeat_interval': rule['repeat_interval'],
            'action': rule['action']
        }
        formatted_rules.append(formatted_rule)

    return jsonify(formatted_rules)

@main.route('/delete_rule/<int:rule_id>', methods=['DELETE'])
@login_required
def delete_rule(rule_id):
    # Pfad zur JSON-Datei mit den Regeln des Benutzers.
    rules_file_path = storage.path_join(current_user.name, 'rules.json')

    # Laden der Regeln aus der Datei.
    rules = json.loads(storage.read_file(rules_file_path))

    # Finden der Regel, die gelöscht werden soll.
    rule_to_delete = None
    for rule in rules:
        if int(rule['id']) == rule_id:
            rule_to_delete = rule
            break

    # Fehlermeldung senden, wenn die Regel nicht gefunden wurde.
    if rule_to_delete is None:
        return jsonify({'error' : 'Regel nicht gefunden'}), 404

    # Entfernen der Regel aus der Liste.
    rules.remove(rule_to_delete)

    # Speichern der aktualisierten Regelliste.
    storage.write_file(rules_file_path, json.dumps(rules))

    return jsonify({'message' : 'Regel wurde erfolgreich gelöscht'}), 200

@main.route("/")
def index():
    return render_template("index.html")

@main.route('/home')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('main.rules'))
    else:
        return redirect(url_for('main.index'))

@main.route('/rules')
@login_required
def rules():
    return render_template('rules.html')

@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

@main.route('/.well-known/acme-challenge/<path:filename>')
def send_certbotfile(filename):
    return send_from_directory('.well-known/acme-challenge', secure_filename(escape(filename)))

@main.route("/test")
@login_required
def test():
    return render_template("test.html")
