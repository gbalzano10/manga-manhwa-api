from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # abilita CORS per tutte le origini

@app.route("/api/home")
def home():
    data = {
        "ongoing": [
            {
                "title": "One Piece",
                "chapter": "Cap. 1105",
                "cover": "https://via.placeholder.com/150x220?text=One+Piece"
            },
            {
                "title": "The Fragrant Flower Blooms with Dignity",
                "chapter": "Cap. 42",
                "cover": "https://via.placeholder.com/150x220?text=Fragrant+Flower"
            }
        ],
        "latest_manga": [
            {
                "title": "Jujutsu Kaisen",
                "chapter": "Cap. 252",
                "cover": "https://via.placeholder.com/150x220?text=JJK",
                "date": "Oggi"
            },
            {
                "title": "My Hero Academia",
                "chapter": "Cap. 411",
                "cover": "https://via.placeholder.com/150x220?text=MHA",
                "date": "Ieri"
            }
        ],
        "latest_manhwa": [
            {
                "title": "Solo Leveling",
                "chapter": "Ep. 243",
                "cover": "https://via.placeholder.com/150x220?text=Solo+Leveling",
                "date": "Oggi"
            },
            {
                "title": "Tower of God",
                "chapter": "Ep. 605",
                "cover": "https://via.placeholder.com/150x220?text=ToG",
                "date": "2 giorni fa"
            }
        ]
    }
    return jsonify(data)

if __name__ == "__main__":
    app.run(port=5000)
