import requests
import html
from firebase_admin import firestore
import telegram_message.send_message as send_message
import generate_summary.webpage_summary as webpage_summary
import generate_summary.comment_summary as comment_summary

# cred = credentials.Certificate("hn-ai-summary-d1e8eaad756d.json")
# firebase_admin.initialize_app(cred)

db = firestore.client()


class Story:
    def __init__(self, story_data: dict):
        """
        {
        "by" : "dhouston",
        "descendants" : 71,
        "id" : 8863,
        "kids" : [ 8952, 9224, 8917, 8884, 8887, 8943, 8869, 8958, 9005, 9671, 8940, 9067, 8908, 9055, 8865, 8881, 8872, 8873, 8955, 10403, 8903, 8928, 9125, 8998, 8901, 8902, 8907, 8894, 8878, 8870, 8980, 8934, 8876 ],
        "score" : 111,
        "time" : 1175714200,
        "title" : "My YC app: Dropbox - Throw away your USB drive",
        "type" : "story",
        "url" : "http://www.getdropbox.com/u/2/screencast.html"
        }

        """
        self.title = html.unescape(story_data["title"])
        self.time = story_data["time"]
        self.id = story_data["id"]
        if "url" in story_data:
            self.url = story_data["url"]
        else:
            self.url = ""
        self.comment_list = self.populate_comment_tree(story_data)
        # print(self.comment_list)

    def populate_comment_tree(self, story_data: dict) -> list:
        comment_list = []
        for kid in story_data["kids"]:
            comment_list.extend(self._recursively_populate_comment_data(kid))
        return comment_list

    def _recursively_populate_comment_data(self, item_id: str) -> list:
        comment_list = []
        response = requests.get(
            f"https://hacker-news.firebaseio.com/v0/item/{item_id}.json",
            timeout=5,
        )
        # Checking if the request was successful
        if response.status_code != 200:
            print(f"Failed to comments Details. Status code: {response.status_code}")
            return comment_list

        comment_data = response.json()
        if comment_data["type"] != "comment":
            return comment_list

        if "deleted" in comment_data and comment_data["deleted"] == True:
            return comment_list

        comment_list.append(html.unescape(comment_data["text"]))

        if "kids" in comment_data:
            for kid in comment_data["kids"]:
                comment_list.extend(self._recursively_populate_comment_data(kid))

        return comment_list

    def post_story_to_telegram(self):
        message: str = self._compose_message_for_telegram()
        comment_url = f"https://news.ycombinator.com/item?id={self.id}"
        article_url = self.url

        if article_url == "":
            article_url = comment_url

        send_message.send_telegram_message(message, article_url, comment_url)

        db.collection("posted_stories").document(str(self.id)).set(
            {
                "id": self.id,
            }
        )

    def _compose_message_for_telegram(self) -> str:
        #         "dehyped_title",
        # "article_summary",
        comment_summary_str: str = comment_summary.generate_comment_summary(self)

        message = f"<b>{self.title}</b>"

        if self.url != "":
            dehyped_title, article_summary = webpage_summary.generate_webpage_summary(
                self
            )
            if dehyped_title != "" and article_summary != "":
                message += f"\n\n<b>De-Hyped Title:</b> {dehyped_title}\n\n<b>Article Summary</b>\n{article_summary}"

        message += f"\n\n<b>Comment Summary<a href='{self.url}' style='color:#FFFFFF;'>:</a></b>\n{comment_summary_str}"
        return message
