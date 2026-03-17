"""
Эмоция талдау моделі — v3
Модель: j-hartmann/emotion-english-distilroberta-base
Қазақ/Орыс мәтіні -> Ағылшынға аудару -> Модель -> Нәтиже
"""

import re
import numpy as np
from typing import Dict, List, Optional
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification


# ================================================================
# Қазақша -> Ағылшынша аударма сөздігі
# ================================================================
KK_TO_EN = {
    'бақытты': 'happy', 'бақыт': 'happiness', 'қуаныш': 'joy',
    'қуанышты': 'joyful', 'керемет': 'wonderful', 'тамаша': 'great',
    'жақсы': 'good', 'жарайды': 'excellent', 'мақтаныш': 'proud',
    'шаттық': 'cheerful', 'мейірімді': 'kind', 'күлкі': 'laughter',
    'жеңіс': 'victory', 'сәттілік': 'success', 'ләззат': 'pleasure',
    'мұңды': 'sad', 'мұң': 'sadness', 'қайғы': 'grief',
    'жылады': 'cried', 'өкініш': 'regret', 'жалғыз': 'lonely',
    'зар': 'longing', 'жоқтау': 'mourning',
    'ашулы': 'angry', 'ашу': 'anger', 'ызалы': 'irritated',
    'ыза': 'irritation', 'ашуланды': 'got angry', 'реніш': 'offence',
    'дау': 'conflict', 'ұрысты': 'quarreled',
    'қорқыныш': 'fear', 'қорқынышты': 'scary', 'қорықты': 'scared',
    'үрей': 'anxiety', 'үрейлі': 'anxious', 'алаңдады': 'worried',
    'таң қалды': 'surprised', 'таң': 'surprise', 'тосын': 'unexpected',
    'күтпеген': 'unexpected', 'таңқаларлық': 'amazing',
    'жиіркеніш': 'disgust', 'жиіркенді': 'disgusted',
    'ерсі': 'disgusting', 'жек көреді': 'hates', 'ұнамсыз': 'unpleasant',
    'сүйіспеншілік': 'love', 'сүйеді': 'loves', 'сүйді': 'loved',
    'ғашық': 'in love', 'ғашықтық': 'love', 'ынтық': 'passionate',
    'бүгін': 'today', 'мен': 'I', 'өте': 'very', 'және': 'and',
    'бірақ': 'but', 'өйткені': 'because', 'болды': 'was',
    'тұр': 'is', 'жоқ': 'no', 'бар': 'yes', 'кездесіп': 'met',
    'уақыт': 'time', 'өткіздім': 'spent', 'досыммен': 'with friend',
    'күн': 'day',
}

# Орысша -> Ағылшынша аударма сөздігі
RU_TO_EN = {
    'счастье': 'happiness', 'счастливый': 'happy', 'радость': 'joy',
    'радостный': 'joyful', 'замечательно': 'wonderful', 'прекрасно': 'great',
    'отлично': 'excellent', 'хорошо': 'good', 'восторг': 'delight',
    'ура': 'hurray', 'улыбка': 'smile', 'смех': 'laughter',
    'победа': 'victory', 'успех': 'success',
    'грусть': 'sadness', 'грустный': 'sad', 'печаль': 'sorrow',
    'плакал': 'cried', 'слеза': 'tear', 'тоска': 'longing',
    'одинокий': 'lonely', 'горе': 'grief', 'сожаление': 'regret',
    'злой': 'angry', 'злость': 'anger', 'гнев': 'rage',
    'раздражение': 'irritation', 'обида': 'offence',
    'ненависть': 'hatred', 'конфликт': 'conflict', 'ярость': 'fury',
    'страх': 'fear', 'страшный': 'scary', 'испугался': 'scared',
    'тревога': 'anxiety', 'паника': 'panic', 'ужас': 'horror',
    'удивление': 'surprise', 'удивился': 'surprised',
    'неожиданный': 'unexpected', 'изумление': 'amazement',
    'отвращение': 'disgust', 'отвратительный': 'disgusting',
    'ненавидит': 'hates', 'неприятный': 'unpleasant', 'мерзкий': 'nasty',
    'любовь': 'love', 'люблю': 'love', 'влюблённый': 'in love',
    'нравится': 'like', 'обожаю': 'adore', 'нежность': 'tenderness',
    'сегодня': 'today', 'очень': 'very', 'замечательный': 'wonderful',
    'встретился': 'met', 'провел': 'spent', 'другом': 'friend',
    'день': 'day', 'я': 'I', 'но': 'but',
}

