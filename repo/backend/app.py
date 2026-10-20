import logging
from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
from models import db
from routes.api import api
from routes.admin import admin
from routes.whatsapp import wa_bp
import models.whatsapp  # noqa: F401  (registers tables before create_all)
from seed.properties import seed_properties, seed_demo_leads

logging.basicConfig(level=logging.INFO)


def create_app(config=Config):
    app = Flask(__name__)
    app.config.from_object(config)
    CORS(app, origins=Config.CORS_ORIGINS)
    db.init_app(app)
    app.register_blueprint(api)
    app.register_blueprint(admin)
    app.register_blueprint(wa_bp)

    @app.errorhandler(404)
    def nf(_):
        return jsonify({"error": "Not found"}), 404

    @app.errorhandler(500)
    def ise(_):
        return jsonify({"error": "Something went wrong. Please try again."}), 500

    with app.app_context():
        db.create_all()
        seed_properties()
        seed_demo_leads()
    if not Config.ai_configured():
        app.logger.warning("AI_API_KEY / AI_MODEL not set: /api/chat will return an error until configured.")
    if Config.AGENT_PASSWORD == "change-me":
        app.logger.warning("AGENT_PASSWORD is the default. Change it in .env before sharing the demo.")
    if Config.WHATSAPP_ACCESS_TOKEN and not Config.WHATSAPP_APP_SECRET and not Config.WHATSAPP_ALLOW_UNSIGNED:
        app.logger.warning("WHATSAPP_APP_SECRET is not set: incoming webhooks will be rejected.")
    return app


if __name__ == "__main__":
    create_app().run(port=5000, debug=True)
