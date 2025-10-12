# en wms/management/commands/seed_db.py

import random
from datetime import timedelta
from django.utils import timezone  # Usar timezone de Django es mejor práctica
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from wms.models import Pedido, TransaccionBancaria, Colaborador
from faker import Faker # Importamos Faker

BANCOS = ["Bancolombia", "Davivienda", "BBVA", "Banco de Bogotá", "Nequi", "Daviplata"]
TOTAL_PEDIDOS = 400

class Command(BaseCommand):
    help = f'Crea {TOTAL_PEDIDOS} pedidos de prueba realistas en la base de datos.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Iniciando el proceso de población de la base de datos...'))
        
        self.fake = Faker('es_CO') # Inicializamos Faker para español/Colombia
        
        self._limpiar_datos_antiguos()
        self._crear_colaboradores()
        pedidos = self._crear_pedidos()
        self._crear_transacciones(pedidos)

        self.stdout.write(self.style.SUCCESS('¡Base de datos poblada exitosamente!'))

    def _limpiar_datos_antiguos(self):
        self.stdout.write('Limpiando datos antiguos...')
        TransaccionBancaria.objects.all().delete()
        Pedido.objects.all().delete()
        Colaborador.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()

    def _crear_colaboradores(self):
        self.stdout.write('Creando colaboradores de prueba...')
        vendedor_user, _ = User.objects.get_or_create(username='vendedor_test', first_name='Vendedor', last_name='Prueba')
        Colaborador.objects.create(usuario=vendedor_user, rol='vendedor')

    def _crear_pedidos(self):
        self.stdout.write(f'Creando {TOTAL_PEDIDOS} pedidos de prueba...')
        lista_pedidos = []
        for i in range(TOTAL_PEDIDOS):
            pedido = Pedido(
                codigo=f'PED-TEST-{i:05d}',
                # --- CORRECCIÓN CRÍTICA ---
                # El estado debe coincidir con el que la vista va a filtrar.
                estado='por_verificar', 
            )
            lista_pedidos.append(pedido)
        
        Pedido.objects.bulk_create(lista_pedidos)
        return Pedido.objects.all()

    def _crear_transacciones(self, pedidos):
        self.stdout.write('Asociando transacciones a los pedidos...')
        lista_transacciones = []
        for pedido in pedidos:
            num_transacciones = random.randint(1, 2)
            for _ in range(num_transacciones):
                transaccion = TransaccionBancaria(
                    pedido=pedido,
                    monto=random.uniform(20000, 500000),
                    # --- MEJORA: Fechas más realistas ---
                    # Crea fechas aleatorias en los últimos 7 días
                    fecha_transaccion=self.fake.date_time_between(start_date='-7d', end_date='now', tzinfo=timezone.get_current_timezone()),
                    banco_origen=random.choice(BANCOS),
                    validada=False
                )
                lista_transacciones.append(transaccion)
        
        TransaccionBancaria.objects.bulk_create(lista_transacciones)