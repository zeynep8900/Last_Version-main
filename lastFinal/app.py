from flask import Flask, flash, render_template, request, redirect, session, url_for
from flask_login import LoginManager, UserMixin, current_user, login_required, login_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import secrets

app = Flask(__name__)
app.config.from_object('config.DevelopmentConfig')  # Development için yapılandırma

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))

class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    city_name = db.Column(db.String(100))
    city_description = db.Column(db.Text)
    cultural_places = db.Column(db.Text)
    tourist_attractions = db.Column(db.Text)
    restaurants = db.Column(db.Text)
    bars = db.Column(db.Text)
    image_url = db.Column(db.String(255))

    def __init__(self, city_name, city_description, cultural_places, tourist_attractions, restaurants, bars, image_url):
        self.city_name = city_name
        self.city_description = city_description
        self.cultural_places = cultural_places
        self.tourist_attractions = tourist_attractions
        self.restaurants = restaurants
        self.bars = bars
        self.image_url = image_url

with app.app_context():
    db.create_all()

    existing_cities = City.query.all()
    for city in existing_cities:
        db.session.delete(city)

    cities_data = [
        ('Izmir', 'A beautiful city on the Aegean coast with a rich history.', 'Ephesus, Agora', 'Clock Tower, Konak Pier', 'Best Restaurant1, Best Restaurant 2', 'Bar 1, Bar 2', 'https://gezginyazar.com/wp-content/uploads/2023/05/izmir.jpg'),
        ('Antalya', 'A popular resort destination with stunning best beaches of the world.', 'Aspendos, Perge', 'Old Town, Düden Waterfalls', 'Seafood Paradise Mediterranean Delight', 'Beach Bar, Rooftop Lounge', 'https://images.pexels.com/photos/3732500/pexels-photo-3732500.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2'),
        ('Istanbul', 'The apple of the worlds eye, where Europe and Asia meet', 'Hagia Sophia, Yere Batan Sarnıcı, Topkapı Palace, Maidens Tower, Hagia Yorgi Monastery', 'Hagia Yorgi Monastery', 'Best Restaurant1, Best Restaurant 2', 'Bar 1, Bar 2', 'https://images.pexels.com/photos/1549326/pexels-photo-1549326.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2'),
        ('Mugla', 'A historical city where blue and green meet.', '', '', 'Best Restaurant1, Best Restaurant 2', 'Bar 1, Bar 2', 'https://images.pexels.com/photos/5892261/pexels-photo-5892261.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2'),
        ('Sinop', 'The northernmost tip of the country. Some say the North Pole can be seen from here.', '', '', 'Best Restaurant1, Best Restaurant 2', 'Bar 1, Bar 2', 'https://images.pexels.com/photos/8391276/pexels-photo-8391276.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2'),
        ('Ankara', 'The city where our founding fathers tomb is located.', '', '', 'Best Restaurant1, Best Restaurant 2', 'Bar 1, Bar 2', 'https://images.pexels.com/photos/7860240/pexels-photo-7860240.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2'),
        ('Canakkale', 'Here still carries the traces of the epic resistance today.', 'Çanakkale Abideleri', '', 'Best Restaurant1, Best Restaurant 2', 'Bar 1, Bar 2', 'https://media.istockphoto.com/id/479392144/tr/foto%C4%9Fraf/canakkale-martyrs-memorial-turkey.jpg?s=612x612&w=0&k=20&c=4Wr6HYnhA43_dSjTeAjImqTSn3vo95EaBtC9RcuvNhE=')

    ]

    for city_data in cities_data:
        city = City(*city_data)
        db.session.add(city)

    db.session.commit()

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    city_id = db.Column(db.Integer, db.ForeignKey('city.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('comments', lazy=True))
    city = db.relationship('City', backref=db.backref('comments', lazy=True))
    username = db.relationship('User', foreign_keys=[user_id], backref=db.backref('comments_username', lazy=True))

with app.app_context():
    db.create_all()

secret_key = secrets.token_hex(24)
app.secret_key = secret_key

@app.route('/', methods=['GET', 'POST'])
def index():
    images = ['pexels-muharrem-aydın-1836580.jpg', 'pexels-şinasi-müldür-2048865.jpg', 'pexels-çağın-kargi-8633909.jpg']

    if request.method == 'POST':
        search_term = request.form.get('destination_city')
        if search_term:
            cities = City.query.filter(City.city_name.ilike(f'%{search_term}%')).all()
        else:
            cities = City.query.all()
    else:
        cities = City.query.all()

    print("Number of cities:", len(cities))
    return render_template('index.html', cities=cities, images=images)

@app.route('/city_detail/<int:city_id>', methods=['GET', 'POST'])
def city_detail(city_id):
    city = City.query.get_or_404(city_id)
    comments = Comment.query.filter_by(city_id=city_id).all()

    if request.method == 'POST':
        if not current_user.is_authenticated:
            flash('You need to be logged in to post a comment.')
            return redirect(url_for('login'))

        comment_text = request.form.get('comment_text')
        if comment_text:
            new_comment = Comment(user_id=current_user.id, city_id=city_id, text=comment_text)
            db.session.add(new_comment)
            db.session.commit()
            # flash('Comment posted successfully.')

    return render_template('city_detail.html', city=city, comments=comments)

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('index'))

        flash('Invalid email or password. Please try again.')

    return render_template("login.html", logged_in=current_user.is_authenticated)

@app.route('/signup', methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            flash("Password and Confirm Password do not match.")
            return redirect(url_for('signup'))

        if len(password) < 8 or not any(char.isdigit() for char in password) or not any(char.isalnum() and not char.isalpha() for char in password):
            flash("Password must be at least 8 characters long, contain at least 1 number, and 1 non-alphanumeric character.")
            return redirect(url_for('signup'))

        hash_and_salted_password = generate_password_hash(
            password,
            method='pbkdf2:sha256',
            salt_length=8
        )

        new_user = User(
            email=email,
            password=hash_and_salted_password,
            name=request.form.get('name'),
        )

        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)
        return redirect(url_for("login"))

    return render_template("signup.html", logged_in=current_user.is_authenticated)

@app.route('/logout')
def logout():
    if current_user.is_authenticated:
        logout_user()
    else:
        flash("You are not logged in.")
    return redirect(url_for('index'))

@app.route('/about')
def about():
    return render_template("about_us.html")

@app.route('/contact')
def contact():
    return render_template("contact.html")

if __name__ == '__main__':
    app.run(debug=True, port=5001)
