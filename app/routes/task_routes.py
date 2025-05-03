from flask import Blueprint, abort, make_response, Blueprint, request, Response
from ..db import db
from .utilities import validate_model, validate_task_data
from ..models.task import Task
from sqlalchemy import desc
from datetime import datetime
import os, requests

SLACK_API_TOKEN = os.environ.get("SLACK_API_TOKEN")

tasks_bp = Blueprint("tasks_bp", __name__, url_prefix="/tasks")


@tasks_bp.post("")
def create_a_task():
    request_body = request.get_json()
    validate_task_data(request_body)
    new_task = Task.from_dict(request_body)

    db.session.add(new_task)
    db.session.commit()

    return {"task": new_task.to_dict()}, 201


@tasks_bp.get("")
def get_all_tasks():
    query = db.select(Task)
    sort_param = request.args.get("sort")
    if sort_param == "asc":
        query = query.order_by(Task.title)
    elif sort_param == "desc":
        query = query.order_by(desc(Task.title))

    tasks = db.session.scalars(query)

    return [task.to_dict() for task in tasks]


@tasks_bp.get("/<task_id>")
def get_a_task(task_id):
    task = validate_model(Task, task_id)

    return {"task": task.to_dict()}, 200


@tasks_bp.put("/<task_id>")
def update_a_task(task_id):
    request_body = request.get_json()
    task = validate_model(Task, task_id)
    task.update_from_dict(request_body)

    db.session.commit()

    return Response(status=204, mimetype="application/json")


@tasks_bp.delete("/<task_id>")
def delete_a_task(task_id):
    task = validate_model(Task, task_id)
    db.session.delete(task)
    db.session.commit()
    return Response(status=204, mimetype="application/json")


@tasks_bp.patch("/<task_id>/mark_complete")
def update_complete_task_field(task_id):
    task = validate_model(Task, task_id)
    task.completed_at = datetime.utcnow()
    db.session.commit()

    slack_message = {
        "channel": "task-notifications",
        "text": f"Someone just completed the task {task.title}",
    }
    headers = {
        "Authorization": f"Bearer {SLACK_API_TOKEN}",
        "Content-Type": "application/json",
    }
    requests.post(
        "https://slack.com/api/chat.postMessage", json=slack_message, headers=headers
    )
    return Response(status=204, mimetype="application/json")


@tasks_bp.patch("/<task_id>/mark_incomplete")
def update_incomplete_task_field(task_id):
    task = validate_model(Task, task_id)
    task.completed_at = None
    db.session.commit()
    return Response(status=204, mimetype="application/json")
