import collections


class _Symbol(object):
    """ Simulates Lisp-like symbols.

    Symbols are appropriate to use in cases where a (global) constant is
    assigned a numeric value, without any real semantics.  The module contains
    any symbol, and is only equal to itself.  Symbols can also be accessed by
    its string name.  Besides that, they can also be clustered in namespaces.

    Some examples of using this module:
        >>> import symbols
        >>> Symbol.Foo is Symbol.Bar
        False
        >>> Symbol.Foo is Symbol.Foo
        True
        >>> Symbol["Foo"] is Symbol.Foo
        True
        >>> Symbol.Foo.Bar.Foo is Symbol.Foo
        False
        >>> Symbol.Foo.Bar.Foo is Symbol["Foo"]["Bar"]["Foo"]
        True
        >>> 

    Original code written by Simon Wittber and available at
        http://entitycrisis.blogspot.nl/2009/12/symbols-in-python_01.html
    """
    def __init__(self, name):
        self.name = name
        self._symbols = {}

    def __repr__(self):
        return "<SYM %s>" % (self.name)

    def __getattr__(self, name):
        s = self._symbols[name] = self.__class__(name)
        self.__dict__[name] = s 
        return s

    def __getitem__(self, name):
        return getattr(self, name)


Symbol = _Symbol("Root")


class Observable(object):
    """ Registers and de-registers callbacks.  Only calls back on given events.

    Only callbacks which are defined to listen for an event in events will be
    notified.  If events is Symbol.ANY_EVENT, all callbacks will be notified.
    If a callback listens for Symbol.ANY_EVENT, it will be notified with any
    event.
    """
    def __init__(self, callback_args=tuple()):
        self.__callbacks = collections.defaultdict(set)
        self.__callback_args = callback_args

    def subscribe(self, callback, events):
        """ Keep a callback function in memory to be notified of events.
        """
        try:
            for event in events:
                self.__callbacks[event].add(callback)
        except TypeError:
            # Single event
            return self.subscribe(callback, [events])

    def unsubscribe(self, callback, events):
        """ Stop notifying callbacks when some events occur.
        """
        try:
            if events is Symbol.ANY_EVENT:
                events = self.__callbacks.keys()
            for event in events:
                if callback in self.__callbacks[event]:
                    self.__callbacks[event].remove(callback)
        except:
            # Single event
            return self.unsubscribe(callback, [events])

    def raise_events(self, events):
        """ Notify all callbacks registered for the given events.
        """
        return_values = collections.defaultdict(set)
        try:
            if events is Symbol.ANY_EVENT:
                events = self.__callbacks.keys()
            else:
                events.append(Symbol.ANY_EVENT)

            for event in events:
                for callback in self.__callbacks[event]:
                    args = map(lambda x: getattr(self, x), self.__callback_args)
                    try:
                        return_values[event, callback] = callback(*args)
                    except:
                        # Ignore errors
                        pass
        except TypeError:
            # Single event
            events = [events]
            return self.raise_events(self, events)
        return return_values
