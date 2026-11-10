from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission, User

class Command(BaseCommand):
    help = 'Crea el grupo Creadores y asigna roles solamente a los usuarios indicados.'

    def add_arguments(self, parser):
        parser.add_argument('--creador', action='append', default=[])
        parser.add_argument('--administrador', action='append', default=[])

    def handle(self, *args, **options):
        grupo, _ = Group.objects.get_or_create(name='Creadores')
        grupo.permissions.add(*Permission.objects.filter(content_type__app_label='portfolio', codename__in=['add_curso', 'add_area']))
        for username in options['creador']:
            User.objects.get(username=username).groups.add(grupo)
        for username in options['administrador']:
            usuario = User.objects.get(username=username)
            usuario.is_staff = True
            usuario.is_superuser = True
            usuario.is_active = True
            usuario.save(update_fields=['is_staff', 'is_superuser', 'is_active'])
        self.stdout.write(self.style.SUCCESS('Roles configurados. Las contraseñas no se modificaron.'))
