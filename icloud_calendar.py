import os
from datetime import datetime, timedelta
from caldav import DAVClient
from dateutil import tz

# Chargement des identifiants iCloud depuis les variables d'environnement
ICLOUD_USERNAME = os.getenv('ICLOUD_USERNAME')
ICLOUD_APP_PASSWORD = os.getenv('ICLOUD_APP_PASSWORD')

if not ICLOUD_USERNAME or not ICLOUD_APP_PASSWORD:
    raise RuntimeError("Merci de définir ICLOUD_USERNAME et ICLOUD_APP_PASSWORD dans vos variables d'environnement.")

# Connexion au client CalDAV
client = DAVClient(
    url="https://caldav.icloud.com",
    username=ICLOUD_USERNAME,
    password=ICLOUD_APP_PASSWORD
)
principal = client.principal()

def get_upcoming_events(days=7, calendar_name="Famille"):
    # Sélection du bon calendrier "Famille" sans emoji ⚠️
    calendars = principal.calendars()
    selected_calendar = None

    for cal in calendars:
        if cal.name == calendar_name and "⚠️" not in cal.name:
            selected_calendar = cal
            break

    if not selected_calendar:
        print(f"❌ Calendrier '{calendar_name}' non trouvé.")
        return []

    start = datetime.utcnow()
    end = start + timedelta(days=days)

    # Recherche des événements dans l’intervalle
    events = selected_calendar.date_search(start, end)
    result = []

    for event in events:
        try:
            vevent = event.vobject_instance.vevent
            summary = vevent.summary.value
            dtstart = vevent.dtstart.value

            # Conversion UTC -> local
            if isinstance(dtstart, datetime) and dtstart.tzinfo is not None:
                dtstart_local = dtstart.astimezone(tz.tzlocal())
            else:
                dtstart_local = datetime.combine(dtstart, datetime.min.time())

            formatted_time = dtstart_local.strftime('%d/%m %H:%M')
            result.append((dtstart_local, f"{formatted_time} - {summary}"))

        except Exception as e:
            result.append((datetime.max, f"[⚠️ Erreur de lecture d’un événement : {e}]"))

    # Tri par date
    result.sort(key=lambda x: x[0])
    return [r[1] for r in result]
