import requests
import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("firebase_keys.json")
firebase_admin.initialize_app(cred)

db = firestore.client()


def fetch_best_stories() -> list:
    response = requests.get(
        "https://hacker-news.firebaseio.com/v0/topstories.json", timeout=5
    )

    # Checking if the request was successful
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch data. Status code: {response.status_code}")

    return []


def get_story_details(item_id: str) -> dict:
    response = requests.get(
        f"https://hacker-news.firebaseio.com/v0/item/{item_id}.json", timeout=5
    )
    # Checking if the request was successful
    if response.status_code == 200:
        story_data = response.json()
        if story_data["type"] != "story":
            return {}
        return response.json()
    else:
        print(f"Failed to story Details. Status code: {response.status_code}")

    return {}


def _filter_posted_stories(story_ids: list) -> list:
    filtered_story_ids = []
    for story_id in story_ids:
        story_doc = db.collection("posted_stories").document(str(story_id))
        if not story_doc.get().exists:
            filtered_story_ids.append(story_id)
    return filtered_story_ids


def fetch_unposted_story_ids() -> list:
    story_ids: list = fetch_best_stories()
    return _filter_posted_stories(story_ids)
