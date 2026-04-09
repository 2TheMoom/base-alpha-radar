from collections import deque

event_queue = deque()

def push_event(event_type, data):

    event = {
        "type": event_type,
        "data": data
    }

    print(f"[QUEUE] Event added: {event_type}")

    event_queue.append(event)


def get_events():

    events = list(event_queue)

    event_queue.clear()

    return events