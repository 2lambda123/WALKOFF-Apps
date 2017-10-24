import logging
from core.decorators import *
from apps.appcache import AppCache

_logger = logging.getLogger(__name__)


class App(object):
    """
    Base class for apps
    """

    _is_walkoff_app = True

    def __init__(self, app, device):
        from server.appdevice import get_app
        self.app = get_app(app)
        self.device = self.app.get_device(device) if self.app is not None else None
        if self.device is not None:
            self.device_fields = self.device.get_plaintext_fields()
            self.device_type = self.device.type
        else:
            self.device_fields = {}
            self.device_type = None
        self.device_id = device

    def get_all_devices(self):
        """ Gets all the devices associated with this app """
        return list(self.app.devices) if self.app is not None else []

    def shutdown(self):
        """ When implemented, this method performs shutdown procedures for the app """
        pass


_cache = AppCache()


def get_app(app_name):
    """
    Gets the app class for a given app from the global cache. If app has only global actions or is not found,
    raises an UnknownApp exception.

    Args:
        app_name (str): Name of the app to get

    Returns:
        (cls) The app's class
    """
    return _cache.get_app(app_name)


def get_all_actions_for_app(app_name):
    """
    Gets all the names of the actions for a given app from the global cache

    Args:
        app_name (str): Name of the app

    Returns:
        (list[str]): The actions associated with the app
    """
    return _cache.get_app_action_names(app_name)


def get_app_action(app_name, action_name):
    """
    Gets the action function for a given app and action name from the global cache

    Args:
        app_name (str): Name of the app
        action_name(str): Name of the action

    Returns:
        (func) The action
    """
    return _cache.get_app_action(app_name, action_name)


def cache_apps(path):
    """
    Cache apps from a given path into the global cache

    Args:
        path (str): Path to apps module
    """
    _cache.cache_apps(path)


def clear_cache():
    """
    Clears the global cache
    """
    _cache.clear()


def is_app_action_bound(app_name, action_name):
    """
    Determines if the action in the global cache is bound (meaning it's inside a class) or not

    Args:
        app_name (str): Name of the app
        action_name(str): Name of the action

    Returns:
        (bool) Is the action bound?
    """
    return _cache.is_app_action_bound(app_name, action_name)


class AppWidgetBlueprint(object):
    """
    Class to create blueprints for custom server endpoints in apps
    """
    def __init__(self, blueprint, rule=''):
        self.blueprint = blueprint
        self.rule = rule

AppBlueprint = AppWidgetBlueprint
WidgetBlueprint = AppWidgetBlueprint


class Event(object):
    """
    Encapsulated an asynchronous event.

    Attributes:
        name (str, optional): Name of the event. Defaults to ''
        receivers (set{func}): Set of functions waiting on the event
    """
    def __init__(self, name=''):
        """
        Constructor

        Args:
             name (str, optional): Name of the Event. Defaults to ''
        """
        self.name = name
        self.receivers = set()

    def connect(self, func):
        """
        Connects a function to the event as a callback

        Args:
            func (func): Function to register as a callback
        Returns:
            (func): The unmodified function
        """
        self.receivers.add(func)
        return func

    def disconnect(self, func):
        """
        Disconnects a function

        Args:
            func (func): The function to disconnect
        """
        try:
            self.receivers.remove(func)
        except KeyError:
            pass

    def trigger(self, data):
        """
        Triggers an event and calls all the functions with the data provided

        Args:
            data: Data to send to all the callbacks registered to this event

        """
        for func in self.receivers:
            func(data)
