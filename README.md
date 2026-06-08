# SPA Comments — Система комментариев

SPA-приложение для написания комментариев с каскадным отображением, сортировкой, пагинацией и real-time обновлением через WebSocket.

## Демо

- **Frontend:** https://dzen-1.onrender.com
- **Backend API:** https://dzen-8t2e.onrender.com/api/comments/

## Стек

- **Backend:** Django, Django ORM, PostgreSQL (Neon), Redis (Upstash), django-channels, daphne
- **Frontend:** Vue 3, Axios
- **Хранилище файлов:** Cloudinary
- **Инфраструктура:** Docker, Docker Compose

## Функционал

- Добавление комментариев с валидацией (username только латиница/цифры, email, captcha)
- Каскадные ответы на комментарии (бесконечная вложенность)
- Сортировка по username, email, дате (по убыванию и возрастанию)
- Пагинация (25 комментариев на страницу), LIFO по умолчанию
- Загрузка изображений JPG/GIF/PNG с автоматическим ресайзом до 320x240
- Загрузка текстовых файлов TXT до 100кб
- Просмотр файлов через Lightbox
- Разрешённые HTML теги: `<a>`, `<code>`, `<i>`, `<strong>` — остальные блокируются
- Панель быстрой вставки тегов
- Предпросмотр сообщения без перезагрузки страницы
- Валидация на стороне клиента и сервера
- Защита от XSS (bleach) и SQL-инъекций (Django ORM)
- Real-time обновление через WebSocket (django-channels + Redis)

## Запуск локально

### Требования

- Python 3.11+
- Node.js 18+
- Redis (Windows: https://github.com/tporadowski/redis/releases)

### Backend

```bash
cd spa
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Создай `.env` в папке `spa/`:

```
SECRET_KEY=your-secret-key
DEBUG=True
DATABASE_URL=postgresql://user:password@localhost:5432/spa_db
REDIS_URL=redis://127.0.0.1:6379
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret
```

```bash
python manage.py migrate
daphne -p 8000 spa.asgi:application
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Создай `frontend/.env.local`:

VITE_API_URL=http://127.0.0.1:8000/api
VITE_WS_URL=ws://127.0.0.1:8000

Фронт будет доступен на `http://localhost:5173`

## Запуск через Docker

```bash
git clone https://github.com/AAAArtteem21/dzen
cd dzen/spa
docker-compose up --build
```


## Схема БД

Table authors {
id integer [primary key]
username varchar
email varchar
home_page varchar
}
Table comments {
id integer [primary key]
author_id integer [ref: > authors.id]
parent_id integer [ref: > comments.id]
text text
file_url varchar
created_at timestamp
}