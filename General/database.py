from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String, DateTime, func, Boolean, Float, CheckConstraint
from General.config import settings

engine = create_async_engine(settings.database_url, echo=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()


# --- THE TABLES ---
# Time Decay
class TaskStatus(Base):
    __tablename__ = "tasks_status"

    id = Column(Integer, primary_key=True, index=True)
    status = Column(String, default="queued")
    influential_ready = Column(Boolean, default=False)
    bulk_ready = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    # This field allows for "Time Decay" calculations later
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


# Time Decay
class InfluentialResults(Base):
    __tablename__ = "influential_results"

    id = Column(Integer, primary_key=True, index=True)
    location = Column(String)

    mode_sentiment = Column(Float)
    most_positive = Column(Float)
    most_negative = Column(Float)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


# Time Decay
class BulkResults(Base):
    __tablename__ = "bulk_results"

    id = Column(Integer, primary_key=True, index=True)
    location = Column(String)

    mode_sentiment = Column(Float)
    most_positive = Column(Float)
    most_negative = Column(Float)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class InfluentialTrainingData(Base):
    __tablename__ = "training_influential"

    tweet_id = Column(Integer, primary_key=True, index=True)

    tweet = Column(String)

    sentiment = Column(Integer)

    __table_args__ = (
        CheckConstraint('sentiment IN (0, 1)', name='check_sentiment_bool'),
    )


class BulkTrainingData(Base):
    __tablename__ = "training_Bulk"

    tweet_id = Column(Integer, primary_key=True, index=True)

    tweet = Column(String)

    sentiment = Column(Integer)

    __table_args__ = (
        CheckConstraint('sentiment IN (0, 1)', name='check_sentiment_bool'),
    )


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
