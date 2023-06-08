from flask import Blueprint, render_template, request, Response, current_app
from markupsafe import escape
from werkzeug.utils import secure_filename
import os

from .localization import Localization


base_path = os.path.dirname(os.path.abspath(__file__))
components_path = os.path.join(base_path,'templates','components')

components = Blueprint('components', __name__, template_folder=components_path)

@components.route('/components/<componentname>')
def get(componentname):
    componentname = secure_filename(escape(componentname))
    componentpath = os.path.join(components_path,componentname)
    component_locfile_path = os.path.join(componentpath,componentname+'_localization.json')
    localization = Localization(request.cookies.get('langcode',current_app.config['DEFAULT_LANGCODE']),fallback_order=['en_US','de_DE'],additional_loc_files=[component_locfile_path])
    return Response(render_template(componentname+'/'+componentname+'.html',loc=localization),mimetype='application/javascript')