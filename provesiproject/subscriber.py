#!/usr/bin/env python3
import pika
import json
import sys, os, django

# ===== Configuración RabbitMQ =====
rabbit_host = '172.31.25.2'   # <-- cámbialo por la IP/DNS de tu broker
rabbit_user = 'monitoring_user'
rabbit_password = 'isis2503'
exchange = 'monitoring_transactions'
topics = ['Pagos.Aprobado']

# ===== Configuración Django =====
# Ruta al directorio donde está manage.py
sys.path.append('/home/ubuntu/Arquisfot-ProyectoProvesi-Grupo3/provesiproject')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'provesiproject.settings')
django.setup()

# Importar modelos de Django
from wms.models import Pedido

# ===== Conexión RabbitMQ =====
connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host=rabbit_host,
        credentials=pika.PlainCredentials(rabbit_user, rabbit_password)
    )
)
channel = connection.channel()

# Declarar exchange y cola temporal
channel.exchange_declare(exchange=exchange, exchange_type='topic')
result = channel.queue_declare('', exclusive=True)
queue_name = result.method.queue

# Bind de la cola a los tópicos
for topic in topics:
    channel.queue_bind(exchange=exchange, queue=queue_name, routing_key=topic)

print('[*] Esperando mensajes de pagos aprobados. CTRL+C para salir')

# ===== Callback =====
def callback(ch, method, properties, body):
    try:
        payload = body.decode()
        data = json.loads(payload)

        trans_id = data.get("transaccion_id")
        pedido_id = data.get("pedido_id")
        banco = data.get("banco")
        monto = data.get("monto")

        # Usar 'codigo' como identificador único
        pedido, created = Pedido.objects.get_or_create(
            codigo=pedido_id,
            defaults={"estado": "empacado_x_despachar"}
        )

        if not created:
            pedido.estado = "empacado_x_despachar"
            pedido.save()

        print(f"[x] Pedido {pedido_id} marcado como 'empacado_x_despachar' (Banco {banco}, Monto {monto})")

    except Exception as e:
        print(f"[!] Error procesando mensaje: {e}")

# ===== Consumidor =====
channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

try:
    channel.start_consuming()
except KeyboardInterrupt:
    channel.stop_consuming()
    connection.close()
    print("\n[!] Subscriber detenido limpiamente")
