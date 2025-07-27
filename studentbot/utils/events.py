import json
from datetime import datetime

def load_events():
    with open('knowledge_base_guide.json', 'r', encoding='utf-8') as f:
        guide_data = json.load(f)

    events = []
    for category in guide_data['guide']['categories']:
        for subsection in category.get('subsections', []):
            if 'details' in subsection:
                for detail in subsection['details']['fa']:
                    # This is a simple parsing logic, it can be improved
                    if 'deadline' in detail.lower() or 'تاریخ' in detail or 'ددلاین' in detail:
                        try:
                            # This is a placeholder for a more robust date parsing logic
                            date_str = detail.split(': ')[1].split('(')[0].strip()
                            date = datetime.strptime(date_str, '%d %B %Y')
                            events.append({'date': date, 'description': detail})
                        except:
                            pass
    return events

def get_events_for_month(year, month):
    events = load_events()
    return [event for event in events if event['date'].year == year and event['date'].month == month]

def get_upcoming_events(days=7):
    events = load_events()
    now = datetime.now()
    upcoming_events = []
    for event in events:
        delta = event['date'] - now
        if 0 <= delta.days <= days:
            upcoming_events.append(event)
    return upcoming_events
