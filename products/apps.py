from django.apps import AppConfig
from django.db.models.signals import post_migrate

def create_default_superuser(sender, **kwargs):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    # Agar bazada ushbu loginli admin bo'lmasa, uni avtomatik yaratadi
    if not User.objects.filter(username='CoolAdmin').exists():
        User.objects.create_superuser('CoolAdmin', 'admin@puffshop.com', 'daisy57jax@')
        print("====== JONLI ADMIN AKKAUNTI AVTOMATIK YARATDI! ======")

class ProductsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'products'

    def ready(self):
        # Migratsiya tugashi bilanoq yuqoridagi funksiyani ishga tushiradi
        post_migrate.connect(create_default_superuser, sender=self)
