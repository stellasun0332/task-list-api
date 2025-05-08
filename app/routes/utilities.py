from flask import abort, make_response
from ..db import db


def validate_model(cls, model_id):
    try:
        model_id = int(model_id)
    except:
        response = {"message": f"{cls.__name__} {model_id} invalid"}
        abort(make_response(response, 400))
    query = db.select(cls).where(cls.id == model_id)
    model = db.session.scalar(query)

    if not model:
        response = {"message": f"{cls.__name__} {model_id} not found"}
        abort(make_response(response, 404))
    return model


def validate_task_data(data):
    if "title" not in data or "description" not in data:
        response = {"details": "Invalid data"}
        abort(make_response(response, 400))


def create_model(cls, data):
    try:
        new_model = cls.from_dict(data)
    except:
        response = {"message": f"missing {cls.__name__} information."}
        abort(make_response(response), 400)

    db.session.add(new_model)
    db.session.commit()
    return new_model.to_dict()
