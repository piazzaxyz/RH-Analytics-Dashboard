from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Position(Base):
    __tablename__ = "positions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(80), nullable=False)
    description = Column(String(255), nullable=False)
    base_salary = Column(Float, nullable=False)
    level = Column(String(40), nullable=True)
    department_id = Column(Integer, ForeignKey("departments.id", ondelete="SET NULL"), nullable=True)
    ala_id = Column(Integer, ForeignKey("alas.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, server_default=func.current_timestamp(), nullable=False)
    updated_at = Column(DateTime, server_default=func.current_timestamp(), onupdate=func.current_timestamp(), nullable=False)

    department = relationship("Department")
    ala = relationship("Ala", back_populates="positions")
    employees = relationship("Employee", back_populates="position")
