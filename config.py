from mongoengine import connect
from models import User, Position
from werkzeug.security import generate_password_hash

# Połącz się z bazą danych MongoDB
connect('shopasistant')  # Zamień 'shopasistant' na nazwę swojej bazy danych

# Dane użytkownika
email = "patryk.skrzeta@gmail.com"
password = generate_password_hash("zaq1@WSX")
role = "admin"
is_admin = True
nickname = "kingofthejungle"
first_name = "patryk"
last_name = "skrzeta"
country = "poland"
user_description = "none informations given"

# Tworzenie listy pozycji (positions) z wymaganym polem description
positions = [
    Position(
        name="admin",
        color="red",
        fontweight="bold",
        backgroundcolor="#FFFFFF",
        description="Administrator of the system"
    ),
    Position(
        name="developer",
        color="blue",
        fontweight="normal",
        backgroundcolor="#EFEFEF",
        description="Developer responsible for coding"
    ),
    Position(
        name="god",
        color="gold",
        fontweight="bold",
        backgroundcolor="#FFD700",
        description="Highest ELO in the system"
    ),
]

# Tworzenie nowego użytkownika
new_user = User(
    email=email,
    password=password,
    role=role,
    is_admin=is_admin,
    nickname=nickname,
    first_name=first_name,
    last_name=last_name,
    country=country,
    positions=positions,  # Przekazanie pełnej listy pozycji
    user_description=user_description
)

# Zapisanie użytkownika do bazy danych
new_user.save()

print(f"User {nickname} added to the database.")