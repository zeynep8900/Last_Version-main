# config.py

class Config:
    SECRET_KEY = 'secret-key-goes-here'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mssql+pyodbc://user:zeynep123.@ourdbserver.database.windows.net/explorecitydb?driver=ODBC+Driver+18+for+SQL+Server'

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = 'mssql+pyodbc://user:zeynep123.@ourdbserver.database.windows.net/explorecitydb?driver=ODBC+Driver+18+for+SQL+Server'
