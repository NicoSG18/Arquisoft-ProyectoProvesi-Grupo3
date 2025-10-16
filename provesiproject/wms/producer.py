import pika
import json

RABBIT_HOST = "host"  # Modificar: IP de la instancia RabbitMQ
RABBIT_USER = "monitoring_user"
RABBIT_PASSWORD = "isis2503"
EXCHANGE = "orders_exchange"
ROUTING_KEY = "orders.confirmed"

def send_order_confirmed(order_data):
    """Publica un mensaje al exchange de RabbitMQ cuando una orden se confirma"""
    credentials = pika.PlainCredentials(RABBIT_USER, RABBIT_PASSWORD)
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=RABBIT_HOST, credentials=credentials)
    )
    channel = connection.channel()

    # Declarar el exchange tipo 'topic' (si no existe, se crea automáticamente)
    channel.exchange_declare(exchange=EXCHANGE, exchange_type='topic')

    # Convertir el diccionario a JSON
    message = json.dumps(order_data)

    # Publicar el mensaje
    channel.basic_publish(exchange=EXCHANGE, routing_key=ROUTING_KEY, body=message)

    print(f"[x] Sent order confirmation message: {message}")

    connection.close()
