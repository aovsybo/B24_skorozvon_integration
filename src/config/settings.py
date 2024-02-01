from pathlib import Path
import os
from dotenv import load_dotenv, find_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("SECRET_KEY"),

YANDEX_DISK_TOKEN = os.environ.get("YANDEX_DISK_TOKEN")
SKOROZVON_LOGIN = os.environ.get("SKOROZVON_LOGIN")
SKOROZVON_API_KEY = os.environ.get("SKOROZVON_API_KEY")
SKOROZVON_APPLICATION_ID = os.environ.get("SKOROZVON_APPLICATION_ID")
SKOROZVON_APPLICATION_KEY = os.environ.get("SKOROZVON_APPLICATION_KEY")

BITRIX_CREATE_DEAL_API_LINK = os.environ.get("BITRIX_CREATE_DEAL_API_LINK")
BITRIX_CREATE_CONTACT_API_LINK = os.environ.get("BITRIX_CREATE_CONTACT_API_LINK")
BITRIX_GET_LIST_OF_CONTACTS = os.environ.get("BITRIX_GET_LIST_OF_CONTACTS")
BITRIX_GET_DEAL_BY_ID = os.environ.get("BITRIX_GET_DEAL_BY_ID")
BITRIX_GET_DEAL_API_URL = os.environ.get("BITRIX_GET_DEAL_API_URL")
BITRIX_GET_DEAL_CATEGORY_LIST = os.environ.get("BITRIX_GET_DEAL_CATEGORY_LIST")
BITRIX_GET_DEAL_CATEGORY_STAGES_LIST = os.environ.get("BITRIX_GET_DEAL_CATEGORY_STAGES_LIST")
BITRIX_UPDATE_DEAL = os.environ.get("BITRIX_UPDATE_DEAL")
BITRIX_APP_TOKEN = os.environ.get("BITRIX_APP_TOKEN")
# BITRIX_LEAD_TYPE = {
#     "49": "есть ПВ",
#     "89": "записать на замер",
#     "87": "посчитать",
#     "51": "С продажи",
#     "83": "без ПВ",
#     "85": "ипотека",
#     "125": "-",
#     "173": "наличные",
#     "175": "кредит или рассрочка",
#     "496": "ЛИЗИНГ",
#     "494": "ПРОДАЖА",
#     "": "",
# }
# BITRIX_LEAD_QUALIFICATION = {
#     "121": "без монтажа",
#     "123": "с монтажом",
#     "45": "для себя",
#     "47": "инвестиция",
#     "117": "уже майнит",
#     "119": "планирует начать майнить",
#     "171": "для кого-то другого",
#     "492": "-",
#     "498": "для компании",
#     "500": "ФЛ",
#     "502": "ФЛ+ГЕО",
#     "504": "ФЛ+СЛ",
#     "": "",
# }
# BITRIX_CITIES = {
#     "275": "Казань",
#     "277": "Ростов-на-Дону",
#     "311": "Новосибирск",
#     "313": "Екатеринбург",
#     "315": "Тюмень",
#     "317": "Краснодар",
#     "331": "Санкт-Петербург",
#     "381": "Москва",
#     "383": "Уфа",
#     "385": "Нижний Новгород",
#     "435": "Красноярск",
#     "437": "Сочи",
#     "439": "Самара",
#     "441": "Тула",
#     "476": "Челябинск",
#     "478": "Омск",
#     "480": "Воронеж",
#     "482": "Волгоград",
#     "484": "Пермь",
#     "486": "Ставрополь",
#     "488": "Сургут",
#     "": "",
# }
# BITRIX_COUNTRIES = {
#     "287": "Тайланд",
#     "405": "Бали",
#     "283": "Турция",
#     "285": "Дубаи",
#     "289": "Северный кипр",
#     "291": "Южный Кипр",
#     "433": "Индонезия",
#     "": "",
# }
# BITRIX_CATEGORY_NAME_TO_SCENARIO = {
#     "ОМР Металл [ЧАСТЬ 6]": "[П1] ОМР Металл [СЗ]",
#     "СС СПБ [Часть 8]": "[П2] Северная Столица СПБ [СЗ]",
#     "[П3] Тихомиров НСК": "[П3] Тихомиров НСК [Ручной]",
#     "Алиро Окна Краснодар [Часть 3]": "[П4] Алиро Окна Краснодар [СЗ]",
#     "ABC.DATA: Москва [часть 4 ТЕСТ]": "[П5] ABC Data РФ [Старт]",
#     "ABC.DATA: UTC +3 [Часть 3]": "[П5] ABC Data РФ [Старт]",
#     "Неометрия Отражение [Часть 4]": "[П6] Неометрия Краснодар [Отражение+Южане+Улыбка]",
#     "Неометрия Облака Новороссийск [старт]": "[П7] Неометрия Облака Новороссийск [СЗ]",
#     "Неометрия 1799 Ростов [часть2]": "[П8] Неометрия Ростов [СЗ]",
#     "АН Домос ЕКБ [часть 4]": "[П9] АН Домос ЕКБ [СЗ]",
#     "АН Империя Калининград [тест]": "[П10] АН Империя Калининград",
#     "АН ЦЖР Рязань [тест]": "[П11] АН ЦЖР Рязань",
#     "[П12] АН Click Пермь [1]": "[П12] Ан Click Пермь",
#     "[Н.Д.] ABC.DATA: РЕГИОНЫ [Часть 1]": "[П14] ABC Data | Наши данные РФ ",
#     "АВС ЗАГРАН [Часть 3]": "[П15] ABC Data ЗАГРАН [СЗ]",
#     "[П16] АН Паритет Воронеж": "[П16] АН Паритет Воронеж",
#     "ABC АВТО МСК+СПБ [тест]": "[П17] ABC АВТО МСК+СПБ",
#     "Диалог-Авто ЧЕРИ Альметьевск [тест]": "[П18] Чери Диалог-Авто",
#     "Интерлизинг": "[П19] ИнтерЛизинг [СЗ] ",
#     "АН Покров Омск [тест]": "[П20] АН Покров Омск",
#     "[П21] АН АЯКС Пенза": "[П21] АН АЯКС Пенза",
#     "[П22] АН MNS Самара [тест]": "[П22] АН MNS Самара",
#     "[П23] АН Анреал Тюмень [тест]": "[П23] АН Анреал Тюмень",
#     "[П24] АН Новострой Астрахань [тест]": "[П24] АН Новострой Астрахань",
#     "[П25] АН Аквариум ОМСК [тест]": "[П25] АН Аквариум Омск",
#     "[П26] АН Добрая душа Уфа [тест]": "[П26] АН Добрая душа Уфа",
#     "[П27] АН АН Арион Group ТМН [тест]": "[П27] АН Арион Group ТМН",
#     "[П28] АН Rialtor Group НСК [1]": "[П28] АН Rialtor Group НСК",
#     "[П29] АН ИИ Тюмень [тест]": "[П29] АН ИИ ТМН",
#     "[П30] АН Недвижимость Калининград [тест]": "[П30] АН Недвижимость Калининград",
#     "[П31] АН Свои Люди Рязань [1]": "[П31] АН Свои Люди",
#     "[П32] АН ТН Тула": "[П32] АН ТН Тула",
#     "[П33] АН Агент026 Ставрополь": "[П33] АН Агент026 Ставрополь",
#     "[П34] АН Сити-Центр Воронеж": "[П34] АН Сити-Центр Воронеж",
#     "[П35] Фолиант Владивосток": "[П35] АН Фолиант Владивосток",
#     "[П36] Трак Импорт Самосвалы": "[П36] Трак Импорт Самосвалы",
#     "[П37] РТА Спецтехника": "[П37] РТА Спецтехника",
#     "[П38] АН Жилфонд Брянск": "[П38] АН Жилфонд Брянск",
#     "[П39] АН Гарант Самара": "[П39] АН Гарант Самара",
#     "[П40] АН Метраж Барнаул": "[П40] АН Метраж Барнаул",
#     "[П41] АН Мирами Кемерово": "[П41] АН Мирами Кемерово",
#     "[П42] АН Владис Ижевск": "[П42] АН Владис Ижевск",
#     "[П43] Экскаваторы ТракРесурс-Регион": "[П43] Экскаваторы ТракРесурс-Регион",
#     "[П44] Свободная 4": "[П44] ТЕСТ ИНТЕГРАЦИЙ",
#     "[П45] ЦАН Тула": "[П45] ЦАН Тула",
#     "[П46] Контрол-Лизинг (CTRL)": "[П46] Контрол-Лизинг (CTRL)",
#     "[П47] АН Самолет Плюс Челябинск": "[П47] АН Самолет Плюс Челябинск",
#     "СП РФ [ЧАСТЬ 1]": "[П48] СП РФ",
#     "[Пакка] Линии Розлива [Тариф 1]": "[П49] Пакка НСК",
#     "АН1 НСК [тест]": "[П50] АН1 НСК",
#     "[П51] АН Зилант Казань": "[П51] АН Зилант Казань",
#     "[П52] Электрообогрев СПБ": "[П52] Электрообогрев СПБ",
#     "[П53] АН ПервоЗдание Астрахань": "[П53] АН ПервоЗдание Астрахань",
#     "[П54] Ульяновск АН Самолет Плюс": "[П54] Ульяновск Самолет",
#     "[П55] Русстанок Самара": "[П55] Русстанок Самара",
#     "нет в сз": "[П56] Не подходит KPI/В лизинг",
#     "[П57] АН Я Дома Томск": "[П57] АН Я Дома Томск",
#     "[П58] АН 43 Киров": "[П58] АН 43 Киров",
#     "[П59] АН МИРА Ставрополь": "[П59] АН МИРА Ставрополь",
#     "[П60] Самолет+ ЧЛБ": "[П60] Самолет+ ЧЛБ",
#     "[П61] ЧФК Недвижимость КРДР": "[П61] ЧФК Недвижимость КРДР",
#     "[П62] Запаска": "[П62] Запаска",
#     "[П63] Запаска": "[П63] Запаска",
#     "[П64] Запаска": "[П64] Запаска",
#     "[П65] Запаска": "[П65] Запаска",
#     "[П66] Запаска": "[П66] Запаска"
# }
BITRIX_SUCCESSFUL_RESULT_NAMES = [
    "успех",
]
SCOPES = os.environ.get("SCOPES").split(',')
INTEGRATIONS_SPREADSHEET_ID = os.environ.get("INTEGRATIONS_SPREADSHEET_ID")
INTEGRATIONS_SHEET_NAME = "таблицы проектов"
CONFIG_SHEET_NAME = "Конфигурация"
CONFIG_SHEET_FIELDS = ["Тип лида", "Квалификация лида", "Город", "Страна"]
PHONE_FIELD_NAMES = ["Тел", "Номер абонента", "Телефон Лида", "Номер", "Телефон"]

TG_API_TOKEN = os.environ.get("TG_API_TOKEN")
TG_DEV_ACCOUNT = os.environ.get("TG_DEV_ACCOUNT")
TG_DEV_CHAT = os.environ.get("TG_DEV_CHAT")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS").split(',')
APSCHEDULER_DATETIME_FORMAT = "N j, Y, f:s a"

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    "django_apscheduler",

    'integrations',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates']
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME':  os.environ.get("POSTGRES_DB"),
        'USER':  os.environ.get("POSTGRES_USER"),
        'PASSWORD':  os.environ.get("POSTGRES_PASSWORD"),
        'HOST':  os.environ.get("POSTGRES_HOST"),
        'PORT':  os.environ.get("POSTGRES_PORT", 5432),
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
