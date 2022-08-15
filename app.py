from datetime import timedelta

from json import dump
from venv import create
from flask import Flask, jsonify, request, abort
app = Flask(__name__)

from flask_marshmallow import Marshmallow
from marshmallow.validate import Length
ma = Marshmallow(app)

from flask_bcrypt import Bcrypt
bcrypt = Bcrypt(app)

from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
jwt = JWTManager(app)


## DB CONNECTION AREA

from flask_sqlalchemy import SQLAlchemy 
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql+psycopg2://tomato:123456@localhost:5432/ripe_tomatoes_db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = "JWT Secret Key"

db = SQLAlchemy(app)

# CLI COMMANDS AREA

@app.cli.command("create")
def create_db():
    db.create_all()
    print("Tables created")

@app.cli.command("seed")
def seed_db():

    movie1 = Movie(
        title = "Spider-Man: No Way Home",
        genre = "Action",
        length = 148,
        year = 2021
    )
    db.session.add(movie1)

    movie2 = Movie(
        title = "Dune",
        genre = "Sci-fi",
        length = 155,
        year = 2021
    )
    db.session.add(movie2)

    actor1 = Actor(
        first_name = "Tom",
        last_name = "Holland",
        gender = "male",
        country = "UK"
    )
    db.session.add(actor1)

    actor2 = Actor(
        first_name = "Marisa",
        last_name = "Tomei",
        gender = "female",
        country = "USA"
    )
    db.session.add(actor2)

    actor3 = Actor(
        first_name = "Timothee",
        last_name = "Chalemet",
        gender = "male",
        country = "USA"
    )
    db.session.add(actor3)

    actor4 = Actor(
        first_name = "Zendaya",
        last_name = "",
        gender = "female",
        country = "USA"
    )
    db.session.add(actor4)

    admin = User(
            username = "admin",
            password = bcrypt.generate_password_hash("12345678").decode("utf-8"),
            admin = True
    )
    db.session.add(admin)

    db.session.commit()
    print("Tables seeded") 

@app.cli.command("drop")
def drop_db():
    db.drop_all()
    print("Tables dropped") 

# MODELS AREA

class Movie(db.Model):
    __tablename__ = "MOVIES"
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String())
    genre = db.Column(db.String())
    length = db.Column(db.Integer())
    year = db.Column(db.Integer())

class Actor(db.Model):
    __tablename__ = "ACTORS"
    id = db.Column(db.Integer,primary_key=True)  
    first_name = db.Column(db.String())
    last_name = db.Column(db.String())
    gender = db.Column(db.String())
    country = db.Column(db.String())

class User(db.Model):
    __tablename__ = "USERS"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(), unique=True, nullable=False)
    password = db.Column(db.String(), nullable=False)
    admin = db.Column(db.Boolean(), default=False)

# SCHEMAS AREA

class MovieSchema(ma.Schema):
    class Meta:
        fields = ("id", "title", "genre", "length", "year")
movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)

class ActorSchema(ma.Schema):
    class Meta:
        fields = ("id", "first_name", "last_name", "gender", "country")
actor_schema = ActorSchema()
actors_schema = ActorSchema(many=True)


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
    password = ma.String(validate=Length(min=8))
user_schema = UserSchema()
users_schema = UserSchema(many=True)


# ROUTING AREA

@app.route("/")
def hello():
    return "Welcome to Ripe Tomatoes API"

@app.route("/movies", methods=["GET"])
def get_movies():
    movies_list = Movie.query.all()
    result = movies_schema.dump(movies_list)
    return jsonify(result)

@app.route("/actors", methods=["GET"])
def get_actors():
    actors_list = Actor.query.all()
    result = actors_schema.dump(actors_list)
    return jsonify(result)

@app.route('/auth/register', methods=["POST"])
def auth_register():
    user_fields = user_schema.load(request.json)
    user = User.query.filter_by(username=user_fields["username"]).first()
    if user:
        return abort(401, description="Username already exists")
    else:
        user = User()
        user.username = user_fields["username"]
        user.password = bcrypt.generate_password_hash(user_fields["password"]).decode("utf-8")
        user.admin = False

        db.session.add(user)
        db.session.commit()

        expiry = timedelta(days=1)
        access_token = create_access_token(identity=str(user.id), expires_delta=expiry)

        return jsonify({"user": user.username, "token": access_token})
        

@app.route('/auth/login', methods=["POST"])
def auth_login():
    user_fields = user_schema.load(request.json)
    user = User.query.filter_by(username=user_fields["username"]).first()
    if not user or not bcrypt.check_password_hash(user.password, user_fields["password"]):
        return abort(401, description="Invalid login")
    
    expiry = timedelta(days=1)
    access_token = create_access_token(identity=str(user.id),expires_delta=expiry)

    return jsonify({"user": user.username, "token": access_token})


# MOVIES TABLE
@app.route('/movies/add', methods=["POST"])
@jwt_required()
def add_movie():      
    movie_fields = movie_schema.load(request.json)
    movie = Movie()
    movie.title = movie_fields["title"]
    movie.year = movie_fields["year"]
    movie.genre = movie_fields["genre"]
    movie.length = movie_fields["length"]

    db.session.add(movie)
    db.session.commit()

    return jsonify(movie_schema.dump(movie))


@app.route('/movies/<int:id>', methods=["DELETE"])
@jwt_required()
def delete_movie(id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return abort(401, description="Invalid user")
    
    movie = Movie.query.filter_by(id=id).first()
    if not movie:
        return abort(400, description="Movie not in database")
    
    db.session.delete(movie)
    db.session.commit()

    return jsonify(movie_schema.dump(movie))


# ACTORS TABLE
@app.route('/actors/add', methods=["POST"])
@jwt_required()
def add_actor():
    actor_fields = actor_schema.load(request.json)
    actor = Actor()
    actor.first_name = actor_fields["first_name"]
    actor.last_name = actor_fields["last_name"]
    actor.gender = actor_fields["gender"]
    actor.country = actor_fields["country"]

    db.session.add(actor)
    db.session.commit()

    return jsonify(actor_schema.dump(actor))


@app.route('/actors/<int:id>', methods=["DELETE"])
@jwt_required()
def delete_actor(id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return abort(401, description="Invalid user")
    
    actor = Actor.query.filter_by(id=id).first()
    if not actor:
        return abort(400, description="Actor not in database")
    
    db.session.delete(actor)
    db.session.commit()

    return jsonify(actor_schema.dump(actor))

