from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# === MODELOS DE BASE DE DATOS ===


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


# === CLASES PARA GESTIÓN DE LÓGICA ===
class UserManager:
    @staticmethod
    def register(username, password):
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('El nombre de usuario ya está en uso.', 'danger')
            return False
        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        flash('¡Registro exitoso! Ahora puedes iniciar sesión.', 'success')
        return True

    @staticmethod
    def login(username, password):
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            flash('Inicio de sesión exitoso.', 'success')
            return True
        flash('Credenciales inválidas. Inténtalo de nuevo.', 'danger')
        return False

    @staticmethod
    def edit_profile(user, username, description, profile_picture):
        user.username = username
        user.description = description
        if profile_picture and allowed_file(profile_picture.filename):
            filename = secure_filename(profile_picture.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            profile_picture.save(file_path)
            user.profile_picture = url_for('uploaded_file', filename=filename)
        db.session.commit()
        flash('Perfil actualizado exitosamente', 'success')


class VideoManager:
    @staticmethod
    def upload_video(title, description, youtube_url, user_id):
        video_id = get_video_id(youtube_url)
        if not video_id:
            flash('No se pudo crear el video. URL de YouTube no válida', 'danger')
            return False
        video = Video(
            title=title,
            description=description,
            youtube_url=youtube_url,
            video_id=video_id,
            user_id=user_id
        )
        db.session.add(video)
        db.session.commit()
        flash('Video creado exitosamente', 'success')
        return True

    @staticmethod
    def delete_video(video_id):
        video = Video.query.get(video_id)
        if video:
            db.session.delete(video)
            db.session.commit()
            flash('Video eliminado exitosamente', 'success')
            return True
        flash('Video no encontrado', 'danger')
        return False


class SEOManager:
    @staticmethod
    def update_seo(title, description, keywords):
        return {
            'title': title,
            'description': description,
            'keywords': keywords
        }


# === FUNCIONES AUXILIARES ===
def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_video_id(youtube_url):
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", youtube_url)
    return match.group(1) if match else None


# === RUTAS DE LA APLICACIÓN ===
@app.route('/')
def inicio():
    seo = SEOManager.update_seo(
        title="Inicio - Compilando Code",
        description="Servicios de Consultoría y Capacitación Tecnológica.",
        keywords="Transformación Digital, Desarrollo de Software"
    )
    return render_template('inicio.html', **seo)


@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if UserManager.register(username, password):
            return redirect(url_for('login'))
    return render_template('registro.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if UserManager.login(username, password):
            return redirect(url_for('index'))
    return render_template('login.html')


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        username = request.form['username']
        description = request.form['description']
        profile_picture = request.files['profile_picture'] if 'profile_picture' in request.files else None
        UserManager.edit_profile(
            current_user, username, description, profile_picture)
        return redirect(url_for('profile'))
    return render_template('edit_profile.html', user=current_user)


@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_video():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        youtube_url = request.form['url']
        VideoManager.upload_video(
            title, description, youtube_url, current_user.id)
        return redirect(url_for('mis_videos'))
    return render_template('upload.html')


@app.route('/mis_videos')
@login_required
def mis_videos():
    videos = Video.query.filter_by(user_id=current_user.id).order_by(
        Video.fecha_creacion.desc()).all()
    return render_template('mis_videos.html', videos=videos)


@app.route('/delete/<int:id>')
@login_required
def delete_video_route(id):
    VideoManager.delete_video(id)
    return redirect(url_for('mis_videos'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
