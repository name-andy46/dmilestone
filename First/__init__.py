import os
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
from flask_mail import Mail

csrf = CSRFProtect()

app = Flask(__name__)
csrf.init_app(app)



app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dharamshi.db'
app.config['SECRET_KEY'] = 'a67101b61d10691bf125f766b0249ea5'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'website.info1.9047@gmail.com'
app.config['MAIL_PASSWORD'] = 'N0wyv#266iD!GwV%'
mail = Mail(app)



from First import routes