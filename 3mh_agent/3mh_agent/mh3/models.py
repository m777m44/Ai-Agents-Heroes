# 3MH TECHNOLOGIES | t.me/j49_c | t.me/bshshshkk | http://3mh.pages.dev
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence
__all__ = ["ModelInfo", "CATALOG", "resolve_model", "suggest_models", "model_ids", "describe_model"]


@dataclass(frozen=True)
class ModelInfo:
    id: str
    label: str
    family: str
    tags: Sequence[str] = ()
    verified: bool = False
    gated: bool = False
    legacy: bool = False
    context: int = 0
    notes: str = ""

    @property
    def short(self) -> str:
        return self.id.split("/")[-1]

    @property
    def vision(self) -> bool:
        return "vision" in self.tags or "multimodal" in self.tags

    @property
    def reasoning(self) -> bool:
        return "reasoning" in self.tags

    def badge(self) -> str:
        marks = []
        if self.verified:
            marks.append("✓")
        if self.gated:
            marks.append("🔒")
        if self.legacy:
            marks.append("قديم")
        return f" [{' '.join(marks)}]" if marks else ""


def _m(id_: str, label: str, family: str, tags: Sequence[str] = (), **kw) -> ModelInfo:
    return ModelInfo(id=id_, label=label, family=family, tags=tuple(tags), **kw)
