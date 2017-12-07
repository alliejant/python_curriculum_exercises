from flask import Blueprint, url_for, redirect, render_template, request, flash, session, g
from project.models import Message, User
from project.forms import MessageForm, DeleteForm
from project import db
from project.decorators import ensure_authentication, prevent_login_signup, ensure_message_authorization

messages_blueprint = Blueprint(
	'messages',
	__name__,
	template_folder='templates'
)


@messages_blueprint.before_request
def current_user():
	if session.get('user_id'):
		g.current_user = User.query.get(session['user_id'])
	else:
		g.current_user = None	


@messages_blueprint.route("/", methods=["GET", "POST"])
@ensure_authentication
@ensure_message_authorization
def index(user_id):
	if request.method == "POST":
		message = Message(request.form.get("text"), request.form.get("img"), user_id)
		db.session.add(message)
		db.session.commit()
		flash('Message Created')
		return redirect(url_for('messages.index', user_id=user_id))
	user = User.query.get(user_id)
	return render_template('messages/index.html', user=user)


@messages_blueprint.route("/new")
@ensure_authentication
@ensure_message_authorization
def new(user_id):
	form = MessageForm()
	user = User.query.get(user_id)
	return render_template('messages/new.html', user=user, form=form)


@messages_blueprint.route("/<int:id>", methods = ["GET", "PATCH", "DELETE"])
@ensure_authentication
@ensure_message_authorization
def show(user_id, id):
	message = Message.query.get(id)
	if request.method == b"PATCH":
		form = MessageForm(request.form)
		if form.validate():
			message.text = form.text.data
			message.img = form.img.data
			db.session.add(message)
			db.session.commit()
			flash('Message Updated')
			return redirect(url_for('messages.index', user_id=user_id))
		return render_template('messages/edit.html', message=message, form=form)
	if request.method == b"DELETE":
		delete_form = DeleteForm(request.form)
		if delete_form.validate():
			db.session.delete(message)
			db.session.commit()
			flash('Message Deleted')
		return redirect(url_for('messages.index', user_id=user_id))
	delete_form = DeleteForm()
	return render_template('messages/show.html', message=message, delete_form=delete_form)


@messages_blueprint.route("/<int:id>/edit")
@ensure_authentication
@ensure_message_authorization
def edit(user_id, id):
	message = Message.query.get(id)
	form = MessageForm(obj=message)
	return render_template('messages/edit.html', message=message, form=form)