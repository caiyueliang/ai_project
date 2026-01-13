from __future__ import annotations
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from ..models import Poll

bp = Blueprint("main", __name__, template_folder="../templates")


@bp.route("/", methods=["GET"])
def index():
    polls = Poll.query.order_by(Poll.created_at.desc()).all()
    return render_template("index.html", polls=polls)
