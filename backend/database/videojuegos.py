from motor.motor_asyncio import AsyncIOMotorClient
MONGODB_URI="mongodb+srv://javier:javier@cluster0.t5cgbal.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = AsyncIOMotorClient(MONGODB_URI)
db = client["videogame_db"]
def get_database():
    return db