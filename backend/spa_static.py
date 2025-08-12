import os
from flask import send_from_directory

def register_spa(app):
    # Point to ../frontend/dist (created by Vite build)
    dist_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend", "dist"))
    app.static_folder = dist_dir
    app.static_url_path = "/"

    @app.get("/")
    def spa_index():
        return send_from_directory(app.static_folder, "index.html")

    @app.get("/assets/<path:path>")
    def spa_assets(path):
        return send_from_directory(os.path.join(app.static_folder, "assets"), path)

    # Catch-all for client-side routes. Never hijack /api/*
    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def spa_catchall(path):
        if path.startswith("api"):
            return {"error": "Not found"}, 404
        full = os.path.join(app.static_folder, path)
        if os.path.isfile(full):
            return send_from_directory(app.static_folder, path)
        return send_from_directory(app.static_folder, "index.html")
