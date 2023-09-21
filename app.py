from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime


app = Flask(__name__)

# Configuración de la base de datos (SQLite)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///videos.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)


# Definición del modelo de base de datos


class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    youtube_url = db.Column(db.String(255), nullable=False)
    video_id = db.Column(db.String(255), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_actualizacion = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    # Puedes agregar más campos según tus necesidades (usuario que subió el video, fecha de carga, etc.)

# fin de creación base de datos

# Función para obtener el video_id de una URL de YouTube


def get_video_id(youtube_url):
    # Buscar el parámetro "v" en la URL
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
        embed_url = f"https://www.youtube.com/embed/{video_id}?si=RSU935ew-UDTDonW"
        return embed_url
    return None

# Ruta para mostrar la lista de videos


# @app.route('/')
# def index():
#     videos = Video.query.all()
#     videos_ordenados = sorted(
#         videos, key=lambda video: video.id, reverse=True)

#     return render_template('index.html', videos=videos_ordenados, embed_youtube_url=embed_youtube_url)

@app.route('/')
def index():
    # Obtén el parámetro 'orden' de la consulta
    orden = request.args.get('orden', 'desc')

    # Ordena los videos según el valor del parámetro 'orden'
    if orden == 'asc':
        videos = Video.query.order_by(Video.id.asc()).all()
    else:
        videos = Video.query.order_by(Video.id.desc()).all()

    return render_template('index.html', videos=videos, embed_youtube_url=embed_youtube_url)

# Ruta para cargar un nuevo video


@app.route('/upload', methods=['GET', 'POST'])
def upload_video():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        youtube_url = request.form['url']

        # Obtener el video_id de la URL de YouTube
        video_id = get_video_id(youtube_url)

        if video_id:
            # Crear una instancia del modelo Video y agregarla a la base de datos
            video = Video(title=title, description=description,
                          youtube_url=youtube_url, video_id=video_id)
            db.session.add(video)
            db.session.commit()

            # Redirigir a la página principal para mostrar los videos
            return redirect(url_for('index'))

    return render_template('upload.html')

# completando crud
# para ver detalle


@app.route('/video/<int:id>')
def show_video_detail(id):
    video = Video.query.get(id)
    return render_template('show.html', video=video, embed_youtube_url=embed_youtube_url)


# para editar o actualizar los datos del video
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_video(id):
    video = Video.query.get(id)
    if request.method == 'POST':
        # Obtén los datos actualizados del formulario
        video.title = request.form['title']
        video.description = request.form['description']
        video.youtube_url = request.form['youtube_url']
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('update.html', video=video,  embed_youtube_url=embed_youtube_url)

# para eliminar video


@app.route('/delete/<int:id>')
def delete_video(id):
    video = Video.query.get(id)
    db.session.delete(video)
    db.session.commit()
    return redirect(url_for('index'))


# buscador
@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    # Realiza la búsqueda en la base de datos o donde almacenes tus datos
    # Aquí puedes usar SQLAlchemy para buscar videos que coincidan con la consulta.
    videos = Video.query.filter(Video.title.contains(query)).all()
    return render_template('search.html', videos=videos, query=query)


if __name__ == '__main__':
    # Crear la base de datos si no existe y ejecutar la aplicación en modo de depuración
    with app.app_context():
        db.create_all()
    app.run(debug=True)
