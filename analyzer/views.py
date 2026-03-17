import json
from collections import Counter
from types import SimpleNamespace

from django.contrib.auth import login
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .forms import KazakhUserCreationForm
from .models import AnalysisHistory, EmotionModelInfo


EMOTION_DISPLAY_MAP = {
    "радость": {"name": "Қуаныш", "emoji": "😊"},
    "грусть": {"name": "Мұң", "emoji": "😢"},
    "гнев": {"name": "Ашу", "emoji": "😠"},
    "страх": {"name": "Қорқыныш", "emoji": "😨"},
    "удивление": {"name": "Таң қалу", "emoji": "😲"},
    "отвращение": {"name": "Жиіркеніш", "emoji": "🤢"},
    "нейтральный": {"name": "Бейтарап", "emoji": "😐"},
    "любовь": {"name": "Махаббат", "emoji": "❤️"},
    "joy": {"name": "Қуаныш", "emoji": "😊"},
    "sadness": {"name": "Мұң", "emoji": "😢"},
    "anger": {"name": "Ашу", "emoji": "😠"},
    "fear": {"name": "Қорқыныш", "emoji": "😨"},
    "surprise": {"name": "Таң қалу", "emoji": "😲"},
    "disgust": {"name": "Жиіркеніш", "emoji": "🤢"},
    "neutral": {"name": "Бейтарап", "emoji": "😐"},
    "love": {"name": "Махаббат", "emoji": "❤️"},
}


def _emotion_display_kk(emotion_key):
    key = (emotion_key or "").strip().lower()
    if key in EMOTION_DISPLAY_MAP:
        return EMOTION_DISPLAY_MAP[key]

    if not emotion_key:
        return {"name": "-", "emoji": "😐"}

    normalized = str(emotion_key).replace("_", " ").strip()
    return {"name": normalized.capitalize() if normalized else "-", "emoji": "😐"}


def _ensure_session_key(request):
    if not request.session.session_key:
        request.session.create()
    return request.session.session_key


def _history_queryset(request):
    if request.user.is_authenticated:
        return AnalysisHistory.objects.filter(user=request.user)

    return AnalysisHistory.objects.filter(
        user__isnull=True,
        session_key=_ensure_session_key(request),
    )


def _to_storage_confidence(value):
    try:
        confidence = float(value)
    except (TypeError, ValueError):
        return 0.0

    return confidence * 100.0 if confidence <= 1.0 else confidence


def _to_api_confidence(value):
    try:
        confidence = float(value)
    except (TypeError, ValueError):
        return 0.0

    return confidence / 100.0 if confidence > 1.0 else confidence


def _fallback_prediction(lang):
    language = lang if lang in {"kk", "ru"} else "auto"
    return {
        "primary_emotion": "neutral",
        "confidence": 0.5,
        "probabilities": {"neutral": 1.0},
        "probabilities_raw": {"neutral": 1.0},
        "main_emotion": "neutral",
        "main_score": 0.5,
        "emotion_info": {
            "neutral": {
                "key": "neutral",
                "emoji": ":|",
                "color": "#95A5A6",
                "name": "Бейтарап",
            }
        },
        "sentence_results": [],
        "language": language,
        "sentence_count": 0,
    }


