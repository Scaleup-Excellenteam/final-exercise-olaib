from controllers.web_app import web_app_bp
from config import app

app.register_blueprint(web_app_bp)


@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404


if __name__ == "__main__":
    app.run(port=5000, debug=True)