# Эмоция сәйкестендіру: ағылшын моделі -> қазақ/орыс атаулары
# j-hartmann моделі: anger, disgust, fear, joy, neutral, sadness, surprise
EN_MODEL_TO_APP = {
    'anger':   'гнев',
    'disgust': 'отвращение',
    'fear':    'страх',
    'joy':     'радость',
    'neutral': 'нейтральный',
    'sadness': 'грусть',
    'surprise':'удивление',
}


class EmotionAnalyzer:
    """Эмоция талдау класы — j-hartmann моделі негізінде"""

    EMOTIONS = {
        'радость':     {'emoji': '😊', 'color': '#FFD93D', 'name_kk': 'Қуаныш',     'name_ru': 'Радость'},
        'грусть':      {'emoji': '😢', 'color': '#6B7AA1', 'name_kk': 'Мұң',        'name_ru': 'Грусть'},
        'гнев':        {'emoji': '😠', 'color': '#E74C3C', 'name_kk': 'Ашу',        'name_ru': 'Гнев'},
        'страх':       {'emoji': '😨', 'color': '#9B59B6', 'name_kk': 'Қорқыныш',   'name_ru': 'Страх'},
        'удивление':   {'emoji': '😲', 'color': '#3498DB', 'name_kk': 'Таң қалу',   'name_ru': 'Удивление'},
        'отвращение':  {'emoji': '🤢', 'color': '#2ECC71', 'name_kk': 'Жиіркеніш', 'name_ru': 'Отвращение'},
        'нейтральный': {'emoji': '😐', 'color': '#95A5A6', 'name_kk': 'Бейтарап',   'name_ru': 'Нейтральный'},
        'любовь':      {'emoji': '❤️', 'color': '#E91E63', 'name_kk': 'Махаббат',   'name_ru': 'Любовь'},
    }

    CONFIDENCE_THRESHOLD = 0.25

    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.model_loaded = False
        self.max_length = 512
        self._load_model()

    def _load_model(self):
        try:
            model_name = "j-hartmann/emotion-english-distilroberta-base"
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
            self.model.eval()
            # Модельдің нақты label тізбесін аламыз
            if hasattr(self.model.config, 'id2label'):
                self.id2label = {int(k): v for k, v in self.model.config.id2label.items()}
            else:
                self.id2label = {0:'anger',1:'disgust',2:'fear',3:'joy',4:'neutral',5:'sadness',6:'surprise'}
            self.model_loaded = True
            print(f"Модель жүктелді: {model_name}")
            print(f"Эмоциялар: {list(self.id2label.values())}")
        except Exception as e:
            print(f"Модельді жүктеу қатесі: {e}")
            self.model_loaded = False

    def detect_language(self, text: str) -> str:
        kazakh_specific = set('әіңғүұқөһӘІҢҒҮҰҚӨҺ')
        cyrillic = set('абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ')
        chars = set(text)
        if chars & kazakh_specific:
            return 'kk'
        elif chars & cyrillic:
            return 'ru'
        return 'ru'

    def translate_to_en(self, text: str, lang: str) -> str:
        """Қазақ/Орыс мәтінін ағылшынға аудару"""
        result = text.lower()
        dictionary = KK_TO_EN if lang == 'kk' else RU_TO_EN
        # Ұзын фразаларды алдымен ауыстыру
        for src, tgt in sorted(dictionary.items(), key=lambda x: -len(x[0])):
            result = result.replace(src, tgt)
        return result

    def split_into_sentences(self, text: str, lang: str = 'ru') -> List[str]:
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]

    def chunk_text(self, text: str, max_tokens: int = 500) -> List[str]:
        if not self.tokenizer:
            return [text[:2000]]
        tokens = self.tokenizer.encode(text, add_special_tokens=False)
        if len(tokens) <= max_tokens:
            return [text]
        chunks, current_chunk, current_tokens = [], "", 0
        for sentence in self.split_into_sentences(text):
            sent_tokens = len(self.tokenizer.encode(sentence, add_special_tokens=False))
            if current_tokens + sent_tokens > max_tokens:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk, current_tokens = sentence, sent_tokens
            else:
                current_chunk += " " + sentence
                current_tokens += sent_tokens
        if current_chunk:
            chunks.append(current_chunk.strip())
        return chunks if chunks else [text[:2000]]

    def predict(self, text: str, lang: str = 'auto') -> Dict:
        if not text or not text.strip():
            return self._get_default_result()

        if lang == 'auto':
            lang = self.detect_language(text)

        if not self.model_loaded or self.model is None:
            return self._get_mock_result(text, lang)

        try:
            # Ағылшынға аудару
            text_en = self.translate_to_en(text, lang)

            chunks = self.chunk_text(text_en, self.max_length - 10)
            all_probabilities = []

            for chunk in chunks:
                chunk_result = self._analyze_chunk(chunk)
                all_probabilities.append(chunk_result['probabilities'])

            # Сөйлем деңгейінде талдау
            orig_sentences = self.split_into_sentences(text, lang)
            en_sentences = self.split_into_sentences(text_en, lang)
            sentence_results = []
            for orig, en_sent in zip(orig_sentences[:10], en_sentences[:10]):
                sent_result = self._analyze_chunk(en_sent)
                sentence_results.append({
                    'text': orig,
                    'emotion': sent_result['primary_emotion'],
                    'confidence': sent_result['confidence'],
                    'emoji': self.EMOTIONS.get(sent_result['primary_emotion'], {}).get('emoji', '😐')
                })

            avg_probs = self._aggregate_probabilities(all_probabilities)
            primary_emotion = max(avg_probs, key=avg_probs.get)
            confidence = avg_probs[primary_emotion]

            if confidence < self.CONFIDENCE_THRESHOLD:
                primary_emotion = 'нейтральный'
                confidence = avg_probs.get('нейтральный', confidence)

            return {
                'primary_emotion': primary_emotion,
                'confidence': confidence,
                'probabilities': avg_probs,
                'sentence_results': sentence_results[:10],
                'language': lang,
                'sentence_count': len(orig_sentences)
            }

        except Exception as e:
            print(f"Талдау қатесі: {e}")
            return self._get_mock_result(text, lang)

    def _analyze_chunk(self, text: str) -> Dict:
        """Ағылшын мәтін бөлігін талдау"""
        try:
            inputs = self.tokenizer(
                text, return_tensors="pt",
                truncation=True, max_length=self.max_length, padding=True
            )
            with torch.no_grad():
                outputs = self.model(**inputs)
                probs = torch.softmax(outputs.logits, dim=1)

            probabilities = probs[0].numpy()

            # Модель эмоцияларын (ағылшын) қосымша эмоцияларға (орыс/қазақ) сәйкестендіру
            prob_dict = {}
            for i, prob in enumerate(probabilities):
                en_label = self.id2label.get(i, f'unknown_{i}')
                app_label = EN_MODEL_TO_APP.get(en_label, en_label)
                if app_label in prob_dict:
                    prob_dict[app_label] += float(prob)
                else:
                    prob_dict[app_label] = float(prob)

            # 'любовь' — joy жоғары болса, оны ескереміз
            joy_val = prob_dict.get('радость', 0.0)
            love_score = joy_val * 0.20
            scale = 1.0 - love_score
            prob_dict = {k: v * scale for k, v in prob_dict.items()}
            prob_dict['любовь'] = love_score

            # Нормализация
            total = sum(prob_dict.values())
            if total > 0:
                prob_dict = {k: v / total for k, v in prob_dict.items()}

            # Барлық 8 эмоция болуын қамтамасыз ету
            for emotion in self.EMOTIONS:
                if emotion not in prob_dict:
                    prob_dict[emotion] = 0.0

            primary_emotion = max(prob_dict, key=prob_dict.get)
            return {
                'primary_emotion': primary_emotion,
                'confidence': prob_dict[primary_emotion],
                'probabilities': prob_dict
            }

        except Exception as e:
            print(f"Бөлік талдау қатесі: {e}")
            return {
                'primary_emotion': 'нейтральный',
                'confidence': 1.0 / len(self.EMOTIONS),
                'probabilities': self._get_default_probabilities()
            }

    def _aggregate_probabilities(self, probabilities_list: List[Dict]) -> Dict:
        if not probabilities_list:
            return self._get_default_probabilities()
        all_emotions = set()
        for probs in probabilities_list:
            all_emotions.update(probs.keys())
        result = {
            e: float(np.mean([p.get(e, 0.0) for p in probabilities_list]))
            for e in all_emotions
        }
        total = sum(result.values())
        if total > 0:
            result = {k: v / total for k, v in result.items()}
        return result

    def _get_mock_result(self, text: str, lang: str) -> Dict:
        """Модель жоқ кезде эвристика"""
        text_lower = text.lower()
        kk_words = {
            'радость':    ['бақыт','қуаныш','шаттық','тамаша','керемет','жақсы','жеңіс','сәттілік'],
            'грусть':     ['мұң','қайғы','жылады','өкініш','жалғыз','зар'],
            'гнев':       ['ашу','ыза','реніш','дау','ашулы','ашуланды'],
            'страх':      ['қорқыныш','үрей','алаң','үрейлі','қорықты'],
            'удивление':  ['таң','тосын','күтпеген','таңқаларлық'],
            'отвращение': ['жиіркеніш','ерсі','жек'],
            'нейтральный':[],
            'любовь':     ['сүйіспеншілік','ғашық','ынтық','сүйді'],
        }
        ru_words = {
            'радость':    ['счастье','радость','веселье','замечательно','прекрасно','отлично','хорошо','победа'],
            'грусть':     ['грусть','печаль','плакал','тоска','одинокий','горе'],
            'гнев':       ['злой','злость','гнев','раздражение','обида','ярость'],
            'страх':      ['страх','испугался','тревога','паника','ужас'],
            'удивление':  ['удивление','удивился','неожиданный','изумление'],
            'отвращение': ['отвращение','отвратительный','мерзкий'],
            'нейтральный':[],
            'любовь':     ['любовь','люблю','влюблённый','нравится','обожаю'],
        }
        word_list = kk_words if lang == 'kk' else ru_words
        scores = {e: 0 for e in self.EMOTIONS}
        for emotion, words in word_list.items():
            for word in words:
                if word in text_lower:
                    scores[emotion] += 1
        max_score = max(scores.values())
        if max_score == 0:
            primary, confidence = 'нейтральный', 0.55
        else:
            primary = max(scores, key=scores.get)
            confidence = min(0.50 + max_score * 0.10, 0.88)

        probabilities = self._get_default_probabilities()
        remaining = 1.0 - confidence
        others = [e for e in probabilities if e != primary]
        probabilities[primary] = confidence
        for e in others:
            probabilities[e] = remaining / len(others)

        sentences = self.split_into_sentences(text, lang)
        return {
            'primary_emotion': primary,
            'confidence': confidence,
            'probabilities': probabilities,
            'sentence_results': [
                {'text': s, 'emotion': primary,
                 'confidence': round(confidence * 0.9, 3),
                 'emoji': self.EMOTIONS.get(primary, {}).get('emoji', '😐')}
                for s in sentences[:5]
            ],
            'language': lang,
            'sentence_count': len(sentences)
        }

    def _get_default_result(self) -> Dict:
        return {
            'primary_emotion': 'нейтральный', 'confidence': 0.0,
            'probabilities': self._get_default_probabilities(),
            'sentence_results': [], 'language': 'ru', 'sentence_count': 0
        }

    def _get_default_probabilities(self) -> Dict:
        eq = 1.0 / len(self.EMOTIONS)
        return {e: eq for e in self.EMOTIONS}

    def get_emotion_info(self, emotion_key: str, lang: str = 'ru') -> Dict:
        ed = self.EMOTIONS.get(emotion_key, self.EMOTIONS['нейтральный'])
        return {
            'key': emotion_key, 'emoji': ed['emoji'], 'color': ed['color'],
            'name': ed['name_kk'] if lang == 'kk' else ed['name_ru']
        }


_emotion_analyzer: Optional[EmotionAnalyzer] = None


def get_emotion_analyzer() -> EmotionAnalyzer:
    global _emotion_analyzer
    if _emotion_analyzer is None:
        _emotion_analyzer = EmotionAnalyzer()
    return _emotion_analyzer