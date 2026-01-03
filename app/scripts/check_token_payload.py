from jose import jwt
from app.config.settings import settings

token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwiZXhwIjoxNzY5NjAxMzM3fQ.RAwZsYG__EwA5-3oyUfLzcDE9DIAQJGWI809n_vbc8o'
ALGORITHM = "HS256"

try:
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
    print(f"PAYLOAD: {payload}")
except Exception as e:
    print(f"ERROR: {e}")
