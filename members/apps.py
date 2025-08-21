from django.apps import AppConfig

class MembersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'members'

    def ready(self):
        # Import signals to connect them
        import members.signals  # noqa
