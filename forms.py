from wtforms import Form, StringField, TextAreaField, PasswordField, validators, SubmitField, ValidationError, FileField
from flask_wtf.file import FileField, FileAllowed, FileRequired

class RegisterForm(Form):
    name = StringField('Name', [
        validators.Length(min = 1, max = 100, message='Length of name should be between 1 and 100'),
    ])
    username = StringField('Username', [
        validators.Length(min = 5, max = 30, message='Length of username should be between 5 and 30'),
    ])
    email = StringField('Email', [
        validators.Length(min = 10, max = 100, message='Length of email should be between 10 and 100'),
    ])
    password = PasswordField('Password', [
        validators.Length(min = 8, max = 100, message='Length of password should be between 8 and 100'),
        validators.EqualTo('confirm', 'Password do not match')
    ])
    confirm = PasswordField('Confirm Password')


class LoginForm(Form):
    email = StringField('Email', [
        validators.Length(min = 10, max = 100, message='Length of email should be between 10 and 100'),
    ])
    password = PasswordField('Password', [
        validators.Length(min = 8, max = 100, message='Length of password should be between 8 and 100')
    ])


class SearchForm(Form):
    search = StringField('Search')
    submit = SubmitField('Search')


class ArticleForm(Form):
    title = StringField('Title', validators=[validators.DataRequired()])
    description = TextAreaField('Description', validators=[validators.DataRequired()])


class BlogForm(Form):
    title = StringField('Title', validators=[validators.DataRequired()])
    description = TextAreaField('Description', validators=[validators.DataRequired()])
    submit = SubmitField('Add')

class CommentForm(Form):
    data = StringField('Data', validators=[validators.DataRequired()])
    submit = SubmitField('Add Comment')