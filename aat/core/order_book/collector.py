from collections import deque


class _Collector(object):
    def __init__(self, callback):
        self._callback = callback
        self._event_queue = deque()

    def setCallback(self, callback):
        self._callback = callback

    def push(self, event):
        '''push event to queue'''
        self._event_queue.append(event)

    def flush(self):
        '''flush the event queue'''
        while self._event_queue:
            ev = self._event_queue.popleft()
            self._callback(ev)

    def clear(self):
        '''clear the event queue'''
        self._event_queue.clear()
