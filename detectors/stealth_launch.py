from app.events.event_queue import get_events


def run_detector():

    events = get_events()

    if not events:
        return

    for event in events:

        event_type = event["type"]
        data = event["data"]

        print("\n[Detector] Event received")

        print("Type:", event_type)
        print("Data:", data)