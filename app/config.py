from dotenv import load_dotenv
import os

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

CLOUDINARY_NAME=os.getenv("CLOUDINARY_NAME")
CLOUDINARY_API_KEY=os.getenv("CLOUDINARY_API_KEY")
CLOUDINARY_API_SECRET=os.getenv("CLOUDINARY_API_SECRET")


GEMINI_API_KEY=os.getenv("GEMINI_API_KEY")
