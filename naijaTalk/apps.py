from django.apps import AppConfig

class NaijatalkConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'naijaTalk'

    def ready(self):
        import naijaTalk.signals