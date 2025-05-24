from apscheduler.schedulers.background import BackgroundScheduler
from .database import Database

def cleanup_inactive_caches():
    """Functie die periodiek wordt uitgevoerd om inactieve caches op te ruimen"""
    db = Database()
    removed_count = db.cleanup_inactive_caches()
    if removed_count > 0:
        print(f"Opgeruimd: {removed_count} inactieve caches verwijderd")
    db.__del__()

def init_scheduler():
    """Initialiseer de scheduler met de cleanup taak"""
    scheduler = BackgroundScheduler()
    # Voer de cleanup elke dag om middernacht uit
    scheduler.add_job(cleanup_inactive_caches, 'cron', hour=0, minute=0)
    scheduler.start() 