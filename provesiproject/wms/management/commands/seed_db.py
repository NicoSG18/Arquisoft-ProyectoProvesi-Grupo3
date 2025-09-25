
import random
from datetime import datetime
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from wms.models import Pedido, TransaccionBancaria, Colaborador

# Se define una lista de bancos para usar en los datos de prueba.
BANCOS = ["Bancolombia", "Davivienda", "BBVA", "Banco de Bogotá", "Nequi"]
TOTAL_PEDIDOS = 200 # Cantidad de pedidos a crear.

class Command(BaseCommand):
    help = f'Crea datos de prueba en la base de datos, incluyendo {TOTAL_PEDIDOS} pedidos.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Iniciando el proceso de población de la base de datos...'))

        
        self.stdout.write('Limpiando datos antiguos...')
        TransaccionBancaria.objects.all().delete()
        Pedido.objects.all().delete()
        Colaborador.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()

        
        self.stdout.write('Creando colaboradores...')
        vendedor_user, _ = User.objects.get_or_create(username='vendedor_test', first_name='Vendedor', last_name='Prueba')
        Colaborador.objects.create(usuario=vendedor_user, rol='vendedor')

        
        self.stdout.write(f'Creando {TOTAL_PEDIDOS} pedidos de prueba...')
        
        lista_pedidos = []
        for i in range(TOTAL_PEDIDOS):
            pedido = Pedido(
                # Se usa un formato de código para que sea único.
                codigo=f'PED-TEST-{i:05d}',
                # El estado es el que la vista va a filtrar.
                estado='empacado_x_despachar',
            )
            lista_pedidos.append(pedido)

    
        Pedido.objects.bulk_create(lista_pedidos)

        
        self.stdout.write('Asociando transacciones a los pedidos...')
        pedidos_creados = Pedido.objects.all()
        lista_transacciones = []

        for pedido in pedidos_creados:
            # A cada pedido se le asocia una o dos transacciones.
            num_transacciones = random.randint(1, 2)
            for _ in range(num_transacciones):
                transaccion = TransaccionBancaria(
                    pedido=pedido,
                    monto=random.uniform(20000, 500000),
                    fecha_transaccion=datetime.now(),
                    banco_origen=random.choice(BANCOS),
                    validada=False # Importante para el escenario de prueba.
                )
                lista_transacciones.append(transaccion)

        # Se usa bulk_create de nuevo para la máxima eficiencia.
        TransaccionBancaria.objects.bulk_create(lista_transacciones)

        self.stdout.write(self.style.SUCCESS('Base de datos poblada exitosamente'))
