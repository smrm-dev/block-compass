import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    TESTING = False


class DevelopmentConfig(Config):
    DEBUG = True

    MONGO_URI = os.environ.get(
        "DEV_MONGO_URI"
    ) or "mongodb://localhost:27017/blockCompass"


class TestingConfig(Config):
    TESTING = True

    MONGO_URI = os.environ.get(
        "TEST_MONGO_URI"
    ) or "mongodb://localhost:27017/blockCompass"


class ProductionConfig(Config):
    MONGO_URI = os.environ.get(
        "PRO_MONGO_URI"
    ) or "mongodb://localhost:27017/blockCompass"


env_config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}
