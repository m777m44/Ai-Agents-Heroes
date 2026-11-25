# ══════════════════════════════════════════════════════════════════════════════
#  3mh agent — 3MH TECHNOLOGIES | t.me/j49_c | http://3mh.pages.dev
# ══════════════════════════════════════════════════════════════════════════════
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    TZ=UTC

# bash مطلوب لأداة shell_exec، وca-certificates للاتصال بـ TLS
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      bash ca-certificates curl tini \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# تثبيت الاعتماديات أولاً (طبقة قابلة للتخزين)
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# بقية المشروع
COPY . .

# مستخدم غير جذري + مجلد البيانات
RUN useradd --create-home --uid 10001 mh3 \
 && mkdir -p /app/data/workspace \
 && chown -R mh3:mh3 /app
USER mh3

VOLUME ["/app/data"]

# فحص خفيف: التأكد من سلامة الحزمة
LABEL org.opencontainers.image.title="3mh agent" \
      org.opencontainers.image.vendor="3MH TECHNOLOGIES" \
      org.opencontainers.image.url="http://3mh.pages.dev" \
      org.opencontainers.image.source="http://3mh.pages.dev"

HEALTHCHECK --interval=60s --timeout=20s --start-period=30s --retries=3 \
  CMD python -c "import mh3, mh3.agent, mh3.tg.app" || exit 1

ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["python", "run.py"]