def _run_prediction(text, lang):
    result = _fallback_prediction(lang)

    try:
        from .emotion_model import get_emotion_analyzer

        analyzer = get_emotion_analyzer()
        predicted = analyzer.predict(text, lang)

        probabilities = predicted.get("probabilities") or {}
        probabilities_raw = predicted.get("probabilities_raw") or probabilities
        if not probabilities:
            probabilities = {"neutral": 1.0}
            probabilities_raw = probabilities

        language = predicted.get("language") or (lang if lang in {"kk", "ru"} else "auto")
        primary_emotion = predicted.get("primary_emotion") or max(probabilities, key=probabilities.get)
        confidence = predicted.get("confidence")
        if confidence is None:
            confidence = probabilities.get(primary_emotion, 0.0)

        emotion_info = {}
        for key in probabilities_raw.keys():
            try:
                emotion_info[key] = analyzer.get_emotion_info(key, "kk")
            except Exception:
                emotion_info[key] = {
                    "key": key,
                    "emoji": ":|",
                    "color": "#95A5A6",
                    "name": key.title(),
                }

        result = {
            "primary_emotion": primary_emotion,
            "confidence": float(confidence),
            "probabilities": probabilities,
            "probabilities_raw": probabilities_raw,
            "main_emotion": predicted.get("main_emotion", primary_emotion),
            "main_score": float(predicted.get("main_score", confidence)),
            "emotion_info": emotion_info or result["emotion_info"],
            "sentence_results": predicted.get("sentence_results") or [],
            "language": language,
            "sentence_count": int(predicted.get("sentence_count") or 0),
        }
    except Exception:
        # Keep the fallback payload when model dependencies are unavailable.
        pass

    result["emotions"] = {
        key: round((value if value > 1.0 else value * 100.0), 1)
        for key, value in result["probabilities"].items()
    }
    return result


def home(request):
    _ensure_session_key(request)
    return render(request, "analyzer/home.html")


def history(request):
    analyses = list(_history_queryset(request)[:100])
    display_emotions = []
    for item in analyses:
        emotion_meta = _emotion_display_kk(item.primary_emotion)
        item.primary_emotion_label = emotion_meta["name"]
        item.primary_emotion_emoji = emotion_meta["emoji"]
        if item.primary_emotion:
            display_emotions.append(item.primary_emotion_label)

    by_emotion_counter = Counter(display_emotions)
    top_emotion = by_emotion_counter.most_common(1)

    avg_confidence = 0.0
    if analyses:
        avg_confidence = sum(float(item.confidence or 0.0) for item in analyses) / len(analyses)
        if avg_confidence <= 1.0:
            avg_confidence *= 100.0

    context = {
        "analyses": analyses,
        "stats": {
            "total": len(analyses),
            "avg_confidence": avg_confidence,
            "by_emotion": dict(by_emotion_counter),
        },
        "top_emotion_label": top_emotion[0][0] if top_emotion else None,
        "top_emotion_count": top_emotion[0][1] if top_emotion else 0,
    }
    return render(request, "analyzer/history.html", context)


def about(request):
    model_info = EmotionModelInfo.objects.filter(is_active=True).first()
    if not model_info:
        model_info = SimpleNamespace(
            name="Emotion AI демонстрациялық моделі",
            description="Ағымдағы эмоция моделі үшін резервтік сипаттама.",
            emotions=[{"name": "Бейтарап"}],
            limitations=(
                "Болжау сапасы мәтіннің тілі мен ұзындығына тәуелді.\n"
                "Дәл нәтиже үшін толық және түсінікті сөйлемдер жазыңыз."
            ),
        )
    return render(request, "analyzer/about.html", {"model_info": model_info})


def register(request):
    if request.user.is_authenticated:
        return redirect("analyzer:home")

    if request.method == "POST":
        form = KazakhUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("analyzer:home")
    else:
        form = KazakhUserCreationForm()

    return render(request, "registration/register.html", {"form": form})


