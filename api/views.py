import datetime
from .models import Habit, HabitCompletion, Plan # <--- Добавили Plan
from .serializers import HabitSerializer, HabitCompletionSerializer, PlanSerializer # <--- И его сериализатор
from django.views.decorators.csrf import csrf_exempt
import google.generativeai as genai
import os
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from .models import Habit, HabitCompletion
from .serializers import HabitSerializer, HabitCompletionSerializer


api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("Ключ ИИ не найден! Проверьте файл .env")

genai.configure(api_key=api_key)

# Твой ID клиента (проверь его в консоли Google)
GOOGLE_CLIENT_ID = "731005291149-g6g1mhln5p3hn90e83ea8tks965efm55.apps.googleusercontent.com"


# --- ЕДИНАЯ И ИСПРАВЛЕННАЯ ФУНКЦИЯ ВХОДА ---
@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def google_login(request):
    token_id = request.data.get('id_token')
    if not token_id:
        return Response({'error': 'Нет токена'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Проверяем токен через Google
        idinfo = id_token.verify_oauth2_token(token_id, google_requests.Request(), GOOGLE_CLIENT_ID)
        email = idinfo['email']

        # Находим или создаем пользователя
        user, _ = User.objects.get_or_create(
            username=email,
            defaults={
                'email': email,
                'first_name': idinfo.get('given_name', ''),
                'last_name': idinfo.get('family_name', '')
            }
        )

        # Создаем или получаем токен для Flutter
        django_token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': django_token.key})

    except ValueError:
        return Response({'error': 'Неверный токен Google'}, status=status.HTTP_400_BAD_REQUEST)


# --- ПОЛУЧЕНИЕ СОВЕТА ИИ ---
GEMINI_API_KEY = "AIzaSyDlryEFoMnB5AvVsdST_iaVL3bNHOfz8RE"
genai.configure(api_key=GEMINI_API_KEY)


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_ai_advice(request):
    name = request.data.get('name', 'Герой')
    bio = request.data.get('bio', '')
    habits = request.data.get('habits_summary', '')

    # --- НОВОЕ ПОЛЕ: Ищем, передал ли Flutter нам важное событие ---
    target_event = request.data.get('target_event', '')

    prompt = f"""
    Ты — продвинутый ИИ-наставник по дисциплине. 
    Твоего подопечного зовут {name}. Контекст, работа и хобби: {bio}.
    Успехи: {habits}
    """

    # Если событие ЕСТЬ, меняем логику Наставника!
    if target_event:
        prompt += f"\nВНИМАНИЕ: У пользователя сегодня/завтра важное событие: «{target_event}». Твоя задача — дать ОЧЕНЬ мощную, короткую мотивацию ИМЕННО для успешного выполнения этого события! Подбодри его в твоем фирменном стиле (используя термины из его профессии/хобби)."
    else:
        prompt += "\nДай один развернутый, мощный и персонализированный совет на сегодня. Используй крутые метафоры по его профилю."

    prompt += "\nОбъем: 3-4 емких предложения. Не пиши банальностей."

    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt)
        response_text = response.text
    except Exception as e:
        response_text = f"Связь с нейросетью прервана. Ошибка: {str(e)}"

    return Response({'advice': response_text})

class HabitViewSet(viewsets.ModelViewSet):
    serializer_class = HabitSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Habit.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def toggle_today(self, request, pk=None):
        habit = self.get_object()
        date_str = request.data.get('date')
        target_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else datetime.date.today()

        completions = HabitCompletion.objects.filter(habit=habit, completed_date=target_date)
        current_count = completions.count()

        if current_count >= habit.target_daily_count:
            completions.delete()
            return Response({'status': 'reset', 'count': 0})
        else:
            HabitCompletion.objects.create(habit=habit, completed_date=target_date)
            return Response({'status': 'added', 'count': current_count + 1})


class HabitCompletionViewSet(viewsets.ModelViewSet):
    serializer_class = HabitCompletionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Возвращаем только отметки текущего пользователя
        return HabitCompletion.objects.filter(habit__user=self.request.user)

class PlanViewSet(viewsets.ModelViewSet):
    serializer_class = PlanSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Отдаем планы текущего юзера, отсортированные по дате
        return Plan.objects.filter(user=self.request.user).order_by('date')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)