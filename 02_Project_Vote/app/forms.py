from __future__ import annotations
from datetime import datetime
from typing import List
from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    BooleanField,
    SubmitField,
    TextAreaField,
    DateTimeLocalField,
    SelectMultipleField,
)
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from .models import User, Poll


class RegisterForm(FlaskForm):
    username = StringField("用户名", validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField("邮箱", validators=[DataRequired(), Email()])
    password = PasswordField("密码", validators=[DataRequired(), Length(min=6, max=128)])
    confirm_password = PasswordField("确认密码", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("注册")

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError("用户名已存在")

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError("邮箱已注册")


class LoginForm(FlaskForm):
    username = StringField("用户名", validators=[DataRequired(), Length(min=3, max=80)])
    password = PasswordField("密码", validators=[DataRequired()])
    remember = BooleanField("记住我")
    submit = SubmitField("登录")


class PollForm(FlaskForm):
    title = StringField("标题", validators=[DataRequired(), Length(max=200)])
    description = TextAreaField("描述", validators=[Length(max=2000)])
    is_multiple = BooleanField("多选")
    start_time = DateTimeLocalField("开始时间", format="%Y-%m-%dT%H:%M", validators=[DataRequired()])
    end_time = DateTimeLocalField("结束时间", format="%Y-%m-%dT%H:%M", validators=[DataRequired()])
    options_text = TextAreaField("选项（每行一个）", validators=[DataRequired()])
    submit = SubmitField("保存")

    def validate(self, extra_validators=None):
        ok = super().validate(extra_validators)
        if not ok:
            return False
        if self.end_time.data <= self.start_time.data:
            self.end_time.errors.append("结束时间必须晚于开始时间")
            return False
        lines = [l.strip() for l in (self.options_text.data or "").splitlines() if l.strip()]
        if len(lines) < 2:
            self.options_text.errors.append("至少需要两个选项")
            return False
        return True
