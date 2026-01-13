from datetime import datetime, timedelta
from app import db
from app.models import User, Poll, Option, VoteRecord


def login(client, username, password):
    return client.post("/auth/login", data={"username": username, "password": password}, follow_redirects=True)


def create_admin_user(app):
    with app.app_context():
        u = User(username="admin", email="admin@example.com", is_admin=True)
        u.set_password("adminpass")
        db.session.add(u)
        db.session.commit()


def test_create_poll_and_vote(app, client):
    create_admin_user(app)
    rv = login(client, "admin", "adminpass")
    assert b"\xe7\x99\xbb\xe5\xbd\x95\xe6\x88\x90\xe5\x8a\x9f" in rv.data

    start = datetime.utcnow() - timedelta(minutes=5)
    end = datetime.utcnow() + timedelta(minutes=30)
    rv = client.post("/polls/create", data={
        "title": "测试投票",
        "description": "描述",
        "is_multiple": "y",
        "start_time": start.strftime("%Y-%m-%dT%H:%M"),
        "end_time": end.strftime("%Y-%m-%dT%H:%M"),
        "options_text": "A\nB\nC",
    }, follow_redirects=True)
    assert b"\xe6\x8a\x95\xe7\xa5\xa8\xe5\xb7\xb2\xe5\x88\x9b\xe5\xbb\xba" in rv.data

    with app.app_context():
        poll = Poll.query.filter_by(title="测试投票").first()
        assert poll is not None
        opts = poll.options.order_by(Option.id.asc()).all()
        assert len(opts) == 3
        oid = opts[0].id

    rv = client.post(f"/polls/{poll.id}/vote", data={"options": str(oid)}, follow_redirects=True)
    assert b"\xe6\x8a\x95\xe7\xa5\xa8\xe6\x88\x90\xe5\x8a\x9f" in rv.data

    with app.app_context():
        count = VoteRecord.query.filter_by(poll_id=poll.id).count()
        assert count == 1
