from CTFd.models import db

class Writeups(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    challenge_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer)
    user_is_team = db.Column(db.Boolean)
    writeup = db.Column(db.Text)

    def __init__(self, challenge_id, user_id, user_is_team, writeup):
        self.challenge_id = challenge_id
        self.user_id = user_id
        self.user_is_team = user_is_team
        self.writeup = writeup

    def __repr__(self):
        return "<Writeup ID:{}>".format(self.id)
        