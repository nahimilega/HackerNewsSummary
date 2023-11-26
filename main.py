from flask import (
    Flask,
    jsonify,
)
from flask_cors import CORS

import get_hn_details
from story import Story

# Initialize Flask app and Firestore client
app = Flask(__name__)
CORS(app)


update_request_logs = False


@app.route("/")
def index():
    return jsonify({"message": "Hello World!"}), 200


@app.route("/update_channel", methods=["POST", "GET"])
def update_channel():
    global update_request_logs
    if update_request_logs:
        return jsonify({"done": "okay"}), 200
    update_request_logs = True
    story_ids = get_hn_details.fetch_unposted_story_ids()[:15]
    # story_ids = ["38305234"]
    for story_id in story_ids:
        print(story_id)
        story_details = get_hn_details.get_story_details(story_id)
        if story_details == {}:  # story_details is empty
            continue
        story_data: Story = Story(story_details)
        story_data.post_story_to_telegram()

    update_request_logs = False
    return jsonify({"done": "okay"}), 200


if __name__ == "__main__":
    app.run(debug=True)
