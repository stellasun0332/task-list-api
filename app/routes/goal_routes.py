from flask import Blueprint, request, Response
from ..routes.utilities import create_model
from ..models.goal import Goal
from ..db import db
from ..routes.utilities import validate_model
from ..models.task import Task

bp = Blueprint("goals_bp", __name__, url_prefix="/goals")


@bp.post("")
def creaet_a_goal():
    request_body = request.get_json()
    if request_body == {}:
        response = {"details": "Invalid data"}
        return response, 400

    return {"goal": create_model(Goal, request_body)}, 201


@bp.get("")
def get_all_goals():
    query = db.select(Goal).order_by(Goal.id)
    goals = db.session.scalars(query)

    response = []

    for goal in goals:
        response.append(goal.to_dict())
    return response


@bp.get("/<goal_id>")
def get_a_goal(goal_id):
    goal = validate_model(Goal, goal_id)
    return {"goal": goal.to_dict()}


@bp.put("/<goal_id>")
def update_a_goal(goal_id):
    request_body = request.get_json()

    goal = validate_model(Goal, goal_id)
    goal.title = request_body["title"]

    db.session.commit()

    return Response(status=204, mimetype="application/json")


@bp.delete("/<goal_id>")
def delete_a_goal(goal_id):
    goal = validate_model(Goal, goal_id)
    db.session.delete(goal)
    db.session.commit()

    return Response(status=204, mimetype="application/json")


@bp.post("/<goal_id>/tasks")
def creat_tasks_for_a_goal(goal_id):
    goal = validate_model(Goal, goal_id)
    request_body = request.get_json()

    task_ids = request_body.get("task_ids", [])
    tasks = []
    # to remove the goal_id if current task has any
    for task in goal.tasks:
        task.goal_id = None

    for task_id in task_ids:
        task = validate_model(Task, task_id)
        # to updated the goal id for tasks
        task.goal_id = goal.id
        tasks.append(task)

    db.session.commit()

    response = {"id": goal.id, "task_ids": [task.id for task in tasks]}
    return response, 200


@bp.get("/<goal_id>/tasks")
def get_tasks_for_a_given_goal_id(goal_id):
    goal = validate_model(Goal, goal_id)
    tasks_response = []
    for task in goal.tasks:
        task_data = task.to_dict()
        # task_data["goal_id"] = goal.id
        tasks_response.append(task_data)

    response = {"id": goal.id, "title": goal.title, "tasks": tasks_response}
    return response, 200
