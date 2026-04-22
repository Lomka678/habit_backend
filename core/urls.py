from django.contrib import admin
from django.urls import path, include # Не забудь добавить include сюда!

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')), # Все запросы, начинающиеся с /api/, пойдут в наше приложение
]