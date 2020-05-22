from First import db, login_manager, app
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from datetime import datetime
from flask_login import UserMixin, current_user



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    position = db.Column(db.String(80), nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    date_registered = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    registered_by = db.Column(db.String, nullable=False, default='super_user')
    posts = db.relationship('Banner', backref='author', lazy=True)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f'User("{self.username}", "{self.email}", "{self.position}", "{self.image_file}", "{self.date_registered}", "{self.registered_by}") '


class Banner(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # author = db.Column(db.String(20), nullable=False, default='super_user')
    picture_file = db.Column(db.String(50), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    description = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"BannerPost('{self.author}', '{self.date_posted}', {self.description})"