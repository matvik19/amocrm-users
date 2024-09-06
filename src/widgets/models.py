from sqlalchemy import Column, Integer, String

from src.database import Base


class Widgets(Base):
    __tablename__ = "widgets"

    id = Column(Integer, primary_key=True)
    client_id = Column(String, nullable=False)
    client_secret = Column(String, nullable=False)
    redirect_url = Column(String, nullable=False)