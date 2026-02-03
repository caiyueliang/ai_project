from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "mysql+mysqlconnector://root:password@localhost:3306/taichi_training"
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # 对象存储配置
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket: str = "taichi-media"
    
    # 阿里云ASR配置
    aliyun_access_key_id: str = ""
    aliyun_access_key_secret: str = ""
    aliyun_region: str = "cn-shanghai"
    
    class Config:
        env_file = ".env"

settings = Settings()

# 数据库引擎
engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()