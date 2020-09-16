from abc import abstractmethod
from aat.core.handler import EventHandler


class ManagerBase(EventHandler):
    @abstractmethod
    def _setManager(self, mgr):
        '''set the root manager'''