_CORE: List[ModelInfo] = [
    _m("@cf/zai-org/glm-4.7-flash", "GLM-4.7 Flash", "zai-org",
       ("reasoning", "tools", "fast"), verified=True, context=128_000,
       notes="الافتراضي — سريع ويدعم الأدوات والتفكير"),
    _m("@cf/zai-org/glm-5.3-flash", "GLM-5.3 Flash", "zai-org",
       ("reasoning", "tools", "fast"), context=128_000,
       notes="أحدث إصدار flash (قد يكون مقيد المعدل في أوقات الذروة)"),
    _m("@cf/zai-org/glm-5.2", "GLM-5.2", "zai-org",
       ("reasoning", "tools"), verified=True, context=200_000,
       notes="نموذج قوي متعدد الخطوات"),
    _m("@cf/openai/gpt-oss-120b", "GPT-OSS 120B", "openai",
       ("reasoning", "tools"), context=128_000, notes="أكبر نموذج مفتوح من OpenAI"),
    _m("@cf/openai/gpt-oss-20b", "GPT-OSS 20B", "openai",
       ("reasoning", "tools", "fast"), context=128_000, notes="خفيف وسريع"),
    _m("@cf/google/gemma-4-26b-a4b-it", "Gemma 4 26B (MoE)", "google",
       ("multimodal", "vision", "tools"), verified=True, context=128_000,
       notes="يدعم الصور — موصى به للرؤية"),
    _m("@cf/meta/llama-4-scout-17b-16e-instruct", "Llama 4 Scout 17B", "meta",
       ("multimodal", "vision", "fast"), context=128_000, notes="سريع ويدعم الصور"),
    _m("@cf/meta/llama-3.3-70b-instruct-fp8-fast", "Llama 3.3 70B (fp8 fast)", "meta",
       ("fast",), context=128_000, notes="توازن جيد بين الجودة والسرعة"),
    _m("@cf/qwen/qwen3-30b-a3b-fp8", "Qwen3 30B-A3B (fp8)", "qwen",
       ("reasoning", "fast"), context=32_000, notes="MoE خفيف"),
    _m("@cf/mistralai/mistral-small-3.1-24b-instruct", "Mistral Small 3.1 24B", "mistralai",
       ("vision",), context=128_000, notes="يدعم الصور"),
    _m("@cf/ibm/granite-4.0-h-micro", "Granite 4.0-H Micro", "ibm",
       ("fast", "micro"), context=32_000, notes="الأصغر والأسرع"),
    _m("@cf/moonshotai/kimi-k2.6", "Kimi K2.6", "moonshotai",
       ("reasoning", "tools"), verified=True, context=256_000, notes="سياق ضخم"),
    _m("@cf/moonshotai/kimi-k2.7-code", "Kimi K2.7 Code", "moonshotai",
       ("code", "reasoning"), context=256_000, notes="متخصص في البرمجة"),
    _m("@cf/deepseek-ai/deepseek-v4-flash-0731", "DeepSeek V4 Flash", "deepseek-ai",
       ("reasoning", "code", "fast"), context=128_000, notes="قد يكون مخصصاً للمقارنات"),
    _m("@cf/deepseek-ai/deepseek-v4-pro-0813", "DeepSeek V4 Pro", "deepseek-ai",
       ("reasoning", "code"), context=128_000, notes="قد يكون مخصصاً للمقارنات"),
]
_EXTRA: List[ModelInfo] = [
    _m("@cf/qwen/qwq-32b", "QwQ 32B", "qwen", ("reasoning",), legacy=True),
    _m("@cf/qwen/qwen2.5-coder-32b-instruct", "Qwen2.5 Coder 32B", "qwen", ("code",), legacy=True),
    _m("@cf/google/gemma-3-12b-it", "Gemma 3 12B", "google", ("vision",), legacy=True),
    _m("@cf/google/gemma-7b-it", "Gemma 7B", "google", (), legacy=True),
    _m("@cf/meta/llama-3.2-3b-instruct", "Llama 3.2 3B", "meta", ("fast",), legacy=True),
    _m("@cf/meta/llama-3.2-1b-instruct", "Llama 3.2 1B", "meta", ("micro",), legacy=True),
    _m("@cf/meta/llama-3.1-70b-instruct", "Llama 3.1 70B", "meta", (), legacy=True),
    _m("@cf/meta/llama-3.1-8b-instruct", "Llama 3.1 8B", "meta", ("fast",), legacy=True),
    _m("@cf/meta/llama-3.1-8b-instruct-fast", "Llama 3.1 8B (fast)", "meta", ("fast",), legacy=True),
    _m("@cf/meta/llama-3.1-8b-instruct-fp8", "Llama 3.1 8B (fp8)", "meta", ("fast",), legacy=True),
    _m("@cf/meta/llama-3-8b-instruct", "Llama 3 8B", "meta", (), legacy=True),
    _m("@cf/mistral/mistral-7b-instruct-v0.2", "Mistral 7B v0.2", "mistral", (), legacy=True),
    _m("@cf/mistral/mistral-7b-instruct-v0.1", "Mistral 7B v0.1", "mistral", (), legacy=True),
    _m("@cf/nousresearch/hermes-2-pro-mistral-7b", "Hermes 2 Pro Mistral 7B", "nousresearch",
       ("tools",), legacy=True),
    _m("@cf/microsoft/phi-2", "Phi-2", "microsoft", ("micro",), legacy=True),
    _m("@cf/defog/sqlcoder-7b-2", "SQLCoder 7B", "defog", ("code", "sql"), legacy=True),
    _m("@cf/aisingapore/gemma-sea-lion-v4-27b-it", "Gemma Sea-Lion v4 27B", "aisingapore", (), legacy=True),
    _m("@cf/meta/llama-2-7b-chat-fp16", "Llama 2 7B (fp16)", "meta", (), verified=True, legacy=True,
       notes="قديم جداً — للاختبار فقط"),
    _m("@cf/meta/llama-3.2-11b-vision-instruct", "Llama 3.2 11B Vision", "meta",
       ("vision",), gated=True, legacy=True, notes="يتطلب الموافقة على ترخيص Meta (5016)"),
]
CATALOG: List[ModelInfo] = _CORE + _EXTRA
_BY_ID: Dict[str, ModelInfo] = {m.id: m for m in CATALOG}
ALIASES: Dict[str, str] = {
    "glm": "@cf/zai-org/glm-4.7-flash",
    "glm4": "@cf/zai-org/glm-4.7-flash",
    "glm47": "@cf/zai-org/glm-4.7-flash",
    "glm5": "@cf/zai-org/glm-5.2",
    "glm52": "@cf/zai-org/glm-5.2",
    "glm53": "@cf/zai-org/glm-5.3-flash",
    "gpt": "@cf/openai/gpt-oss-120b",
    "gptoss": "@cf/openai/gpt-oss-120b",
    "oss120": "@cf/openai/gpt-oss-120b",
    "oss20": "@cf/openai/gpt-oss-20b",
    "gemma": "@cf/google/gemma-4-26b-a4b-it",
    "gemma4": "@cf/google/gemma-4-26b-a4b-it",
    "vision": "@cf/google/gemma-4-26b-a4b-it",
    "صورة": "@cf/google/gemma-4-26b-a4b-it",
    "صور": "@cf/google/gemma-4-26b-a4b-it",
    "llama4": "@cf/meta/llama-4-scout-17b-16e-instruct",
    "scout": "@cf/meta/llama-4-scout-17b-16e-instruct",
    "llama": "@cf/meta/llama-3.3-70b-instruct-fp8-fast",
    "llama70": "@cf/meta/llama-3.3-70b-instruct-fp8-fast",
    "qwen": "@cf/qwen/qwen3-30b-a3b-fp8",
    "mistral": "@cf/mistralai/mistral-small-3.1-24b-instruct",
    "granite": "@cf/ibm/granite-4.0-h-micro",
    "micro": "@cf/ibm/granite-4.0-h-micro",
    "kimi": "@cf/moonshotai/kimi-k2.6",
    "kimicode": "@cf/moonshotai/kimi-k2.7-code",
    "code": "@cf/moonshotai/kimi-k2.7-code",
    "deepseek": "@cf/deepseek-ai/deepseek-v4-flash-0731",
    "fast": "@cf/zai-org/glm-4.7-flash",
    "default": "@cf/zai-org/glm-4.7-flash",
}


