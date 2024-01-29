from flask_admin import Admin
from flask_login import LoginManager, UserMixin
from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy
from flask_admin.contrib.sqla import ModelView
from flask import Flask, render_template, url_for, redirect, request
from flask_bcrypt import Bcrypt
import os
import os.path as op

UPLOAD_FOLDER = 'static'
admin = Admin()
app = Flask(__name__, static_folder='static')
app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
login_manager = LoginManager(app)
bcrypt = Bcrypt(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:\\Users\\737215\\DB Browser for SQLite\\site.db'
# C:\Users\726678\DB Browser for SQLite

app.config['SECRET_KEY'] = 'this is a secret key'
app.config['SQLALCHEMY_ECHO'] = True
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = SQLAlchemy(app)
admin.init_app(app)
file_path = op.join(op.dirname(__file__), 'static')
try:
    os.mkdir(file_path)
except OSError:
    pass


class User(db.Model, UserMixin):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

    def __str__(self):
        return self.username


class Consumer(db.Model, UserMixin):
    __tablename__ = "consumer"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(80), nullable=False)

    def __str__(self):
        return self.username


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Menu(db.Model):
    __tablename__ = "menu"
    menu_id = db.Column(db.Integer, primary_key=True)
    menu_name = db.Column(db.String(20), unique=True, nullable=False)
    menu_price = db.Column(db.Numeric(10, 2), nullable=False)
    menu_type = db.Column(db.Unicode(128))
    image = db.Column(db.String(30), nullable=False)
    basketitems = relationship("BasketItem", back_populates="menu")

    def __unicode__(self):
        return f'<Menu {self.menu_name}>'


@login_manager.user_loader
def load_user(menu_id):
    return Menu.query.get(int(menu_id))


class BasketItem(db.Model):
    __tablename__ = "basket"
    basket_id = db.Column(db.Integer, primary_key=True)
    basket_name = db.Column(db.String(20), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    menu_id = db.Column(db.Integer, db.ForeignKey('menu.menu_id'), nullable=False)
    menu = relationship("Menu", back_populates="basketitems")

    def __unicode__(self):
        return f'<BasketItem {self.basket_name}'


class MenuView(ModelView):
    can_delete = False
    form_columns = ['menu_name', 'menu_price', 'menu_type']
    column_list = ['menu_name', 'menu_price', 'menu_type']


admin.add_view(ModelView(User, db.session))
admin.add_view(MenuView(Menu, db.session))

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_customer = Consumer(username=username, email=email, password=hashed_password)
        db.session.add(new_customer)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')
@app.route('/login', methods=['GET','POST'])
def login():
    return render_template('login.html')

@app.route('/addfood', methods=['GET', 'POST'])
def addfood():
    if request.method == 'POST':
        menu_name = request.form['menu_name']
        menu_price = request.form['menu_price']
        menu_type = request.form['menu_type']
        if 'file1' not in request.files:
            return 'there is no file1 in form!'
        file1 = request.files['file1']
        path = os.path.join(app.config['UPLOAD_FOLDER'], file1.filename)
        file1.save(path)
        new_food = Menu(menu_name=menu_name, menu_price=menu_price, menu_type=menu_type, image=path)
        db.session.add(new_food)
        db.session.commit()
    return render_template('createfood.html')

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
