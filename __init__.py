from flask import render_template, request, redirect, url_for, Blueprint, session, send_file, Response
from CTFd.utils.decorators import authed_only, admins_only
from CTFd.utils.user import get_current_team
from CTFd.utils.logging import log
from CTFd.utils.helpers import get_errors
from CTFd.utils import get_config
from CTFd.models import db
from .models import Writeups
import os 
import subprocess

def load(app):
    app.db.create_all()
    writeup = Blueprint('writeup', __name__, template_folder='templates')

    # Gets the writeup page
    @writeup.route('/writeup/<int:challenge_id>', methods=['GET', 'POST'])
    @authed_only
    def get_writeup(challenge_id):
        if request.method == "GET":
            return render_template('writeup.html', challenge_id=challenge_id)
        else:
            user_is_team = False
            if get_config("user_mode") == 'users': 
                user = session['name']
            else:
                user = get_current_team().id
                user_is_team = True
            data = request.get_json()
            writeup_text = data['writeup_text']
            writeup = Writeups(challenge_id=challenge_id, user_id=user, user_is_team=user_is_team, writeup=writeup_text)
            db.session.add(writeup)
            db.session.commit()
            db.session.close()
            return 'Writeup added   '

    # Gets the writeup overview page for admins
    @writeup.route('/admin/writeup/overview', methods=['GET'])
    @admins_only
    def admin_writeup_overview():
        writeups_per_page = 10
        # Get page if page parameter is set in the url
        page = 1
        if 'page' in request.args:
            page = int(request.args.get('page'))
        writeups = Writeups.query
        pages = writeups.count()/writeups_per_page
        writeups.paginate(page=page, per_page=writeups_per_page)
        return render_template('writeup_overview.html', page=page, pages=pages, writeups=writeups)

    # Gets the writeup overview page for admins
    @writeup.route('/admin/writeup/<int:writeup_id>', methods=['GET'])
    @admins_only
    def admin_writeup_text(writeup_id):
        # The admin can view the buildfile of all containers
        writeup = Writeups.query.filter_by(id=writeup_id).first_or_404()
        # <pre> tags are so that the newlines are interperated
        return "<pre>" + writeup.writeup + "</pre>"

    app.register_blueprint(writeup)
