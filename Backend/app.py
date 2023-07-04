import asyncio
from datetime import datetime, timedelta

from apscheduler.schedulers.background import BackgroundScheduler

from controllers.explainer import explainer
from controllers.web_app import web_app_bp
from config import app, app_log as log, explainer_log,EXPLAINER_INTERVAL

app.register_blueprint(web_app_bp)


@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>404 Page not found.</p>", 404


async def run_explainer():
    explainer_log.info("Running the explainer")
    await explainer()
    explainer_log.info("Explainer finished")


def run_explainer_job():
    asyncio.run(run_explainer())


def run_scheduler():
    explainer_log.info("Starting the scheduler")
    scheduler = BackgroundScheduler()
    scheduler.add_job(run_explainer_job, 'date', run_date=datetime.now() + timedelta(seconds=1))  # Run after 1 second
    scheduler.add_job(run_explainer_job, 'interval', seconds=EXPLAINER_INTERVAL)  # Run every 10 minutes
    scheduler.start()


def main():
    log.info("Starting the app")
    run_scheduler()
    app.run(port=5000, debug=True)


if __name__ == "__main__":
    main()
