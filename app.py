from flask import Flask, Blueprint, render_template, request, redirect, url_for, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import DataRequired
from datetime import datetime
# from flask_uploads import UploadSet, configure_uploads, IMAGES
from flask_wtf.file import FileField, FileAllowed
from werkzeug.utils import secure_filename

import os

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta'

# Configuración de la base de datos (SQLite)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///videos.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)


# Configuración para subir archivos
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['UPLOADED_PHOTOS_DEST'] = 'uploads'
# photos = UploadSet('photos', IMAGES)
# configure_uploads(app, photos)

# Define una lista de extensiones de archivo permitidas para la imagen de perfil
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Configuración de Flask-Login
login_manager = LoginManager()
login_manager.login_view = 'login'  # Vista de inicio de sesión
login_manager.init_app(app)
# Función para verificar si la extensión del archivo es válida


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Definición del modelo de base de datos


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    profile_picture = db.Column(db.String(255), nullable=True)
    name = db.Column(db.String(255), nullable=True)
    description = db.Column(db.Text, nullable=True)
    videos = db.relationship('Video', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Modelo de Video


class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    youtube_url = db.Column(db.String(255), nullable=False)
    video_id = db.Column(db.String(255), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_actualizacion = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# Formulario de Registro


class RegistrationForm(FlaskForm):
    username = StringField('Nombre de Usuario', validators=[DataRequired()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    submit = SubmitField('Registrarse')

# Formulario de Edición de Perfil


class EditProfileForm(FlaskForm):
    username = StringField('Nombre de Usuario', validators=[DataRequired()])
    description = TextAreaField('Descripción')
    # profile_picture = FileField('Imagen de Perfil', validators=[
    #                             FileAllowed(photos, 'Solo imágenes')])
    submit = SubmitField('Guardar Cambios')

# fin de creación base de datos

# Función para obtener el video_id de una URL de YouTube


def get_video_id(youtube_url):
    start_idx = youtube_url.find("v=")
    if start_idx != -1:
        start_idx += 2
        end_idx = youtube_url.find("&", start_idx)
        if end_idx == -1:
            video_id = youtube_url[start_idx:]
        else:
            video_id = youtube_url[start_idx:end_idx]
        return video_id
    return None

# Función para incrustar URL de YouTube


def embed_youtube_url(youtube_url):
    video_id = get_video_id(youtube_url)
    if video_id:
        embed_url = f"https://www.youtube.com/embed/{video_id}"
        return embed_url
    return None

# Ruta para mostrar la lista de videos


@app.route('/')
def index():
    title = "Lista de mis videos de  youtube"
    orden = request.args.get('orden', 'desc')
    if orden == 'asc':
        videos = Video.query.order_by(Video.id.asc()).all()
    else:
        videos = Video.query.order_by(Video.id.desc()).all()
    return render_template('index.html', videos=videos, embed_youtube_url=embed_youtube_url, title=title)

# Ruta para cargar un nuevo video


@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_video():
    title = "Cargando Videos"
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        youtube_url = request.form['url']
        user_id = current_user.id
        video_id = get_video_id(youtube_url)
        if video_id:
            video = Video(
                title=title,
                description=description,
                youtube_url=youtube_url,
                video_id=video_id,
                user_id=user_id
            )
            db.session.add(video)
            db.session.commit()
            flash('Video creado exitosamente', 'success')  # Mensaje de éxito
            return redirect(url_for('mis_videos'))
        else:
            flash('No se pudo crear el video. URL de YouTube no válida',
                  'danger')  # Mensaje de error
    return render_template('upload.html', title=title)

# Ruta para ver detalles de un video


@app.route('/video/<int:id>')
@login_required
def show_video_detail(id):
    title = f"Detalle video {id} "
    video = Video.query.get(id)
    if not current_user.is_authenticated:
        flash('Inicia sesión para ver el video.', 'warning')
        return redirect(url_for('login'))
    return render_template('show.html', video=video, embed_youtube_url=embed_youtube_url, title=title)

# Ruta para ver solo los videos del usuario actual


@app.route('/mis_videos')
@login_required
def mis_videos():
    title = "mis videos"
    user_videos = Video.query.filter_by(user_id=current_user.id).all()
    user_videos = Video.query.filter_by(
        user_id=current_user.id).order_by(desc(Video.fecha_creacion)).all()
    return render_template('mis_videos.html', videos=user_videos, embed_youtube_url=embed_youtube_url, title=title)

# Ruta para editar un video


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_video(id):
    title = "edit video"
    video = Video.query.get(id)
    if request.method == 'POST':
        video.title = request.form['title']
        video.description = request.form['description']
        video.youtube_url = request.form['youtube_url']
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('update.html', video=video, embed_youtube_url=embed_youtube_url, title=title)

# Ruta para eliminar un video


@app.route('/delete/<int:id>')
def delete_video(id):

    video = Video.query.get(id)
    db.session.delete(video)
    db.session.commit()
    return redirect(url_for('index'))

# Ruta para buscar videos


@app.route('/search', methods=['GET'])
def search():
    title = "Buscando videos"
    query = request.args.get('query')

    videos = Video.query.filter((Video.title.contains(query)) | (
        Video.description.contains(query))).all()
    return render_template('search.html', videos=videos, query=query, title=title, embed_youtube_url=embed_youtube_url)

# Configura la ruta para la página de error 404


@app.errorhandler(404)
def not_found_error(error):
    title = "Pagina no Encotrado"
    return render_template('404.html', error=error, title=title), 404

# Ruta para editar el perfil del usuario


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    title = "editar perfil "
    form = EditProfileForm()
    if form.validate_on_submit():
        user = current_user
        user.username = form.username.data
        user.description = form.description.data
        profile_picture = form.profile_picture.data
        if profile_picture and allowed_file(profile_picture.filename):
            filename = secure_filename(profile_picture.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            profile_picture.save(file_path)
            user.profile_picture = url_for('uploaded_file', filename=filename)
        db.session.commit()
        flash('Perfil actualizado exitosamente', 'success')
        return redirect(url_for('profile'))
    form.username.data = current_user.username
    form.description.data = current_user.description
    return render_template('edit_profile.html', form=form, user=current_user, title=title)

# Ruta para mostrar la imagen de perfil del usuario


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Vista para cerrar sesión


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión exitosamente.', 'success')
    return redirect(url_for('index'))

# Inicio de sesión


@app.route('/login', methods=['GET', 'POST'])
def login():
    title = "Iniciando Sesión"
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            flash('Inicio de sesión exitoso.', 'success')
            return redirect(url_for('index'))
        flash('Credenciales inválidas. Inténtalo de nuevo.', 'danger')
    return render_template('login.html', title=title)

# registrar usuario


@app.route('/registro', methods=['GET', 'POST'])
def registro():
    title = "Registrando Usuario"
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Verificar si el usuario ya existe
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('El nombre de usuario ya está en uso.', 'danger')
        else:
            new_user = User(username=username)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            flash('¡Registro exitoso! Ahora puedes iniciar sesión.', 'success')
            # Redirige a la página de inicio de sesión
            return redirect(url_for('login'))
    return render_template('registro.html', title=title)


@login_manager.user_loader
def load_user(user_id):
    # Recupera y devuelve el objeto de usuario correspondiente al ID de usuario
    return User.query.get(int(user_id))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
