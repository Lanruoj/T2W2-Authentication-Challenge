from controllers.auth_controller import auth
from controllers.actors_controller import actors
from controllers.movies_controller import movies


registerable_controllers = [
    auth,
    actors,
    movies
]