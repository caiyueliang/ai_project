from app import db
from app.models import User


def test_register_and_login(client):
    rv = client.post("/auth/register", data={
        "username": "alice",
        "email": "alice@example.com",
        "password": "password123",
        "confirm_password": "password123",
    }, follow_redirects=True)
    assert b"\xe6\xb3\xa8\xe5\x86\x8c\xe6\x88\x90\xe5\x8a\x9f" in rv.data  # 注册成功

    rv = client.post("/auth/login", data={
        "username": "alice",
        "password": "password123",
    }, follow_redirects=True)
    assert b"\xe7\x99\xbb\xe5\xbd\x95\xe6\x88\x90\xe5\x8a\x9f" in rv.data  # 登录成功
