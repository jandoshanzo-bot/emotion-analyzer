# Emotion AI - Эмоция талдау қосымшасы

🧠 **Emotion AI** - қазақ және орыс тілдеріндегі мәтіндердің эмоционалдық күйін талдайтын заманауи веб-қосымша.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Django](https://img.shields.io/badge/Django-6.0-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

## ✨ Мүмкіндіктер

- 🎯 **8 эмоцияны тану**: қуаныш, мұң, ашу, қорқыныш, таң қалу, жиіркеніш, бейтарап, махаббат
- 🌍 **Екі тілді қолдау**: қазақша және орысша
- 🤖 **AI негізінде**: Transformer/BERT моделі
- 📊 **Визуализация**: интерактивті диаграммалар (Chart.js)
- 📝 **Сөйлем деңгейінде талдау**: әр сөйлемге жеке эмоция
- 📜 **Тарих**: соңғы 20 талдауды сақтау
- 💾 **Экспорт**: PNG/PDF ретінде сақтау
- 🌓 **Dark/Light режим**: тақырыпты ауыстыру
- 📱 **Mobile-first**: мобильді құрылғыларға бейімделген

## 🚀 Орнату және іске қосу

### 1. Қоршамды орнату

```bash
# Виртуалды қоршам жасау

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 2. Тәуелділіктерді орнату

```bash
pip install django transformers torch numpy scikit-learn pandas matplotlib seaborn reportlab pillow
```

### 3. Миграцияларды жасау

```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Суперпайдаланушы жасау

```bash
python manage.py createsuperuser
```

### 5. Серверді іске қосу

```bash
python manage.py runserver
```

Қосымша http://127.0.0.1:8000/ мекенжайында қолжетімді.

## 📁 Жоба құрылымы

```
emotion_analyzer/
├── emotion_analyzer/          # Негізгі Django жоба
│   ├── settings.py            # Параметрлер
│   ├── urls.py                # URL маршруттары
│   └── wsgi.py                # WSGI конфигурациясы
├── analyzer/                   # Негізгі қосымша
│   ├── models.py              # Дерекқор модельдері
│   ├── views.py               # Көріністер
│   ├── urls.py                # URL маршруттары
│   ├── emotion_model.py       # ML моделі
│   ├── admin.py               # Админ панелі
│   └── migrations/            # Миграциялар
├── templates/                  # HTML шаблондар
│   ├── base.html              # Негізгі шаблон
│   └── analyzer/
│       ├── home.html          # Басты бет
│       ├── history.html       # Тарих беті
│       └── about.html         # Модель туралы
├── static/                     # Статикалық файлдар
│   ├── css/style.css          # Стильдер
│   └── js/
│       ├── main.js            # Негізгі JS
│       ├── analyzer.js        # Талдау логикасы
│       └── history.js         # Тарих логикасы
├── manage.py                   # Django басқару скрипті
└── db.sqlite3                  # SQLite дерекқоры
```

## 🔌 API Endpoints

| Endpoint | Method | Сипаттама |
|----------|--------|-----------|
| `/` | GET | Басты бет |
| `/history/` | GET | Тарих беті |
| `/about/` | GET | Модель туралы |
| `/api/predict/` | POST | Мәтінді талдау |
| `/api/feedback/` | POST | Кері байланыс |
| `/api/history/stats/` | GET | Тарих статистикасы |
| `/api/history/delete/<id>/` | DELETE | Жазбаны жою |

### API Пайдалану мысалы

```bash
# Мәтінді талдау
curl -X POST http://127.0.0.1:8000/api/predict/ \
  -H "Content-Type: application/json" \
  -d '{"text": "Бүгін керемет күн!", "lang": "auto"}'
```

**Жауап:**
```json
{
  "success": true,
  "data": {
    "primary_emotion": "радость",
    "confidence": 0.85,
    "probabilities": {
      "радость": 0.85,
      "грусть": 0.05,
      ...
    },
    "sentence_results": [...],
    "language": "kk"
  }
}
```

## 🎨 Интерфейс

### Басты бет
- Үлкен textarea мәтін енгізу үшін
- Тіл таңдау (AUTO / Қазақша / Орысша)
- Символ/сөз санағыш
- "Талдау", "Тазалау", "Демо мәтін" батырмалары

### Нәтиже бөлімі
- Негізгі эмоция карточкасы (эмодзи + пайыз)
- Top-5 эмоциялар тізімі
- Интерактивті диаграммалар (bar + pie)
- Сөйлем деңгейінде талдау
- Сенімділік индикаторы
- Кері байланыс батырмалары

## 🛠️ Технологиялар

- **Backend**: Django 6.0, Python 3.12
- **ML**: Transformers, PyTorch, BERT
- **Frontend**: HTML5, CSS3, JavaScript (vanilla)
- **Диаграммалар**: Chart.js
- **Дерекқор**: SQLite
- **Стили**: CSS Variables, Flexbox, Grid
- **Шрифт**: Inter (Google Fonts)

## ⚙️ Параметрлер

`emotion_analyzer/settings.py` файлында:

```python
# Тіл және уақыт белдеуі
LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Asia/Almaty'

# Модель параметрлері
MAX_TEXT_LENGTH = 10000  # Максималды мәтін ұзындығы
CHUNK_SIZE = 512         # Токен саны бір бөлікке
```

## 📝 Қолданылатын эмоциялар

| Эмоция | Emoji | Түс | Қазақша |
|--------|-------|-----|---------|
| радость | 😊 | #FFD93D | Қуаныш |
| грусть | 😢 | #6B7AA1 | Мұң |
| гнев | 😠 | #E74C3C | Ашу |
| страх | 😨 | #9B59B6 | Қорқыныш |
| удивление | 😲 | #3498DB | Таң қалу |
| отвращение | 🤢 | #2ECC71 | Жиіркеніш |
| нейтральный | 😐 | #95A5A6 | Бейтарап |
| любовь | ❤️ | #E91E63 | Махаббат |

## ⚠️ Шектеулер

- Сарказм және иронияны түсінбеуі мүмкін
- Сленг және диалект сөздерді дұрыс талдамайды
- Аралас тілдегі мәтіндерде қателесуі мүмкін
- 512 токеннен ұзын мәтіндер бөлікке бөлінеді

## 🔒 Құпиялылық

- Мәтіндер сақталмайды, тек талдау уақытында қолданылады
- Тарихта тек мәтіннің алғашқы 200 таңбасы сақталады
- Барлық деректер сессия бойынша бөлінеді

## 📄 Лицензия

MIT License

## 🤝 Үлес қосу

Үлес қосқыңыз келсе, pull request жіберіңіз!

---

**Автор**:   Tabigat jandos
**Жыл**: 2026
