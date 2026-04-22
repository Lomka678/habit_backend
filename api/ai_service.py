from google import genai
from django.conf import settings

# Инициализируем клиент новым способом
client = genai.Client(api_key=settings.GEMINI_API_KEY)


def generate_smart_advice(habits_data):
    """
    Эта функция принимает список привычек пользователя и просит ИИ дать совет.
    """
    # Формируем системный промпт (инструкцию для ИИ)
    prompt = f"""
    Ты - профессиональный и эмпатичный AI-наставник по продуктивности.
    Пользователь ведет трекер привычек. Вот список его привычек: {habits_data}.

    Проанализируй их и дай один короткий, дружелюбный и мотивирующий совет на 2-3 предложения. 
    Обращайся к пользователю на "ты". Не используй сложные термины.
    """

    try:
        # В новой библиотеке запрос отправляется так.
        # Используем актуальную модель gemini-2.5-flash
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        return response.text
    except Exception as e:
        print(f"Ошибка ИИ: {e}")
        return "Нейросеть пока отдыхает, но ты всё равно молодец! Продолжай в том же духе."