from __future__ import annotations

from dotenv import load_dotenv
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

from app.config import Config
from app.extensions import flatpages, my_renderer
from app.routes.site import site_bp
from app.routes.visualizations import visualizations_bp


load_dotenv()


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(
        __name__,
        static_folder=str(Config.STATIC_FOLDER),
        template_folder=str(Config.TEMPLATES_FOLDER),
    )
    app.config.from_object(Config)

    if test_config:
        app.config.from_mapping(test_config)

    flatpages.init_app(app)
    app.config["FLATPAGES_HTML_RENDERER"] = my_renderer
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_host=0)

    app.register_blueprint(site_bp)
    app.register_blueprint(visualizations_bp)

    return app


app = create_app()
