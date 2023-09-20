from flask import Flask, render_template, request

app = Flask(__name__)


def embed_youtube_url(youtube_url):
    parts = youtube_url.split("=")
    video_id = parts[-1]
    embed_url = f"https://www.youtube.com/embed/{video_id}?si=RSU935ew-UDTDonW"
    return embed_url


@app.route('/', methods=['GET', 'POST'])
def index():
    embed_url = None

    if request.method == 'POST':
        youtube_url = request.form.get('youtube_url')
        if youtube_url:
            embed_url = embed_youtube_url(youtube_url)

    return render_template('prueba.html', embed_url=embed_url)


if __name__ == '__main__':
    app.run(debug=True)