def model_ids() -> List[str]:
    return [m.id for m in CATALOG]


def get(model_id: str) -> Optional[ModelInfo]:
    return _BY_ID.get(model_id.strip())


def resolve_model(query: str) -> Optional[ModelInfo]:
    if not query:
        return None
    q = query.strip()
    direct = _BY_ID.get(q)
    if direct:
        return direct
    low = q.lower().strip("@")
    alias = ALIASES.get(low) or ALIASES.get(low.replace("-", "").replace(".", "").replace(" ", ""))
    if alias:
        return _BY_ID.get(alias)
    if not low.startswith("@cf/") and "/" not in low:
        low = "@cf/" + low
    if low in _BY_ID:
        return _BY_ID[low]
    for m in CATALOG:
        if m.id.lower() == low or m.short.lower() == low.rsplit("/", 1)[-1] or m.label.lower() == q.lower():
            return m
    scored: List[tuple] = []
    needle = low.rsplit("/", 1)[-1]
    for m in CATALOG:
        hay = f"{m.id} {m.label} {m.family} {' '.join(m.tags)}".lower()
        if needle and needle in hay:
            score = len(needle) - (0 if m.verified else 1) - (2 if m.legacy else 0)
            scored.append((score, m))
    if scored:
        scored.sort(key=lambda t: t[0], reverse=True)
        return scored[0][1]
    return None


def suggest_models(query: str, limit: int = 6) -> List[ModelInfo]:
    out: List[ModelInfo] = []
    needle = (query or "").lower().strip()
    for m in CATALOG:
        hay = f"{m.id} {m.label} {m.family} {' '.join(m.tags)}".lower()
        if not needle or needle in hay:
            out.append(m)
    out.sort(key=lambda m: (not m.verified, m.legacy, m.label))
    return out[:limit]


def describe_model(model_id: str) -> str:
    m = get(model_id)
    if not m:
        return model_id
    tags = "، ".join(m.tags) or "—"
    ctx = f"{m.context // 1000}K" if m.context else "؟"
    parts = [f"🧠 {m.label}", f"   المعرّف: {m.id}", f"   العائلة: {m.family}",
             f"   السياق: {ctx} توكن", f"   القدرات: {tags}"]
    if m.notes:
        parts.append(f"   ملاحظات: {m.notes}")
    return "\n".join(parts)


def vision_models() -> List[ModelInfo]:
    return [m for m in CATALOG if m.vision]


def is_vision(model_id: str) -> bool:
    m = get(model_id)
    return bool(m and m.vision)
