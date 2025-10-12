import logging
logger = logging.getLogger(__name__)

class EventDispatcher:
    _observers = {}

    @classmethod
    def register(cls, event_type, observer):
        """Register observer for an event type"""
        if event_type not in cls._observers:
            cls._observers[event_type] = []
        cls._observers[event_type].append(observer)

    @classmethod
    def notify(cls, event_type, **kwargs):
        """Notify all observers of this event type"""
        observers = cls._observers.get(event_type, [])
        for observer in observers:
            try:
                observer.update(**kwargs)
            except Exception as e:
                logger.error(f"[ObserverError] {observer.__class__.__name__}: {e}")
