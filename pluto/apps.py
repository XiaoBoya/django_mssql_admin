from django.apps import AppConfig


class PlutoConfig(AppConfig):
    name = 'pluto'

    def ready(self):
        from django.utils.module_loading import autodiscover_modules
        autodiscover_modules('pluto')