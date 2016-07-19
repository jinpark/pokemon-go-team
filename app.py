from flask import Flask, request, redirect, url_for, jsonify, json
from flask import render_template
from werkzeug.utils import secure_filename
from PIL import Image
import uuid
import os
from pokemonocr import ocr_image

import redis

app = Flask(__name__)
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')
r = redis.StrictRedis.from_url(REDIS_URL)

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/upload", methods=['POST'])
def upload():
    file = request.files['screenshot']
    text = ocr_image(file)
    random_key = uuid.uuid4().hex[0:8]
    r.set(random_key, json.dumps(text))
    return redirect(url_for('team', team_hash=random_key))

@app.route("/team/<team_hash>")
def team(team_hash):
    text_byte = r.get(team_hash)
    text = str(text_byte, "utf-8")
    return render_template("team.html", team_json=text)

if __name__ == "__main__":
    app.run()
