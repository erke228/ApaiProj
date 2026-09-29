from flask import Flask, request, jsonify
from database import create_user, get_user, get_user_by_name, get_balance, process_transfer
from external_api import get_models, score_record

app = Flask(__name__)

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json(force=True)
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({"error": "Требуется username и password"}), 400
        
    user_id, error = create_user(username, password)
    if error:
        return jsonify({"error": error}), 400
        
    return jsonify({"message": "Пользователь успешно зарегистрирован", "user_id": user_id}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json(force=True)
    username = data.get('username')
    password = data.get('password')
    
    user = get_user(username, password)
    if not user:
        return jsonify({"error": "Неверный логин или пароль"}), 401
        
    return jsonify({"message": "Успешный вход", "user_id": user['id'], "username": user['username'], "has_pin": bool(user.get('pin'))}), 200

from database import set_pin, verify_pin, get_user_by_id

@app.route('/api/pin/set', methods=['POST'])
def setup_pin():
    data = request.get_json(force=True)
    set_pin(data['user_id'], data['pin'])
    return jsonify({"message": "PIN установлен"}), 200

@app.route('/api/pin/verify', methods=['POST'])
def check_pin():
    data = request.get_json(force=True)
    if verify_pin(data['user_id'], data['pin']):
        return jsonify({"message": "OK"}), 200
    return jsonify({"error": "Неверный PIN"}), 401

@app.route('/api/profile/<user_id>', methods=['GET'])
def profile(user_id):
    user = get_user_by_id(user_id)
    if not user:
        return jsonify({"error": "Not found"}), 404
    return jsonify({"username": user['username']}), 200

@app.route('/api/accounts/<user_id>', methods=['GET'])
def accounts(user_id):
    accs = db.get_accounts(user_id)
    return jsonify({"accounts": accs})

@app.route('/api/balance/<user_id>', methods=['GET'])
def balance(user_id):
    bal = get_balance(user_id)
    if bal is None:
        return jsonify({"error": "Пользователь не найден"}), 404
        
    return jsonify({"user_id": user_id, "balance": bal}), 200

from database import get_user_transactions

@app.route('/api/transactions/<user_id>', methods=['GET'])
def get_transactions(user_id):
    txs = get_user_transactions(user_id)
    return jsonify(txs), 200

@app.route('/api/transfer', methods=['POST'])
def transfer():
    data = request.get_json(force=True)
    sender_id = data.get('sender_id')
    receiver_username = data.get('receiver_username')
    amount = data.get('amount')
    
    if not sender_id or not receiver_username or not amount:
        return jsonify({"error": "Требуется sender_id, receiver_username и amount"}), 400
        
    try:
        amount = float(amount)
    except ValueError:
        return jsonify({"error": "Неверный формат суммы"}), 400
        
    if amount <= 0:
        return jsonify({"error": "Сумма должна быть больше 0"}), 400
        
    # Находим получателя
    receiver = get_user_by_name(receiver_username)
    if not receiver:
        return jsonify({"error": f"Получатель с именем {receiver_username} не найден"}), 404
        
    receiver_id = receiver['id']
    
    # === ИНТЕГРАЦИЯ С DEFENDER (ML АНТИФРОД) ===
    # Подготавливаем данные для ML модели. Модель обучена на определенных фичах.
    # Если мы передадим только Amount, остальные она заполнит нулями (логика в external_api.py).
    record_for_ml = {
        "Amount": amount,
        # В реальном приложении сюда можно добавить устройство, геолокацию, историю и т.д.
        "is_mobile_app": 1
    }
    
    # Загружаем модели (по умолчанию используется датасет creditcard)
    models = get_models("creditcard")
    
    if not models:
        return jsonify({"error": "Модели ML не загружены. Проверьте папку models."}), 500
        
    # Определяем имена признаков
    sample = next(iter(models.values()))
    if hasattr(sample, "feature_names_in_"):
        feature_names = list(sample.feature_names_in_)
    elif hasattr(sample, "steps"):
        last = sample.steps[-1][1]
        feature_names = list(getattr(last, "feature_names_in_", []))
    else:
        feature_names = []
        
    # Оцениваем транзакцию нейросетью
    ml_result = score_record(record_for_ml, models, feature_names)
    is_fraud = (ml_result["verdict"] == "FRAUD")
    fraud_prob = ml_result["ml_avg_prob"]
    
    # Обрабатываем перевод в базе данных
    success, message = process_transfer(sender_id, receiver_id, amount, is_fraud, fraud_prob)
    
    if not success:
        return jsonify({"error": message, "ml_verdict": ml_result["verdict"], "ml_prob": fraud_prob}), 400
        
    return jsonify({
        "message": message,
        "ml_verdict": ml_result["verdict"], 
        "ml_prob": fraud_prob
    }), 200

# ================= SUPERAAP ENDPOINTS =================

from database import get_all_products, apply_loan

@app.route('/api/shop/products', methods=['GET'])
def get_products():
    return jsonify(get_all_products()), 200

from database import buy_product

@app.route('/api/shop/buy', methods=['POST'])
def buy_item():
    data = request.get_json(force=True)
    success, msg = buy_product(data.get('user_id'), data.get('product_id'))
    if not success: return jsonify({"error": msg}), 400
    return jsonify({"message": msg}), 200

@app.route('/api/loans/apply', methods=['POST'])
def get_loan():
    data = request.get_json(force=True)
    user_id = data.get('user_id')
    amount = float(data.get('amount', 0))
    
    if amount <= 0:
        return jsonify({"error": "Сумма должна быть больше нуля"}), 400
        
    # Имитация проверки ИИ (скоринг)
    # Если сумма больше 1 млн, ИИ может отказать
    if amount > 1000000:
        return jsonify({"error": "В кредите отказано (Низкий скоринг балл)"}), 400
        
    success, message = apply_loan(user_id, amount, 0.15) # 15% ставка
    if not success:
        return jsonify({"error": message}), 500
        
    return jsonify({"message": message}), 200

# ================= ULTIMATE SUPERAPP ENDPOINTS =================

from database import buy_investment, send_message, get_stories, get_fines

@app.route('/api/investments/buy', methods=['POST'])
def buy_inv():
    data = request.get_json(force=True)
    success, msg = buy_investment(data.get('user_id'), data.get('ticker'), data.get('amount'), data.get('price'))
    if not success: return jsonify({"error": msg}), 400
    return jsonify({"message": msg}), 200

@app.route('/api/chat/send', methods=['POST'])
def chat_send():
    data = request.get_json(force=True)
    success, msg = send_message(data.get('sender_id'), data.get('receiver_id'), data.get('text'), data.get('is_money', False), data.get('amount', 0.0))
    if not success: return jsonify({"error": msg}), 400
    return jsonify({"message": msg}), 200

@app.route('/api/stories', methods=['GET'])
def stories():
    return jsonify(get_stories()), 200

@app.route('/api/gov/fines/<user_id>', methods=['GET'])
def fines(user_id):
    return jsonify(get_fines(user_id)), 200

from database import get_assets, get_portfolio, buy_asset

@app.route('/api/assets', methods=['GET'])
def get_all_assets():
    return jsonify(get_assets()), 200

@app.route('/api/portfolio/<user_id>', methods=['GET'])
def get_user_portfolio(user_id):
    return jsonify(get_portfolio(user_id)), 200

@app.route('/api/assets/buy', methods=['POST'])
def buy_user_asset():
    data = request.get_json(force=True)
    success, msg = buy_asset(data['user_id'], data['ticker'], data['amount'])
    if success:
        return jsonify({"message": msg}), 200
    return jsonify({"error": msg}), 400

@app.route('/api/chat', methods=['POST'])
def ai_chat():
    data = request.get_json(force=True)
    msg = data.get('message', '').lower()
    
    response = "Я пока только учусь! Попробуйте спросить: 'Баланс', 'Инвестиции', 'Траты', 'Копилка', 'Кредит' или 'Курс'."
    
    if 'баланс' in msg or 'balance' in msg:
        response = "Вы можете свайпать карточки на главной странице, чтобы увидеть все ваши счета: Основной, Копилка, Кредитка и Евро!"
    elif 'инвест' in msg or 'invest' in msg:
        response = "Сейчас отличное время для инвестиций. Загляните на вкладку 'My Portfolio', там теперь хранятся все ваши купленные акции!"
    elif 'трат' in msg or 'spend' in msg:
        response = "Ваши траты в норме, но вы стали больше заглядывать в Marketplace. Кстати, там теперь 50+ товаров и можно оставлять отзывы!"
    elif 'привет' in msg or 'hello' in msg:
        response = "Привет! Я ваш финансовый AI-ассистент Defender. Я знаю всё о ваших счетах. Чем могу помочь?"
    elif 'курс' in msg or 'обмен' in msg or 'rate' in msg:
        response = "В приложении работает обмен валют! Просто нажмите 'Exchange' на главной и конвертируйте USD в EUR по живому курсу."
    elif 'копилк' in msg or 'saving' in msg:
        response = "Ваша Копилка (Savings Vault) приносит вам 20% годовых! Это невероятная доходность."
    elif 'кредит' in msg or 'credit' in msg:
        response = "Мы открыли вам кредитную линию на $10,000! Тратьте с умом 😉"
    elif 'магазин' in msg or 'shop' in msg:
        response = "Я только что добавил 50 новых товаров! Там есть машины, квартиры, техника и часы Rolex. Можете искать по названию или категории."
    elif 'аватар' in msg or 'фото' in msg:
        response = "Перейдите в профиль (иконка внизу справа) и нажмите на свое фото — оно обновится!"
    
    return jsonify({"response": response}), 200

if __name__ == '__main__':
    print("Запуск Banking API с антифродом Defender на порту 8080...")
    app.run(host='0.0.0.0', port=8080, debug=True)
