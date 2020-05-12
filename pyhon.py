from flask import Flask, render_template, redirect, request
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_restful import abort

from data import db_session
from data.offerform import OfferForm
from data.login_form import LoginForm
from data.users import User
from data.search import SearchForm
from data.offers import Offer
from data.register_form import RegisterForm
from data.profile_edit_form import ProfileEditForm
from data.photoform import PhotoForm
import os
from werkzeug.utils import secure_filename
#fcmt
app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)

def main():
    db_session.global_init("db/shop.sqlite")

    @login_manager.user_loader
    def load_user(user_id):
        session = db_session.create_session()
        return session.query(User).get(user_id)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        form = LoginForm()
        if form.validate_on_submit():
            session = db_session.create_session()
            user = session.query(User).filter(User.email == form.email.data).first()
            if user and user.check_password(form.password.data):
                login_user(user, remember=form.remember_me.data)
                return redirect("/")
            return render_template('login.html', message="Wrong login or password", form=form)
        return render_template('login.html', title='Authorization', form=form)

    @app.route("/")
    def index():
        return redirect('/home')

    @app.route("/home")
    def home():
        return redirect("/home/0/0")

    @app.route("/home/<int:pg>/<string:search>", methods=['GET', 'POST'])
    def homepage(pg, search):
        session = db_session.create_session()
        maxpage = (len(session.query(Offer).all()) // 50)
        form = SearchForm()
        if form.validate_on_submit():
            search = form.search.data
            return redirect(f"/home/{pg}/{search}")
        if search == '0':
            offers = session.query(Offer).filter((Offer.id > pg*50 - 1) | (Offer.id < (pg*50 + 51))).all()
        else:
            offers = session.query(Offer).filter(Offer.offer.like(f'%{search}%'), ((Offer.id > pg * 50 - 1) | (Offer.id < (pg * 50 + 51)))).all()
        return render_template("home.html", title='Home', page='home', offers=offers, search=search, pg=pg, maxpage=maxpage, prpg=pg-1, nxpg=pg+1, form=form)

    @app.route("/profile")
    def profile():
        return render_template("profile.html", title='Profile')

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        form = RegisterForm()
        if form.validate_on_submit():
            if form.password.data != form.password_again.data:
                return render_template('register.html', title='Register', form=form,
                                       message="Passwords don't match")
            session = db_session.create_session()
            if session.query(User).filter(User.email == form.email.data).first():
                return render_template('register.html', title='Register', form=form,
                                       message="This user already exists")
            user = User(
                name=form.name.data,
                surname=form.surname.data,
                bd=form.bd.data,
                email=form.email.data,
                address=form.address.data,
                phone_number=form.phone_number.data,
                description=form.description.data
            )
            user.set_password(form.password.data)
            session.add(user)
            session.commit()
            return redirect('/login')
        return render_template('register.html', title='Registration', form=form)

    @app.route('/newoffer', methods=['GET', 'POST'])
    @login_required
    def newoffer():
        ofform = OfferForm()
        if current_user.phone_number:
            ofform.contact_number.data = current_user.phone_number
        if ofform.validate_on_submit():
            session = db_session.create_session()
            offer = Offer(
                offer=ofform.offer.data,
                description=ofform.description.data,
                creator=current_user.id,
                quantity=ofform.quantity.data,
                price=ofform.price.data,
                contact_number=ofform.contact_number.data,
                location=ofform.location.data
            )
            session.add(offer)
            session.commit()
            f = ofform.thumbnail.data
            if f:
                if not os.path.exists(f'static\\images\\{offer.id}'):
                    os.mkdir(f'static\\images\\{offer.id}')
                f.save(f'static\\images\\{offer.id}\\thumbnail.jpg')
            return redirect('/')
        return render_template('newoffer.html', title='New offer', form=ofform)

    @app.route('/edit-offer/<int:id>', methods=['GET', 'POST'])
    @login_required
    def offer_edit(id):
        form = OfferForm()
        if request.method == "GET":
            session = db_session.create_session()
            offer = session.query(Offer).filter(Offer.id == id, Offer.creator == current_user.id).first()
            if offer:
                form.offer.data = offer.offer
                form.description.data = offer.description
                form.quantity.data = offer.quantity
                form.price.data = offer.price
                form.contact_number.data = offer.contact_number
                form.location.data = offer.location
            else:
                abort(404)
        if form.validate_on_submit():
            session = db_session.create_session()
            offer = session.query(Offer).filter(Offer.id == id, Offer.creator == current_user.id).first()
            if offer:
                offer.offer = form.offer.data
                offer.description = form.description.data
                offer.quantity = form.quantity.data
                offer.price = form.price.data
                offer.contact_number = form.contact_number.data
                offer.location = form.location.data
                session.commit()

                f = form.thumbnail.data
                if f:
                    if not os.path.exists(f'static\\images\\{offer.id}'):
                        os.mkdir(f'static\\images\\{offer.id}')
                    f.save(f'static\\images\\{offer.id}\\thumbnail.jpg')

                return redirect(f'/view-offer/{offer.id}')
            else:
                abort(404)
        return render_template('newoffer.html', title='Offer edit', form=form)

    @app.route('/delete-offer/<int:id>', methods=['GET', 'POST'])
    @login_required
    def delete_offer(id):
        session = db_session.create_session()
        offer = session.query(Offer).filter(Offer.id == id, Offer.creator == current_user.id).first()
        if offer:
            dir = f"static\\images\\{offer.id}"
            if os.path.exists(dir):
                for filename in os.listdir(dir):
                    os.remove(f"{dir}\\{filename}")
            session.delete(offer)
            session.commit()
            return redirect('/')
        else:
            abort(404)

    @app.route('/view-offer/<int:id>', methods=['GET', 'POST'])
    def view_offer(id):
            session = db_session.create_session()
            offer = session.query(Offer).filter(Offer.id == id).first()
            creator = session.query(User).filter(User.id == offer.creator).first()
            if offer:
                dir = f'static\\images\\{offer.id}'
                filenames = []
                if os.path.exists(dir):
                    for filename in os.listdir(dir):
                        filenames.append(filename)
                form = PhotoForm()
                if form.validate_on_submit():
                    f = form.photo.data
                    if not os.path.exists(dir):
                        os.mkdir(dir)
                    dir = dir + '\\'
                    if f.filename in filenames:
                        i = 0
                        while True:
                            newfilename = str(i) + f.filename
                            if newfilename not in filenames:
                                break
                            i += 1
                        f.save(dir + newfilename)
                    else:
                        f.save(dir + f.filename)
                    return redirect(f'/view-offer/{offer.id}')

                return render_template('view_offer.html', title=offer.offer, offer=offer, creator=creator, form=form, filenames=filenames)
            else:
                abort(404)

    @app.route('/view-profile/<int:id>')
    def view_profile(id):
            session = db_session.create_session()
            user = session.query(User).filter(User.id == id).first()
            offers = session.query(Offer).filter(Offer.creator == id)
            if user:
                return render_template('view_profile.html', title='profile of ' + user.name + ' ' + user.surname, user=user, offers=offers)
            else:
                abort(404)

    @app.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
    @login_required
    def profile_edit(id):
        form = ProfileEditForm()
        if request.method == "GET":
            session = db_session.create_session()
            user = session.query(User).filter(User.id == id, User.id == current_user.id).first()
            if user:
                form.surname.data = user.surname
                form.name.data = user.name
                form.bd.data = user.bd
                form.address.data = user.address
                form.phone_number.data = user.phone_number
                form.description.data = user.description
            else:
                abort(404)
        if form.validate_on_submit():
            session = db_session.create_session()
            user = session.query(User).filter(User.id == id, User.id == current_user.id).first()
            if user:
                user.surname = form.surname.data
                user.name = form.name.data
                user.bd = form.bd.data
                user.address = form.address.data
                user.phone_number = form.phone_number.data
                user.description = form.description.data
                session.commit()
                return redirect(f'/view-profile/{id}')
            else:
                abort(404)
        return render_template('profile_edit.html', title='Profile edit', form=form)

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect("/")
    app.run()


if __name__ == '__main__':
    main()


