import requests
import json
import time

BASE_URL = "http://127.0.0.1:8080/api"

def test_api():
    print("1. Регистрация Ивана...")
    r = requests.post(f"{BASE_URL}/register", json={"username": "ivan", "password": "123"})
    print(r.json())
    
    print("\n2. Регистрация Петра...")
    r = requests.post(f"{BASE_URL}/register", json={"username": "petr", "password": "123"})
    print(r.json())
    
    print("\n3. Вход Ивана...")
    r = requests.post(f"{BASE_URL}/login", json={"username": "ivan", "password": "123"})
    data = r.json()
    print(data)
    ivan_id = data.get("user_id")
    
    if not ivan_id:
        print("Не удалось войти")
        return
        
    print("\n4. Проверка баланса Ивана...")
    r = requests.get(f"{BASE_URL}/balance/{ivan_id}")
    print(r.json())
    
    print("\n5. Обычный перевод Петру (1000 руб)...")
    tx1 = {"sender_id": ivan_id, "receiver_username": "petr", "amount": 1000.0}
    r = requests.post(f"{BASE_URL}/transfer", json=tx1)
    print("Status:", r.status_code)
    print(r.json())

    # Попытаемся сделать подозрительный перевод (очень большая сумма или специфичные данные)
    # Так как мы не знаем точно, на что сработает модель при нулях, попробуем огромную сумму.
    print("\n6. Подозрительный перевод Петру (999999 руб)...")
    tx2 = {"sender_id": ivan_id, "receiver_username": "petr", "amount": 999999.0}
    r = requests.post(f"{BASE_URL}/transfer", json=tx2)
    print("Status:", r.status_code)
    print(r.json())
    
if __name__ == "__main__":
    test_api()
