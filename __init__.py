from flask import render_template, request, redirect, url_for, Blueprint, session, send_file, Response
from CTFd.utils.decorators import authed_only, admins_only
from CTFd.utils.user import get_current_team
from CTFd.utils.logging import log
from CTFd.utils.helpers import get_errors
from CTFd.utils import get_config
from CTFd.models import db, Challenges, Users, Teams
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
            return 'Writeup added'

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
        writeups = writeups.paginate(page=page, per_page=writeups_per_page).items
        for w in writeups:
            w.challenge_name = Challenges.query.filter_by(id=w.challenge_id).first_or_404().name
            if w.user_is_team:
                w.user_name = Teams.query.filter_by(id=w.user_id).first_or_404().name
            else:
                w.user_name = Users.query.filter_by(id=w.user_id).first_or_404().name
        return render_template('writeup_overview.html', page=page, pages=pages, writeups=writeups)

    # Gets the writeup overview page for admins
    @writeup.route('/admin/writeup/<int:writeup_id>', methods=['GET'])
    @admins_only
    def admin_writeup_text(writeup_id):
        # Get the names
        writeup = Writeups.query.filter_by(id=writeup_id).first_or_404()
        challenge_name = Challenges.query.filter_by(id=writeup.challenge_id).first_or_404().name
        print(writeup.challenge_id, challenge_name)
        writeup_text = writeup.writeup
        user_name = "placeholder"
        if writeup.user_is_team:
            user_name = Teams.query.filter_by(id=writeup.user_id).first_or_404().name
        else:
            user_name = Users.query.filter_by(id=writeup.user_id).first_or_404().name
        return render_template('writeup_text.html', writeup_text=writeup_text, challenge_name=challenge_name, user_name=user_name, is_team=writeup.user_is_team)

    app.register_blueprint(writeup)
