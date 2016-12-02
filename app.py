# coding = utf-8
import os

from flask import Flask

from flask_mail import Mail, Message

from flask import request, session, render_template, flash, redirect, url_for

from celery import Celery

app = Flask(__name__)
mail = Mail(app)


def make_celery(app):
    celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery


app.config.update(
    CELERY_BROKER_URL='redis://localhost:6379',
    CELERY_RESULT_BACKEND='redis://localhost:6379',
    SECRET_KEY=os.environ.get('SCERET_KEY') or 'you can not guess it',
    MAIL_SERVER='smtp.googlemail.com',
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USERNAME=os.environ.get('MAIL_USERNAME'),
    MAIL_PASSWORD=os.environ.get('MAIL_PASSWORD'),
    MAIL_DEFAULT_SENDER='flask@example.com'
)

celery = make_celery(app)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == "GET":
        return render_template('index.html', email=session.get('email', ''))
    email = request.form['email']
    session['email'] = email

    msg = Message('Hello',
                  recipients=[request.form['email']])
    msg.body = "This is a test email"
    msg.html = "<b>testing</b>"

    if request.form['submit'] == 'send':
        send_email.delay(email)
        flash('Send email to {}'.format(email))
    else:
        send_email.apply_async(args=[msg], countdown=60)
        flash('Your email will be send one minute later'.format(email))

    return redirect(url_for('index'))


@celery.task
def send_email(msg):
    with app.app_context():
        mail.send(msg)


if __name__ == '__main__':
    app.run(debug=True)
