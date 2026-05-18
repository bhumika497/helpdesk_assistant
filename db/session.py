import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./internal_company.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class DocumentModel(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    metadata_info = Column(String, nullable=True) 
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class QueryLogModel(Base):
    __tablename__ = "queries"

    id = Column(Integer, primary_key=True, index=True)
    input_query = Column(String, nullable=False)
    output_response = Column(Text, nullable=False)
    tools_used = Column(String, nullable=True)     
    routing_decision = Column(String, nullable=False) 
    latency_ms = Column(Integer, nullable=True)    
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

def init_db():
    Base.metadata.create_all(bind=engine)