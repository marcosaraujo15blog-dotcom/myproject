from django.apps import AppConfig


class TransportesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'transportes'
    verbose_name = 'Transportes'

    def ready(self):
        import transportes.signals  # noqa
