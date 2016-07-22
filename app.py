from flask import Flask, request, redirect, url_for, jsonify, json
from flask import render_template
from werkzeug.utils import secure_filename
from PIL import Image
from pokemonocr import ocr_image
import pokemondata

import uuid
import os
import ast
import json
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
    random_key = uuid.uuid4().hex[0:10]
    r.set(random_key, json.dumps(text))
    return redirect(url_for('team_edit', team_hash=random_key))

@app.route("/team/<team_hash>/")
def team(team_hash):
    print('in team')
    text_byte = r.get(team_hash)
    text = str(text_byte, "utf-8")
    pokemon_dict = json.loads(text)
    return render_template("team.html", pokemon=json.dumps(pokemon_dict['pokemon']), 
        all_pokemon_names=json.dumps(pokemondata.all_pokemon_names), 
        fast_attacks=json.dumps(pokemondata.fast_attacks),
        special_attacks=json.dumps(pokemondata.special_attacks),
        team_hash=team_hash)

@app.route("/team/<team_hash>/edit")
def team_edit(team_hash):
    text_byte = r.get(team_hash)
    text = str(text_byte, "utf-8")
    pokemon_dict = json.loads(text)
    if pokemon_dict["edited"]:
        return redirect(url_for('team', team_hash=team_hash))

    return render_template("team_edit.html", pokemon=json.dumps(pokemon_dict['pokemon']), 
        all_pokemon_names=json.dumps(pokemondata.all_pokemon_names), 
        fast_attacks=json.dumps(pokemondata.fast_attacks),
        special_attacks=json.dumps(pokemondata.special_attacks),
        team_hash=team_hash)

@app.route("/team/<team_hash>/update", methods=['POST'])
def update(team_hash):
    text_byte = r.get(team_hash)
    text = str(text_byte, "utf-8")
    pokemon_dict = json.loads(text)
    if pokemon_dict["edited"]:
        return redirect(url_for('team', team_hash=team_hash))
    updated_json = request.get_json()
    pokemons = {"pokemon": updated_json, "edited": True}
    r.set(team_hash, json.dumps(pokemons))
    return redirect(url_for('team', team_hash=team_hash))

if __name__ == "__main__":
    app.config['DEBUG'] = True
    app.run()
