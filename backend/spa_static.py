import os
from flask import send_from_directory, request

def register_spa(app):
    # Point Flask at the built React app (frontend/dist)
    dist_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend", "dist"))
    app.static_folder = dist_dir
    app.static_url_path = "/"

    # Serve the SPA index at /
    @app.get("/")
    def spa_index():
        return send_from_directory(app.static_folder, "index.html")

    # Serve asset files under /assets/*
    @app.get("/assets/<path:path>")
    def spa_assets(path):
        return send_from_directory(os.path.join(app.static_folder, "assets"), path)

    # Catch-all for SPA routes (but don't eat API routes)
    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def spa_catchall(path):
        if path.startswith("api"):
            return {"error": "Not found"}, 404
        full = os.path.join(app.static_folder, path)
        if os.path.isfile(full):
            return send_from_directory(app.static_folder, path)
        return send_from_directory(app.static_folder, "index.html")
