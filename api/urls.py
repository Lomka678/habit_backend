from django.urls import path, include
from rest_framework.routers import DefaultRouter

# ИСПРАВЛЕНИЕ: Обязательно импортируем get_ai_advice

from .views import HabitViewSet, HabitCompletionViewSet, PlanViewSet, google_login, get_ai_advice

router = DefaultRouter()
router.register(r'habits', HabitViewSet, basename='habit')
router.register(r'completions', HabitCompletionViewSet, basename='completion')
router.register(r'plans', PlanViewSet, basename='plan') # <--- НОВАЯ СТРОЧКА

urlpatterns = [
    path('', include(router.urls)),
    path('auth/google/', google_login, name='google_login'),

    # --- НОВЫЙ МАРШРУТ ДЛЯ ИИ ---
    path('ai-advice/', get_ai_advice, name='ai_advice'),
]