from main import db
from flask import Blueprint
from main import bcrypt
from models.users import User
from models.movies import Movie
from models.actors import Actor
from datetime import date


db_commands = Blueprint('db', __name__)


@db_commands.cli.command("create")
def create_db():
    db.create_all()
    print("Tables created")


@db_commands.cli.command("seed")
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


@db_commands.cli.command("drop")
def drop_db():
    db.drop_all()
    print("Tables dropped") 