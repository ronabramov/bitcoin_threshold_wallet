from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


Base = declarative_base()
DB_FILE = "local_db.sqlite"

class User(Base):
    __tablename__ = "users"
    email = Column(String, primary_key=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    homeserver_url = Column(String, nullable=True)
    homeserver_login = Column(String, nullable=True)
    homeserver_password = Column(String, nullable=True)


class Wallet(Base):
    __tablename__ = "wallets"
    wallet_id = Column(String, primary_key=True, nullable=False)
    threshold = Column(Integer, nullable=False)
    users = Column(Text, nullable=True)
    configuration = Column(Text, nullable=True)


class Transaction(Base):
    __tablename__ = "transactions"
    transaction_id = Column(String, primary_key=True, nullable=False)
    wallet_id = Column(String, ForeignKey("wallets.wallet_id"), nullable=False)
    details = Column(Text, nullable=True)
    approvers = Column(Text, nullable=True)

# Create SQLite engine
engine = create_engine(f"sqlite:///{DB_FILE}")

# Create all tables
Base.metadata.create_all(engine)

# Session maker
Session = sessionmaker(bind=engine)
session = Session()
