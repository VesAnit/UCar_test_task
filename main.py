import sqlite3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


# Pydantic для валидации формата входных данных
class UserInput(BaseModel):
    text: str



def init_db():
    """Функция для инициализации базы данных и таблицы"""
    connection = sqlite3.connect('reviews.db')
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            sentiment TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    connection.commit()
    connection.close()


# Словарь, определяющий эмоциональный окрас
sent_dict = {'positive': ["хорош", "люблю"], 'negative': ["плохо", "ненавиж"]}


def sentiment_classification(text: str):
    """Функция для классификации текста на позитивный, негативный или нейтральный"""
    text_lower = text.lower()
    for key, value in sent_dict.items():
        if any(word in text_lower for word in value): 
            return key
    return 'neutral'

# Обращаю внимание, что из задания следует необходимость проверять "словосочетания",
# не очень ясно, что имелось в виду; если нужна логика с "и", то я бы заменила any на all.


# Эндпойнты для классификации отзывов

app = FastAPI()


@app.post('/reviews')
def add_review(user_input: UserInput):
    """Функция-эндпойнт для получения текста, его классификации по эмоциональной окраске и добавления полученного JSON в БД"""
    if not user_input.text:
        raise HTTPException(status_code=400, detail="Добавьте отзыв")

    sentiment = sentiment_classification(user_input.text)
    created_at = datetime.utcnow().isoformat()

    connection = sqlite3.connect('reviews.db')
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO reviews (text, sentiment, created_at) VALUES (?, ?, ?)",
        (user_input.text, sentiment, created_at)
    )
    connection.commit()
    review_id = cursor.lastrowid
    connection.close()

    return {
        'id': review_id,
        'text': user_input.text,
        'sentiment': sentiment,
        'created_at': created_at
    }


@app.get('/reviews')
def get_review(sentiment: Optional[str] = None):
    """Функция-эндпойнт для получения отфильтрованных по типу эмоциональной окраски отзывов"""
    
    connection = sqlite3.connect('reviews.db')
    cursor = connection.cursor()

    review_types = ['positive', 'negative', 'neutral']
    if sentiment:
        if sentiment not in review_types:
            raise HTTPException(status_code=400, detail="В запросе передан невалидный тип отзыва")

        cursor.execute(
            "SELECT id, text, sentiment, created_at FROM reviews WHERE sentiment=?", (sentiment,)
            )
    else:
        cursor.execute("SELECT id, text, sentiment, created_at FROM reviews")
    
    reviews = [{'id': row[0], 'text': row[1], 'sentiment': row[2], 'created_at': row[3]} for row in cursor.fetchall()]

    connection.close()

    return reviews
    


# Локальный запуск
if __name__ == '__main__':
    init_db()
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

# Сваггер доступен через http://0.0.0.0:8000/docs (либо другой порт, если будете менять)























