from flask import Blueprint, jsonify, request, abort
from main import db
from models.users import User
from schemas.actor_schema import actor_schema, actors_schema
from models.actors import Actor
from flask_jwt_extended import jwt_required, get_jwt_identity


actors = Blueprint("actors", __name__, url_prefix="/actors")


@actors.route("/", methods=["GET"])
def get_actors():
    actors_list = Actor.query.all()
    result = actors_schema.dump(actors_list)
    return jsonify(result)


@actors.route("/", methods=["POST"])
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


@actors.route('/<int:id>', methods=["DELETE"])
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