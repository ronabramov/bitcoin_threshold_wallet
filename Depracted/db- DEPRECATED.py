from pymongo import MongoClient

DEFAULT_CONNECTION_STRING = "mongodb+srv://ronabram:ic6UYRx1onTf5rKm@tresholdecdsawallet.fdncb.mongodb.net/?retryWrites=true&w=majority&appName=TresholdECDSAwallet"
DB_NAME = "ecdsa-db" 

class Database:
    def __init__(self, connection_string, database_name):
        self.client = MongoClient(connection_string)
        self.db = self.client[database_name]
    
    def get_collection(self, collection_name):
        return self.db[collection_name]

db = Database(
    connection_string = DEFAULT_CONNECTION_STRING,
    database_name = DB_NAME
)

wallets_collection = db.get_collection("wallets")
transactions_collection = db.get_collection("transactions")
users_collection = db.get_collection("users")