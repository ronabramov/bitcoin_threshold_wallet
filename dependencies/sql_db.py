import os
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship


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
    wallet_id = Column(String, primary_key=True, nullable=False) #This will be the room Id.
    threshold = Column(Integer, nullable=False)
    users = Column(Text, nullable=True) #@alice:matrix.org,@bob:matrix.org - we will save comma parsed absolute path for participating users
    configuration = Column(Text, nullable=True)
    transactions = relationship("Transaction", back_populates="wallet")
    


class Transaction(Base):
    __tablename__ = "transactions"
    transaction_id = Column(String, primary_key=True, nullable=False)
    details = Column(Text, nullable=True)
    approvers = Column(Text, nullable=True)
    wallet_id = Column(String, ForeignKey("wallets.wallet_id"), nullable=False)
    wallet = relationship("Wallet", back_populates="transactions")

# check if the database exists
if not os.path.exists(DB_FILE):
    # Create SQLite engine
    engine = create_engine(f"sqlite:///{DB_FILE}")
    Base.metadata.create_all(engine)
else:
    engine = create_engine(f"sqlite:///{DB_FILE}")

# Session maker
Session = sessionmaker(bind=engine)

# this is the session that will be used to interact with the database
session = Session()
