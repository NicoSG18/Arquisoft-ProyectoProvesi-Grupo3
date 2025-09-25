# en tu_app/serializers.py
from rest_framework import serializers
from .models import Pedido, TransaccionBancaria

# ---------------------------------------------------------------------------
# Serializer para el modelo TransaccionBancaria
# Define qué campos de la transacción se enviarán en el JSON.
# ---------------------------------------------------------------------------
class TransaccionBancariaSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransaccionBancaria
        # Lista de campos del modelo que queremos mostrar.
        fields = ['id', 'monto', 'fecha_transaccion', 'banco_origen', 'validada']

# ---------------------------------------------------------------------------
# Serializer para el modelo Pedido (incluyendo sus transacciones)
# Este es el serializer principal para nuestra vista.
# ---------------------------------------------------------------------------
class PedidoConTransaccionesSerializer(serializers.ModelSerializer):
    
    transacciones = TransaccionBancariaSerializer(many=True, read_only=True)

    class Meta:
        model = Pedido
        fields = ['id', 'codigo', 'estado', 'fecha_creacion', 'transacciones']