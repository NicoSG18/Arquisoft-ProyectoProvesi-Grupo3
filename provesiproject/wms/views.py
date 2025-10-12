
from django.core.cache import cache # Importamos el sistema de cache de Django
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Pedido
from .serializers import PedidoConTransaccionesSerializer
import time # Para medir el tiempo de ejecución
from django.shortcuts import render



 # Vista para renderizar la página HTML del frontend.
def panel_vendedor_view(request):
    # Simplemente le dice a Django que busque y devuelva el archivo index.html.
    return render(request, 'wms/index.html')
# ---------------------------------------------------------------------------
# Vista para obtener pedidos pendientes de validación de pago.
# Esta es la implementación directa del ASR de latencia.
# ---------------------------------------------------------------------------
class PedidosPendientesValidacionView(APIView):
    def get(self, request, *args, **kwargs):
        # Para la prueba, medimos el tiempo de inicio
        start_time = time.time()

        # --- Táctica de Arquitectura #1: Caching ---
        CACHE_KEY = "por_verificar"
        datos_en_cache = cache.get(CACHE_KEY)
        
        if datos_en_cache:
            # Si los datos están en cache, los retornamos inmediatamente
            # y añadimos una cabecera para saber que vino de la cache.
            response = Response(datos_en_cache)
            response['X-DataSource'] = 'Cache'
            return response

        # --- Táctica de Arquitectura #2: Optimización de Consulta ---
        # Si no hay nada en cache, hacemos la consulta a la BD.
        # 1. Filtramos los pedidos en el estado correcto.
        # 2. Usamos prefetch_related para traer todas las transacciones asociadas en UNA sola consulta adicional.
        #    Esto evita el problema "N+1" y es crucial para el rendimiento.
        pedidos = Pedido.objects.filter(
            estado='por_verificar'
        ).prefetch_related('transacciones')

        # Usamos el serializer para convertir los datos a JSON
        serializer = PedidoConTransaccionesSerializer(pedidos, many=True)
        
        # Guardamos el resultado en cache para la próxima vez (ej: por 60 segundos)
        cache.set(CACHE_KEY, serializer.data, timeout=60)
        
        # Calculamos el tiempo de ejecución para la prueba
        end_time = time.time()
        execution_time = (end_time - start_time) * 1000 # en milisegundos

        # Devolvemos la respuesta y añadimos una cabecera con el tiempo
        response = Response(serializer.data)
        response['X-DataSource'] = 'Database'
        response['X-Execution-Time-ms'] = f"{execution_time:.2f}"
        
        return response
    
 
