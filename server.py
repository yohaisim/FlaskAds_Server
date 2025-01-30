import os
from flask import Flask, jsonify, request, render_template, redirect, url_for
from flask_cors import CORS
from pymongo import MongoClient

app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)

# ---------------------- DATABASE CONNECTION ----------------------
try:
    MONGO_URI = "mongodb+srv://yohaisimhony:i33Gp5UYfnhchk7r@cluster0.29ufd.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    client = MongoClient(MONGO_URI)
    db = client["ads_db"]
    ads_collection = db["ads"]
    print("✅ Successfully connected to MongoDB")
except Exception as e:
    print("❌ Error connecting to MongoDB:", str(e))
    ads_collection = None  # Prevent crashes if MongoDB is unavailable

# ---------------------- WEB MANAGEMENT PORTAL ----------------------
@app.route("/")
def index():
    if ads_collection is None:
        return "❌ Database connection failed.", 500

    try:
        ads = list(ads_collection.find({}, {"_id": 0}))
        print(f"📢 Loaded {len(ads)} ads from DB")  # Debugging
    except Exception as e:
        print(f"❌ Error fetching ads: {e}")
        return "❌ Error fetching ads", 500

    return render_template("index.html", ads=ads)

@app.route("/add_ad", methods=["POST"])
def add_ad_web():
    if ads_collection is None:
        return "❌ Database connection failed.", 500

    try:
        data = request.form
        new_ad = {
            "title": data["title"],
            "description": data["description"],
            "image_url": data["image_url"],
            "click_url": data["click_url"],
            "views": 0,
            "clicks": 0
        }
        ads_collection.insert_one(new_ad)
        print(f"✅ Ad '{data['title']}' added to DB")
    except Exception as e:
        print(f"❌ Error adding ad: {e}")
        return "❌ Error adding ad", 500

    return redirect(url_for("index"))

@app.route("/delete_ad", methods=["POST"])
def delete_ad():
    if ads_collection is None:
        return "❌ Database connection failed.", 500

    try:
        title = request.form.get("title")
        result = ads_collection.delete_one({"title": title})
        if result.deleted_count:
            print(f"✅ Ad '{title}' deleted from DB")
        else:
            print(f"⚠️ Ad '{title}' not found in DB")
    except Exception as e:
        print(f"❌ Error deleting ad: {e}")
        return "❌ Error deleting ad", 500

    return redirect(url_for("index"))

# ---------------------- API ----------------------
@app.route('/ads', methods=['GET'])
def get_ads():
    try:
        ads = list(ads_collection.find({}, {"_id": 0}))
        print(f"📢 Returning {len(ads)} ads via API")
        return jsonify(ads), 200
    except Exception as e:
        print(f"❌ Error fetching ads: {e}")
        return jsonify({"error": "Error fetching ads"}), 500

@app.route('/ads/view', methods=['POST'])
def update_view_count():
    try:
        data = request.json
        ad_title = data.get("title")
        if not ad_title:
            return jsonify({"error": "Missing title"}), 400

        result = ads_collection.update_one({"title": ad_title}, {"$inc": {"views": 1}})
        if result.modified_count:
            print(f"✅ View count updated for '{ad_title}'")
        else:
            print(f"⚠️ Ad '{ad_title}' not found")

        return jsonify({"message": "View count updated"}), 200
    except Exception as e:
        print(f"❌ Error updating view count: {e}")
        return jsonify({"error": "Error updating view count"}), 500

@app.route('/ads/click', methods=['POST'])
def update_click_count():
    data = request.json
    ad_title = data.get("title")
    
    if not ad_title:
        return jsonify({"error": "Missing title"}), 400

    ads_collection.update_one({"title": ad_title}, {"$inc": {"clicks": 1}})
    return jsonify({"message": "Click count updated"}), 200



if __name__ == '__main__':
    app.run(debug=True)

def handler(event, context):
    return app(event, context)
