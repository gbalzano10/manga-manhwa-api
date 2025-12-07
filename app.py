from flask import Flask, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)  # abilita CORS per tutte le origini

ANILIST_URL = "https://graphql.anilist.co"


def fetch_latest_manga(limit: int = 6):
    """
    Prende alcuni manga 'aggiornati di recente' da AniList
    e li converte nel formato che usa la tua WebApp.
    """
    query = """
    query ($page: Int, $perPage: Int) {
      Page(page: $page, perPage: $perPage) {
        media(
          type: MANGA
          sort: UPDATED_AT_DESC
          status_in: [RELEASING]
        ) {
          id
          title {
            romaji
            english
            native
          }
          coverImage {
            large
          }
          chapters
          siteUrl
        }
      }
    }
    """

    variables = {
        "page": 1,
        "perPage": limit
    }

    resp = requests.post(
        ANILIST_URL,
        json={"query": query, "variables": variables},
        timeout=10,
    )
    resp.raise_for_status()
    json_data = resp.json()

    media_list = json_data["data"]["Page"]["media"]

    results = []
    for m in media_list:
        title_info = m.get("title") or {}
        title = (
            title_info.get("romaji")
            or title_info.get("english")
            or title_info.get("native")
            or "Senza titolo"
        )

        chapters = m.get("chapters")
        if chapters:
            chapter_label = f"Cap. {chapters}"
        else:
            chapter_label = "Capitoli in corso"

        cover = (m.get("coverImage") or {}).get("large") or \
            "https://via.placeholder.com/150x220?text=Manga"

        results.append({
            "title": title,
            "chapter": chapter_label,
            "cover": cover,
            "date": "Aggiornato di recente",
            # se vorrai, potrai usarlo nella card come link
            "url": m.get("siteUrl")
        })

    return results


@app.route("/api/home")
def home():
    # Ongoing e manhwa per ora sono ancora dummy
    ongoing = [
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
    ]

    latest_manhwa = [
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

    try:
        latest_manga = fetch_latest_manga(limit=6)
    except Exception as e:
        # Se AniList dà errore, non facciamo crashare tutto
        print("Errore nel chiamare AniList:", e)
        latest_manga = [
            {
                "title": "Jujutsu Kaisen",
                "chapter": "Cap. 252",
                "cover": "https://via.placeholder.com/150x220?text=JJK",
                "date": "Oggi"
            }
        ]

    data = {
        "ongoing": ongoing,
        "latest_manga": latest_manga,
        "latest_manhwa": latest_manhwa
    }

    return jsonify(data)


if __name__ == "__main__":
    app.run(port=5000)
