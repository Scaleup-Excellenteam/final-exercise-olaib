import asyncio
from datetime import datetime, timedelta

from apscheduler.schedulers.background import BackgroundScheduler

from controllers.explainer import explainer
from controllers.web_app import web_app_bp
from config import app, app_log as log, explainer_log, PROCESS_INTERVAL

app.register_blueprint(web_app_bp)


# todo: fix the explainer
@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>404 Page not found.</p>", 404


# async def run_explainer():
#     explainer_log.info("Running the explainer")
#     await explainer()
#     explainer_log.info("Explainer finished")
#
#
# def run_scheduler():
#     explainer_log.info("Starting the scheduler")
#     scheduler = BackgroundScheduler()
#     scheduler.add_job(run_explainer, 'date', run_date=datetime.now() + timedelta(seconds=1))  # Run after 1 second
#     scheduler.add_job(run_explainer, 'interval', minutes=10)  # Run every 10 minutes
#     scheduler.start()

async def run_explainer():
    while True:
        explainer_log.info("Running the explainer")
        await explainer()
        explainer_log.info("Explainer finished")
        await asyncio.sleep(PROCESS_INTERVAL * 1000)  # Wait for 10 minutes


def run_scheduler():
    explainer_log.info("Starting the scheduler")
    scheduler = BackgroundScheduler()
    scheduler.add_job(run_explainer, 'date', run_date=datetime.now() + timedelta(seconds=1))  # Run after 1 second
    scheduler.start()


def main():
    log.info("Starting the app")
    asyncio.run(run_explainer())  # Await the initial run of explainer
    run_scheduler()
    app.run(port=5000, debug=True)


if __name__ == "__main__":
    main()