@csrf_exempt
@require_http_methods(["POST"])
def api_predict(request):
    try:
        data = json.loads(request.body or "{}")
        text = (data.get("text") or "").strip()
        lang = data.get("lang", "auto")
        if lang not in {"auto", "kk", "ru"}:
            lang = "auto"

        if not text:
            return JsonResponse(
                {"success": False, "error": "Мәтін енгізу қажет", "error_code": "EMPTY_TEXT"},
                status=400,
            )
        if len(text) < 5:
            return JsonResponse(
                {"success": False, "error": "Мәтін тым қысқа", "error_code": "TOO_SHORT"},
                status=400,
            )
        if len(text) > 10000:
            return JsonResponse(
                {"success": False, "error": "Мәтін тым ұзын", "error_code": "TOO_LONG"},
                status=400,
            )
        if not any(ch.isalpha() for ch in text):
            return JsonResponse(
                {"success": False, "error": "Енгізілген дерек жарамсыз", "error_code": "INVALID_INPUT"},
                status=400,
            )

        prediction = _run_prediction(text, lang)

        analysis = AnalysisHistory.objects.create(
            text_snippet=text[:200],
            language=prediction["language"],
            primary_emotion=prediction["primary_emotion"],
            confidence=_to_storage_confidence(prediction["confidence"]),
            probabilities=prediction["probabilities_raw"],
            sentence_count=prediction["sentence_count"],
            session_key=_ensure_session_key(request),
            user=request.user if request.user.is_authenticated else None,
        )

        return JsonResponse(
            {
                "success": True,
                "data": {
                    "id": analysis.id,
                    "primary_emotion": prediction["primary_emotion"],
                    "confidence": prediction["confidence"],
                    "probabilities": prediction["probabilities"],
                    "probabilities_raw": prediction["probabilities_raw"],
                    "main_emotion": prediction["main_emotion"],
                    "main_score": prediction["main_score"],
                    "emotions": prediction["emotions"],
                    "emotion_info": prediction["emotion_info"],
                    "sentence_results": prediction["sentence_results"],
                    "language": prediction["language"],
                    "sentence_count": prediction["sentence_count"],
                    "timestamp": analysis.created_at.isoformat(),
                    "errors": [],
                },
            }
        )
    except json.JSONDecodeError:
        return JsonResponse(
            {"success": False, "error": "JSON пішімі қате", "error_code": "INVALID_JSON"},
            status=400,
        )
    except Exception as exc:
        return JsonResponse(
            {"success": False, "error": f"Сервер қатесі: {exc}", "error_code": "SERVER_ERROR"},
            status=500,
        )


@require_http_methods(["GET"])
def api_history_detail(request, analysis_id):
    analysis = get_object_or_404(_history_queryset(request), id=analysis_id)
    emotion_meta = _emotion_display_kk(analysis.primary_emotion)
    return JsonResponse(
        {
            "success": True,
            "data": {
                "id": analysis.id,
                "text_snippet": analysis.text_snippet,
                "language": analysis.language,
                "primary_emotion": analysis.primary_emotion,
                "primary_emotion_label": emotion_meta["name"],
                "primary_emotion_emoji": emotion_meta["emoji"],
                "confidence": _to_api_confidence(analysis.confidence),
                "probabilities": analysis.probabilities,
                "sentence_count": analysis.sentence_count,
                "created_at": analysis.created_at.isoformat(),
            },
        }
    )


@csrf_exempt
@require_http_methods(["POST", "DELETE"])
def api_history_delete(request, analysis_id):
    analysis = get_object_or_404(_history_queryset(request), id=analysis_id)
    analysis.delete()
    return JsonResponse({"success": True})


@csrf_exempt
@require_http_methods(["POST", "DELETE"])
def api_history_clear(request):
    deleted_count, _ = _history_queryset(request).delete()
    return JsonResponse({"success": True, "deleted": deleted_count})


@require_http_methods(["GET"])
def api_history_stats(request):
    histories = list(_history_queryset(request))
    by_emotion = Counter(
        _emotion_display_kk(item.primary_emotion)["name"]
        for item in histories
        if item.primary_emotion
    )

    avg_confidence = 0.0
    if histories:
        avg_confidence = sum(float(item.confidence or 0.0) for item in histories) / len(histories)
        if avg_confidence <= 1.0:
            avg_confidence *= 100.0

    return JsonResponse(
        {
            "success": True,
            "data": {
                "total": len(histories),
                "avg_confidence": avg_confidence,
                "by_emotion": dict(by_emotion),
            },
        }
    )
