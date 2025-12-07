from flask import Flask, jsonify
from flask_cors import CORS
import requests
import time

app = Flask(__name__)
CORS(app)  # abilita CORS per tutte le origini

ANILIST_URL = "https://graphql.anilist.co"

# Cache in memoria per manga e manhwa (AniList)
_manga_cache = {"data": None, "timestamp": 0}
_manhwa_cache = {"data": None, "timestamp": 0}
CACHE_TTL_SECONDS = 600  # 10 minuti


def _anilist_request(query: str, variables: dict):
    """Funzione di utilità per chiamare AniList con error handling."""
    resp = requests.post(
        ANILIST_URL,
        json={"query": query, "variables": variables},
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()


def fetch_latest_manga(limit: int = 6):
    """
    Manga (generici) aggiornati di recente da AniList.
    Usa una cache per evitare di superare il rate limit.
    """
    now = time.time()

    if (
        _manga_cache["data"] is not None
        and (now - _manga_cache["timestamp"]) < CACHE_TTL_SECONDS
    ):
        return _manga_cache["data"]

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

    variables = {"page": 1, "perPage": limit}

    try:
        json_data = _anilist_request(query, variables)
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
                "url": m.get("siteUrl"),
            })

        _manga_cache["data"] = results
        _manga_cache["timestamp"] = now
        return results

    except Exception as e:
        print("Errore nel chiamare AniList (manga):", e)

        if _manga_cache["data"] is not None:
            return _manga_cache["data"]

        return [
            {
                "title": "Jujutsu Kaisen",
                "chapter": "Cap. 252",
                "cover": "https://via.placeholder.com/150x220?text=JJK",
                "date": "Fallback",
            }
        ]


def fetch_latest_manhwa(limit: int = 6):
    """
    Manhwa (titoli coreani) da AniList.
    Filtra per countryOfOrigin = KR.
    Anche qui usiamo una cache.
    """
    now = time.time()

    if (
        _manhwa_cache["data"] is not None
        and (now - _manhwa_cache["timestamp"]) < CACHE_TTL_SECONDS
    ):
        return _manhwa_cache["data"]

    query = """
    query ($page: Int, $perPage: Int) {
      Page(page: $page, perPage: $perPage) {
        media(
          type: MANGA
          countryOfOrigin: KR
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

    variables = {"page": 1, "perPage": limit}

    try:
        json_data = _anilist_request(query, variables)
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
                chapter_label = f"Ep. {chapters}"
            else:
                chapter_label = "Episodi in corso"

            cover = (m.get("coverImage") or {}).get("large") or \
                "https://via.placeholder.com/150x220?text=Manhwa"

            results.append({
                "title": title,
                "chapter": chapter_label,
                "cover": cover,
                "date": "Aggiornato di recente",
                "url": m.get("siteUrl"),
            })

        _manhwa_cache["data"] = results
        _manhwa_cache["timestamp"] = now
        return results

    except Exception as e:
        print("Errore nel chiamare AniList (manhwa):", e)

        if _manhwa_cache["data"] is not None:
            return _manhwa_cache["data"]

        return [
            {
                "title": "Solo Leveling",
                "chapter": "Ep. 243",
                "cover": "https://via.placeholder.com/150x220?text=Solo+Leveling",
                "date": "Fallback",
            }
        ]


@app.route("/api/home")
def home():
    # Ongoing per ora li lasciamo statici
    ongoing = [
        {
            "title": "One Piece",
            "chapter": "Cap. 1105",
            "cover": "https://via.placeholder.com/150x220?text=One+Piece",
        },
        {
            "title": "The Fragrant Flower Blooms with Dignity",
            "chapter": "Cap. 42",
            "cover": "https://via.placeholder.com/150x220?text=Fragrant+Flower",
        },
    ]

    latest_manga = fetch_latest_manga(limit=6)
    latest_manhwa = fetch_latest_manhwa(limit=6)

    data = {
        "ongoing": ongoing,
        "latest_manga": latest_manga,
        "latest_manhwa": latest_manhwa,
    }

    return jsonify(data)


if __name__ == "__main__":
    app.run(port=5000)
