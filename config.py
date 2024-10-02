
class DevelopmentConfig:
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:BAC146@localhost/library_db'
    DEBUG = True


class TestingConfig:
    pass

class ProductionConfig:
    pass