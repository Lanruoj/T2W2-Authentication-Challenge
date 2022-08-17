from main import db
from flask import Blueprint, jsonify, request, abort
from models.users import User
from schemas.movie_schema import movie_schema, movies_schema
from models.movies import Movie
from flask_jwt_extended import jwt_required, get_jwt_identity


movies = Blueprint("movies", __name__, url_prefix="/movies")


@movies.route("/", methods=["GET"])
def get_movies():
    movies_list = Movie.query.all()
    result = movies_schema.dump(movies_list)
    return jsonify(result)


@movies.route("/", methods=["POST"])
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


@movies.route("/<int:id>", methods=["DELETE"])
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