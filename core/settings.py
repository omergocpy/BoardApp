from pathlib import Path
import os
import datetime

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-(^eqxpe@+hg+e9!@d8tanbdwg8z1xxc0nl0_)s#rh6jsv5pf24'


DEBUG = True

ALLOWED_HOSTS = ["boardapp.net", "www.boardapp.net", "127.0.0.1", "localhost"]

CSRF_COOKIE_HTTPONLY = False 
CSRF_COOKIE_SAMESITE = 'Lax'  

CSRF_COOKIE_SECURE = False
CSRF_TRUSTED_ORIGINS = ['https://boardapp.net', 'http://127.0.0.1:8000']

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    "notifications",
    "users",
    "pages",
    'posts',
    'support',
    'scoreboards',
    "django_extensions",
    'django_celery_beat',
    'django_celery_results',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'users.middleware.UserSessionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'core.middleware.AjaxRequestMiddleware', 

]

ROOT_URLCONF = 'core.urls'

CELERY_RESULT_BACKEND = 'django-db'

CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_BEAT_SCHEDULE = {
    'check-stale-sessions': {
        'task': 'users.tasks.check_and_close_stale_sessions',
        'schedule': datetime.timedelta(minutes=30),  # Her 30 dakikada bir çalıştır
    },
}
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')], 
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'users.context_processors.navbar_context'
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_USER_MODEL = 'users.CustomUser'


AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


LANGUAGE_CODE = 'tr'

TIME_ZONE = 'Europe/Istanbul'

USE_I18N = True  
USE_L10N = True  
USE_TZ = True    

DATETIME_FORMAT = 'd-m-Y H:i:s'
DATE_FORMAT = 'd-m-Y'
TIME_FORMAT = 'H:i:s'


STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles') 

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CELERY_BEAT_SCHEDULE = {
    'check-second-survey-due': {
        'task': 'users.tasks.check_second_survey_due',
        'schedule': datetime.timedelta(days=1),  # Her gün kontrol et
    },
}

JAZZMIN_SETTINGS = {
    "site_title": "Board Yönetim Paneli",
    "site_header": "Bord Yönetimi",
    "site_brand": "Board Mobil",
    "welcome_sign": "Hoş Geldiniz Board Mobil App Yönetim Paneline",
    "show_sidebar": True,
    "navigation_expanded": True,
    "order_with_respect_to": ["auth", "books", "books.author", "books.book"],
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
    },
    "custom_links": {
        "footer": [
            {
                "name": "Board Mobil App",
                "url": "https://example.com",  
                "icon": "fas fa-link",  
                "permissions": ["auth.view_user"],  
            },
            {
                "name": "Hakkında",
                "url": "https://example.com/about",
                "icon": "fas fa-info-circle",
                "permissions": ["auth.view_user"],
            },
        ],
    },
    "site_brand_footer": "© 2024 Board Mobil App",  
        "footer": "© 2024 Board Mobil App - All Rights Reserved",

}

JAZZMIN_UI_TWEAKS = {
    "navbar": "navbar-dark",  
    "theme": "flatly",  
    "dark_mode_theme": "darkly",  
    "primary_color": "#ff7f0e", 
    "accent": "orange", 
    "button_classes": {
        "primary": "btn btn-warning", 
        "secondary": "btn btn-secondary",
        "info": "btn btn-info",
        "warning": "btn btn-warning", 
        "danger": "btn btn-danger",
        "success": "btn btn-success",
    },
    "sidebar": "sidebar-light-orange",  
    "brand_colour": "orange",  
    "navbar_fixed": True,  
    "sidebar_fixed": True,  
}
