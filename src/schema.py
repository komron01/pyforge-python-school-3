import re
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLAlchemy Base
Base = declarative_base()

# Database connection setup
DATABASE_URL = "postgresql://postgres:123@postgres:5432/drugs"

# Create engine and session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Drug(Base):
    __tablename__ = 'drugs'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    smiles = Column(String)

# Create the database tables
Base.metadata.create_all(bind=engine)

class DrugResponse(BaseModel):
    id: int
    name: str = Field(..., min_length=1, max_length=100, description="Drug name")
    smiles: str = Field(..., min_length=1, max_length=100, description="Structure of chemical molecules")

    @field_validator("smiles")
    def validate_smiles(cls, value):
        if not re.match(
            r"^(?:[A-Z][a-z]?|[a-z])(?:(?:[1-9]\d*)?(?:\[(?:(?:[A-Z][a-z]?(?:@[@]?)?)"
            r"|[#+-]|\d+)?\])?|(?:[-=#$:/\\])?(?:[A-Z][a-z]?|[a-z])|[().\[\]])*((?:[1-9]\d*)?)$",
            value,
        ):
            raise ValueError("This SMILES has an invalid structure")
        return value

class DrugAdd(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Drug name")
    smiles: str = Field(..., min_length=1, max_length=100, description="Structure of chemical molecules")

    @field_validator("smiles")
    def validate_smiles(cls, value):
        if not re.match(
            r"^(?:[A-Z][a-z]?|[a-z])(?:(?:[1-9]\d*)?(?:\[(?:(?:[A-Z][a-z]?(?:@[@]?)?)"
            r"|[#+-]|\d+)?\])?|(?:[-=#$:/\\])?(?:[A-Z][a-z]?|[a-z])|[().\[\]])*((?:[1-9]\d*)?)$",
            value,
        ):
            raise ValueError("This SMILES has an invalid structure")
        return value
