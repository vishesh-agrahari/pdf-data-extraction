from django.urls import path
from . import views
urlpatterns = [
       path('scanqr',views.scanQRCode),
       path('delall',views.delAll),
       path('getall',views.getAll)
]