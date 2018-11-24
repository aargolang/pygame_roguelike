# event module

class Event(object):
    def __init__(self, doc):
        self.__doc__ = doc
        self.subscribers = []

    def __iadd__(self, subscriber):
        self.subscribers.append(subscriber)
        return self

    def __isub__(self, subscriber):
        self.subscribers.remove(subscriber)
        return self      

    def __call__(self, sender, eventArgs=None):
        for function in self.subscribers:
            function(sender,eventArgs)