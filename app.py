from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
# configurando la base de datos
# Usa SQLite para la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///videos.db'
db = SQLAlchemy(app)
# creando el modelo de base de datos


class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    url = db.Column(db.String(255), nullable=False)
    # Agrega más campos según tus necesidades (usuario que subió el video, fecha de carga, etc.)

# Ruta para mostrar la lista de videos


@app.route('/')
def index():
    videos = Video.query.all()
    return render_template('index.html', videos=videos)

# Ruta para cargar un nuevo video


def embed_youtube_url(youtube_url):
    parts = youtube_url.split("=")
    video_id = parts[-1]
    embed_url = f"https://www.youtube.com/embed/{video_id}?si=RSU935ew-UDTDonW"
    return embed_url


@app.route('/upload', methods=['GET', 'POST'])
def upload_video():

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        url = request.form['url']

        video = Video(title=title, description=description, url=url)
        db.session.add(video)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('upload.html')


if __name__ == '__main__':
    # Crear la base de datos si no existe y ejecutar la aplicación en modo de depuración
    with app.app_context():
        db.create_all()
    app.run(debug=True)
