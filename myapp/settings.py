"""
Django settings for myapp project.
"""

from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# =========================
# 基本（本番では必ず環境変数から渡す）
# =========================
SECRET_KEY = os.getenv(
    "DJANGO_SECRET_KEY",
    "django-insecure-4r889(*9l-+m&oe=7-n5m9!p$(eh&i*v&)_pdvz@%f$blr-@lq"  # ←暫定（本番で必ず差し替え）
)

# デフォルトは開発用に True。デプロイ先では環境変数 DJANGO_DEBUG=false を設定してOFFに。
DEBUG = os.getenv("DJANGO_DEBUG", "True").lower() == "true"

# デプロイ先のドメイン/ホストを環境変数で列挙（カンマ区切り）
# 例: "your-app.onrender.com,www.example.com"
ALLOWED_HOSTS = ['masudate.pythonanywhere.com']

# CSRF許可オリジン（httpsスキーム付き、カンマ区切り）
# 例: "https://your-app.onrender.com,https://www.example.com"
_csrf_env = os.getenv("CSRF_TRUSTED_ORIGINS", "")
CSRF_TRUSTED_ORIGINS = ["https://masudate.pythonanywhere.com"]

# 逆プロキシ越しのHTTPSを認識（Render/Heroku/Nginx/Cloudflare等）
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# =========================
# アプリ/ミドルウェア
# =========================
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "diary",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "myapp.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "myapp.wsgi.application"

# =========================
# DB（開発: SQLite）
# =========================
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# =========================
# 認証
# =========================
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "ja"
TIME_ZONE = "Asia/Tokyo"
USE_I18N = True
USE_TZ = True

# =========================
# 静的/メディア
# =========================
STATIC_URL = "static/"
# collectstatic の出力先（本番で必須）
STATIC_ROOT = BASE_DIR / "staticfiles"
# もしプロジェクト直下に独自静的ファイルがあるなら（任意）
# STATICFILES_DIRS = [BASE_DIR / "static"]

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# =========================
# ログイン遷移
# =========================
LOGIN_REDIRECT_URL = "home"
LOGIN_URL = "login"

# =========================
# セッション
# =========================
SESSION_COOKIE_AGE = 60 * 60 * 2         # 2時間
SESSION_EXPIRE_AT_BROWSER_CLOSE = False  # ブラウザを閉じても期限までは維持
SESSION_SAVE_EVERY_REQUEST = True        # アクセスの度に延長
SESSION_COOKIE_SAMESITE = "Lax"

# セキュアクッキー/HTTPSリダイレクト
if DEBUG:
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    SECURE_SSL_REDIRECT = False
else:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = True  # 本番はHTTPSへ強制リダイレクト
