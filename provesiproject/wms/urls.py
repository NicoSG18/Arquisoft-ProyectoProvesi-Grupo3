from django.urls import path
from .views import PedidosPendientesValidacionView
from wms import views as wms_views

urlpatterns = [
    path('', wms_views.panel_vendedor_view, name='panel_vendedor'),
    path('pedidos/pendientes-validacion/', 
         PedidosPendientesValidacionView.as_view(), 
         name='pedidos_pendientes_api'),
]