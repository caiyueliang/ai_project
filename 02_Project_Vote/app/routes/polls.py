from __future__ import annotations
from datetime import datetime, timedelta
from typing import List
from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    request,
    abort,
    current_app,
    make_response,
)
from flask_login import login_required, current_user
from sqlalchemy import func
from ..forms import PollForm
from ..models import Poll, Option, VoteRecord
from .. import db

bp = Blueprint("polls", __name__, template_folder="../templates")


def admin_required():
    if not current_user.is_authenticated or not current_user.is_admin:
        abort(403)


@bp.route("/admin", methods=["GET"])
@login_required
def admin_index():
    admin_required()
    polls = Poll.query.order_by(Poll.created_at.desc()).all()
    return render_template("admin_polls.html", polls=polls)


@bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    admin_required()
    form = PollForm()
    if form.validate_on_submit():
        poll = Poll(
            title=form.title.data,
            description=form.description.data,
            is_multiple=form.is_multiple.data,
            start_time=form.start_time.data,
            end_time=form.end_time.data,
            created_by=current_user.id,
        )
        db.session.add(poll)
        lines = [l.strip() for l in form.options_text.data.splitlines() if l.strip()]
        for text in lines:
            db.session.add(Option(poll=poll, text=text))
        db.session.commit()
        flash("投票已创建", "success")
        return redirect(url_for("polls.admin_index"))
    return render_template("create_poll.html", form=form)


@bp.route("/<int:poll_id>/edit", methods=["GET", "POST"])
@login_required
def edit(poll_id: int):
    admin_required()
    poll = Poll.query.get_or_404(poll_id)
    form = PollForm(
        title=poll.title,
        description=poll.description,
        is_multiple=poll.is_multiple,
        start_time=poll.start_time,
        end_time=poll.end_time,
        options_text="\n".join([o.text for o in poll.options.order_by(Option.id.asc()).all()]),
    )
    if request.method == "POST" and form.validate_on_submit():
        poll.title = form.title.data
        poll.description = form.description.data
        poll.is_multiple = form.is_multiple.data
        poll.start_time = form.start_time.data
        poll.end_time = form.end_time.data
        poll.options.delete()
        lines = [l.strip() for l in form.options_text.data.splitlines() if l.strip()]
        for text in lines:
            db.session.add(Option(poll=poll, text=text))
        db.session.commit()
        flash("投票已更新", "success")
        return redirect(url_for("polls.admin_index"))
    return render_template("edit_poll.html", form=form, poll=poll)


@bp.route("/<int:poll_id>/delete", methods=["POST"])
@login_required
def delete(poll_id: int):
    admin_required()
    poll = Poll.query.get_or_404(poll_id)
    db.session.delete(poll)
    db.session.commit()
    flash("投票已删除", "info")
    return redirect(url_for("polls.admin_index"))


@bp.route("/<int:poll_id>", methods=["GET"])
@login_required
def detail(poll_id: int):
    poll = Poll.query.get_or_404(poll_id)
    options = poll.options.order_by(Option.id.asc()).all()
    return render_template("poll_detail.html", poll=poll, options=options)


@bp.route("/<int:poll_id>/vote", methods=["POST"])
@login_required
def vote(poll_id: int):
    poll = Poll.query.get_or_404(poll_id)
    if not poll.is_active():
        flash("投票未开始或已结束", "warning")
        return redirect(url_for("polls.detail", poll_id=poll_id))

    ip = request.headers.get("X-Forwarded-For", request.remote_addr)

    cooldown = current_app.config.get("VOTE_COOLDOWN_SECONDS", 30)
    recent_vote = (
        VoteRecord.query.filter_by(poll_id=poll_id, user_id=current_user.id)
        .order_by(VoteRecord.created_at.desc())
        .first()
    )
    if recent_vote and (datetime.utcnow() - recent_vote.created_at).total_seconds() < cooldown:
        flash("操作过于频繁，请稍后再试", "warning")
        return redirect(url_for("polls.detail", poll_id=poll_id))

    cookie_key = f"voted_{poll_id}"
    if request.cookies.get(cookie_key):
        flash("检测到您已参与过投票（Cookie）", "warning")

    selected_ids = request.form.getlist("options")
    try:
        selected_ids = [int(i) for i in selected_ids]
    except ValueError:
        selected_ids = []

    max_choices = current_app.config.get("MAX_CHOICES_PER_POLL", 10)
    if poll.is_multiple:
        if not selected_ids:
            flash("请至少选择一个选项", "warning")
            return redirect(url_for("polls.detail", poll_id=poll_id))
        if len(selected_ids) > max_choices:
            flash(f"最多可选择 {max_choices} 个选项", "warning")
            return redirect(url_for("polls.detail", poll_id=poll_id))
    else:
        if len(selected_ids) != 1:
            flash("此投票为单选", "warning")
            return redirect(url_for("polls.detail", poll_id=poll_id))

    valid_option_ids = [o.id for o in poll.options.all()]
    for oid in selected_ids:
        if oid not in valid_option_ids:
            abort(400)

    for oid in selected_ids:
        if (
            VoteRecord.query.filter_by(poll_id=poll_id, option_id=oid, user_id=current_user.id).first()
            is None
        ):
            db.session.add(
                VoteRecord(poll_id=poll_id, option_id=oid, user_id=current_user.id, ip_address=ip)
            )
    db.session.commit()

    resp = make_response(redirect(url_for("polls.results", poll_id=poll_id)))
    resp.set_cookie(cookie_key, "1", max_age=3600 * 24 * 365, httponly=True, samesite="Lax")
    flash("投票成功", "success")
    return resp


@bp.route("/<int:poll_id>/results", methods=["GET"])
@login_required
def results(poll_id: int):
    poll = Poll.query.get_or_404(poll_id)
    options = poll.options.order_by(Option.id.asc()).all()
    counts = (
        db.session.query(VoteRecord.option_id, func.count(VoteRecord.id))
        .filter(VoteRecord.poll_id == poll_id)
        .group_by(VoteRecord.option_id)
        .all()
    )
    count_map = {oid: c for oid, c in counts}
    labels = [o.text for o in options]
    data = [int(count_map.get(o.id, 0)) for o in options]
    total = sum(data)
    return render_template("poll_results.html", poll=poll, options=options, labels=labels, data=data, total=total)
