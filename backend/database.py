import sqlite3
import uuid
from pathlib import Path

DB_PATH = Path(__file__).parent / "bank.db"

def get_connection():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row  # Return dict-like rows
    return conn

def init_db():
    conn = get_connection()
    c = conn.cursor()
    
    # Таблица пользователей
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            pin TEXT
        )
    ''')
    try:
        c.execute('ALTER TABLE users ADD COLUMN pin TEXT')
    except:
        pass
    
    # Таблица счетов (балансов)
    c.execute('''
        CREATE TABLE IF NOT EXISTS accounts (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            type TEXT NOT NULL DEFAULT 'MAIN',
            balance REAL NOT NULL DEFAULT 0.0,
            credit_limit REAL DEFAULT 0.0,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    try:
        c.execute('ALTER TABLE accounts ADD COLUMN type TEXT DEFAULT "MAIN"')
        c.execute('ALTER TABLE accounts ADD COLUMN credit_limit REAL DEFAULT 0.0')
    except:
        pass
    
    # Отзывы на товары
    c.execute('''
        CREATE TABLE IF NOT EXISTS product_comments (
            id TEXT PRIMARY KEY,
            product_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            username TEXT NOT NULL,
            text TEXT NOT NULL,
            rating INTEGER DEFAULT 5,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Таблица транзакций
    c.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id TEXT PRIMARY KEY,
            sender_id TEXT,
            receiver_id TEXT,
            amount REAL NOT NULL,
            status TEXT NOT NULL, 
            ml_verdict TEXT,
            ml_prob REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 🛒 Маркетплейс: Товары
    c.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL,
            category TEXT,
            image_url TEXT,
            specs TEXT
        )
    ''')
    try:
        c.execute('ALTER TABLE products ADD COLUMN category TEXT')
        c.execute('ALTER TABLE products ADD COLUMN image_url TEXT')
        c.execute('ALTER TABLE products ADD COLUMN specs TEXT')
    except:
        pass

    # 📈 Биржа: Активы
    c.execute('''
        CREATE TABLE IF NOT EXISTS assets (
            ticker TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            current_price REAL NOT NULL,
            is_crypto BOOLEAN NOT NULL
        )
    ''')

    # Портфель пользователя
    c.execute('''
        CREATE TABLE IF NOT EXISTS user_portfolio (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            ticker TEXT NOT NULL,
            amount REAL NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(ticker) REFERENCES assets(ticker)
        )
    ''')
    
    # 📦 Логистика и Заказы
    c.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            product_id TEXT NOT NULL,
            amount REAL NOT NULL,
            status TEXT NOT NULL DEFAULT 'CREATED', -- CREATED, PAID, SHIPPED, DELIVERED
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(product_id) REFERENCES products(id)
        )
    ''')
    
    # 💳 Кредиты и рассрочка
    c.execute('''
        CREATE TABLE IF NOT EXISTS loans (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            amount REAL NOT NULL,
            interest_rate REAL NOT NULL,
            remaining_balance REAL NOT NULL,
            status TEXT NOT NULL DEFAULT 'ACTIVE',
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    
    # 📄 Документооборот
    c.execute('''
        CREATE TABLE IF NOT EXISTS documents (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            title TEXT NOT NULL,
            pdf_url TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    
    # 📈 Инвестиции (Акции, Крипта)
    c.execute('''
        CREATE TABLE IF NOT EXISTS investments (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            ticker TEXT NOT NULL,
            amount REAL NOT NULL,
            buy_price REAL NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    
    # 💬 Мессенджер
    c.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id TEXT PRIMARY KEY,
            sender_id TEXT NOT NULL,
            receiver_id TEXT NOT NULL,
            text TEXT,
            is_money_transfer BOOLEAN DEFAULT 0,
            amount REAL DEFAULT 0.0,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(sender_id) REFERENCES users(id),
            FOREIGN KEY(receiver_id) REFERENCES users(id)
        )
    ''')
    
    # ✈️ Тревел и Услуги
    c.execute('''
        CREATE TABLE IF NOT EXISTS services (
            id TEXT PRIMARY KEY,
            type TEXT NOT NULL, -- flight, cinema, hotel
            title TEXT NOT NULL,
            price REAL NOT NULL
        )
    ''')
    
    # 🛡️ Страхование
    c.execute('''
        CREATE TABLE IF NOT EXISTS insurance (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            type TEXT NOT NULL, -- auto, life, travel
            valid_until DATETIME NOT NULL,
            pdf_url TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    
    # 🏛️ Госуслуги и Штрафы
    c.execute('''
        CREATE TABLE IF NOT EXISTS gov_fines (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            description TEXT NOT NULL,
            amount REAL NOT NULL,
            is_paid BOOLEAN DEFAULT 0,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    
    # 📱 Сториз
    c.execute('''
        CREATE TABLE IF NOT EXISTS stories (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            image_url TEXT
        )
    ''')

    # Добавим тестового пользователя с балансом
    c.execute('SELECT count(*) FROM users WHERE id = ?', ('test_user_id',))
    if c.fetchone()[0] == 0:
        c.execute('INSERT INTO users (id, username, password) VALUES (?, ?, ?)', ('test_user_id', 'TestUser', 'password123'))
        c.execute('INSERT INTO accounts (id, user_id, type, balance, credit_limit) VALUES (?, ?, ?, ?, ?)', (str(uuid.uuid4()), 'test_user_id', 'MAIN', 5000.0, 0.0))
        c.execute('INSERT INTO accounts (id, user_id, type, balance, credit_limit) VALUES (?, ?, ?, ?, ?)', (str(uuid.uuid4()), 'test_user_id', 'SAVINGS', 15000.0, 0.0))
        c.execute('INSERT INTO accounts (id, user_id, type, balance, credit_limit) VALUES (?, ?, ?, ?, ?)', (str(uuid.uuid4()), 'test_user_id', 'CREDIT', 0.0, 10000.0))
        c.execute('INSERT INTO accounts (id, user_id, type, balance, credit_limit) VALUES (?, ?, ?, ?, ?)', (str(uuid.uuid4()), 'test_user_id', 'EUR', 1000.0, 0.0))

    # Добавим тестовый товар, если таблица пустая
    c.execute('SELECT count(*) FROM products')
    if c.fetchone()[0] < 5:
        c.execute('DELETE FROM products') # очистим старые
        prods = [
            (str(uuid.uuid4()), 'iPhone 15 Pro Max', 'Флагманский смартфон Apple, 256GB, Titanium', 120000.0, 'Electronics', 'https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/iphone-15-pro-max-natural-titanium-select?wid=470&hei=556&fmt=png-alpha', 'Вес: 221г\nЭкран: 6.7"\nПамять: 256GB'),
            (str(uuid.uuid4()), 'PlayStation 5', 'Игровая консоль Sony PS5 с дисководом', 55000.0, 'Gaming', 'https://gmedia.playstation.com/is/image/SIEPDC/ps5-product-thumbnail-01-en-14sep21', 'Вес: 4.5кг\nПамять: 825GB SSD\nПоддержка 4K: Да'),
            (str(uuid.uuid4()), 'AirPods Pro 2', 'Беспроводные наушники с шумоподавлением', 25000.0, 'Electronics', 'https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/MQD83?wid=572&hei=572&fmt=jpeg', 'Вес: 5.3г\nАвтономность: 6 часов\nШумоподавление: Active'),
            (str(uuid.uuid4()), 'MacBook Pro 14', 'Ноутбук Apple на чипе M3 Pro', 250000.0, 'Computers', 'https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/mbp14-spaceblack-select-202310?wid=904&hei=840&fmt=jpeg', 'Вес: 1.61кг\nЭкран: 14.2"\nRAM: 18GB'),
            (str(uuid.uuid4()), 'Dyson V15 Detect', 'Беспроводной пылесос с лазерной подсветкой', 75000.0, 'Home', 'https://dyson-h.assetsadobe2.com/is/image/content/dam/dyson/images/products/primary/369362-01.png', 'Вес: 3кг\nМощность: 240 Вт\nОбъем пылесборника: 0.76л'),
            (str(uuid.uuid4()), 'Nike Air Max 270', 'Кроссовки для бега и повседневной носки', 15000.0, 'Clothing', 'https://static.nike.com/a/images/t_default/c4939b4b-74b8-4c91-959c-6828555e09f1/air-max-270-mens-shoes-KkLcGR.png', 'Размер: 42 (EU)\nЦвет: Черный\nМатериал: Текстиль'),
            (str(uuid.uuid4()), 'Samsung Galaxy S24 Ultra', 'Смартфон с AI функциями и стилусом S Pen', 135000.0, 'Electronics', 'https://images.samsung.com/is/image/samsung/p6pim/ru/2401/gallery/ru-galaxy-s24-s928-sm-s928bzkcser-539527635', 'Вес: 232г\nЭкран: 6.8"\nКамера: 200 МП'),
            (str(uuid.uuid4()), 'Rolex Submariner', 'Премиальные швейцарские часы', 1250000.0, 'Jewelry', 'https://images.rolex.com/catalogue/images/upright-bba-with-shadow/m124060-0001.png', 'Материал: Oystersteel\nДиаметр: 41 мм\nВодонепроницаемость: 300 м')
        ]
        c.executemany('INSERT INTO products (id, name, description, price, category, image_url, specs) VALUES (?, ?, ?, ?, ?, ?, ?)', prods)
        
    c.execute('SELECT count(*) FROM assets')
    if c.fetchone()[0] == 0:
        assets = [
            ('BTC', 'Bitcoin', 64500.0, True),
            ('ETH', 'Ethereum', 3400.0, True),
            ('AAPL', 'Apple Inc.', 175.50, False),
            ('TSLA', 'Tesla Inc.', 180.20, False),
            ('NVDA', 'NVIDIA Corp.', 850.0, False)
        ]
        c.executemany('INSERT INTO assets (ticker, name, current_price, is_crypto) VALUES (?, ?, ?, ?)', assets)

    c.execute('SELECT count(*) FROM stories')
    if c.fetchone()[0] == 0:
        stories = [
            (str(uuid.uuid4()), 'Apple -5%', 'Акции Apple упали на 5% после презентации. Отличный момент для покупки!', 'https://images.unsplash.com/photo-1611186871348-b1ce696e52c9?w=500'),
            (str(uuid.uuid4()), 'Кешбэк 10%', 'В этом месяце вы получаете 10% кешбэка на все покупки в категории "Электроника".', 'https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?w=500'),
            (str(uuid.uuid4()), 'Cyber Sec', 'Как защитить свои деньги от мошенников? Никогда не сообщайте PIN-код третьим лицам.', 'https://images.unsplash.com/photo-1614064641913-6b20ce238515?w=500')
        ]
        c.executemany('INSERT INTO stories (id, title, content, image_url) VALUES (?, ?, ?, ?)', stories)

    conn.commit()
    conn.close()

def get_assets():
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM assets')
    assets = [dict(row) for row in c.fetchall()]
    conn.close()
    return assets

def get_portfolio(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        SELECT p.ticker, p.amount, a.name, a.current_price, a.is_crypto 
        FROM user_portfolio p
        JOIN assets a ON p.ticker = a.ticker
        WHERE p.user_id = ?
    ''', (user_id,))
    portfolio = [dict(row) for row in c.fetchall()]
    conn.close()
    return portfolio

def buy_asset(user_id, ticker, amount):
    conn = get_connection()
    c = conn.cursor()
    # Получим цену
    c.execute('SELECT current_price FROM assets WHERE ticker = ?', (ticker,))
    asset = c.fetchone()
    if not asset: return False, "Актив не найден"
    
    total_cost = asset['current_price'] * amount
    
    # Спишем с баланса
    c.execute('SELECT balance FROM accounts WHERE user_id = ?', (user_id,))
    acc = c.fetchone()
    if not acc or acc['balance'] < total_cost:
        return False, "Недостаточно средств"
        
    c.execute('UPDATE accounts SET balance = balance - ? WHERE user_id = ?', (total_cost, user_id))
    
    # Добавим в портфель
    c.execute('SELECT id, amount FROM user_portfolio WHERE user_id = ? AND ticker = ?', (user_id, ticker))
    port = c.fetchone()
    if port:
        c.execute('UPDATE user_portfolio SET amount = amount + ? WHERE id = ?', (amount, port['id']))
    else:
        c.execute('INSERT INTO user_portfolio (id, user_id, ticker, amount) VALUES (?, ?, ?, ?)', 
                  (str(uuid.uuid4()), user_id, ticker, amount))
    
    # Запишем транзакцию
    record_transaction(user_id, 'STOCK_MARKET', total_cost, 'SUCCESS')
    conn.commit()
    conn.close()
    return True, "Успешная покупка"

def create_user(username, password, initial_balance=100000.0):
    conn = get_connection()
    c = conn.cursor()
    
    # Проверяем, есть ли уже такой пользователь
    c.execute('SELECT id FROM users WHERE username = ?', (username,))
    if c.fetchone():
        conn.close()
        return None, "Пользователь с таким именем уже существует"
        
    user_id = str(uuid.uuid4())
    account_id = str(uuid.uuid4())
    
    try:
        c.execute('INSERT INTO users (id, username, password) VALUES (?, ?, ?)', (user_id, username, password))
        c.execute('INSERT INTO accounts (id, user_id, type, balance, credit_limit) VALUES (?, ?, ?, ?, ?)', (str(uuid.uuid4()), user_id, 'MAIN', initial_balance, 0.0))
        c.execute('INSERT INTO accounts (id, user_id, type, balance, credit_limit) VALUES (?, ?, ?, ?, ?)', (str(uuid.uuid4()), user_id, 'SAVINGS', 0.0, 0.0))
        c.execute('INSERT INTO accounts (id, user_id, type, balance, credit_limit) VALUES (?, ?, ?, ?, ?)', (str(uuid.uuid4()), user_id, 'CREDIT', 0.0, 50000.0))
        c.execute('INSERT INTO accounts (id, user_id, type, balance, credit_limit) VALUES (?, ?, ?, ?, ?)', (str(uuid.uuid4()), user_id, 'EUR', 0.0, 0.0))
        conn.commit()
    except Exception as e:
        conn.rollback()
        conn.close()
        return None, str(e)
        
    conn.close()
    return user_id, None

def get_user(username, password):
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT id, username FROM users WHERE username = ? AND password = ?', (username, password))
    user = c.fetchone()
    conn.close()
    return dict(user) if user else None

def get_user_by_name(username):
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = c.fetchone()
    conn.close()
    return dict(user) if user else None

def get_user_by_id(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = c.fetchone()
    conn.close()
    return dict(user) if user else None

def set_pin(user_id, pin):
    conn = get_connection()
    c = conn.cursor()
    c.execute('UPDATE users SET pin = ? WHERE id = ?', (pin, user_id))
    conn.commit()
    conn.close()
    return True

def verify_pin(user_id, pin):
    user = get_user_by_id(user_id)
    return user is not None and user.get('pin') == pin

def get_balance(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT balance FROM accounts WHERE user_id = ? AND type = "MAIN"', (user_id,))
    account = c.fetchone()
    conn.close()
    return account['balance'] if account else None

def get_accounts(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM accounts WHERE user_id = ?', (user_id,))
    accounts = [dict(row) for row in c.fetchall()]
    conn.close()
    return accounts

def get_user_transactions(user_id, limit=10):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        SELECT t.*, 
               u1.username as sender_name, 
               u2.username as receiver_name 
        FROM transactions t
        LEFT JOIN users u1 ON t.sender_id = u1.id
        LEFT JOIN users u2 ON t.receiver_id = u2.id
        WHERE t.sender_id = ? OR t.receiver_id = ?
        ORDER BY t.timestamp DESC LIMIT ?
    ''', (user_id, user_id, limit))
    txs = [dict(row) for row in c.fetchall()]
    conn.close()
    return txs

def record_transaction(sender_id, receiver_id, amount, status, verdict="LEGIT", prob=0.0):
    tx_id = str(uuid.uuid4())
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        INSERT INTO transactions (id, sender_id, receiver_id, amount, status, ml_verdict, ml_prob)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (tx_id, sender_id, receiver_id, amount, status, verdict, prob))
    conn.commit()
    conn.close()
    return tx_id

def process_transfer(sender_id, receiver_id, amount, is_fraud, fraud_prob=0.0):
    """
    Основная логика перевода с проверкой на мошенничество.
    """
    if sender_id == receiver_id:
        return False, "Нельзя перевести деньги самому себе"
        
    conn = get_connection()
    c = conn.cursor()
    
    try:
        # Проверяем баланс отправителя
        c.execute('SELECT balance FROM accounts WHERE user_id = ?', (sender_id,))
        sender_acc = c.fetchone()
        
        if not sender_acc or sender_acc['balance'] < amount:
            return False, "Недостаточно средств"
            
        # Если Defender сказал, что это ФРОД - блокируем!
        if is_fraud:
            record_transaction(sender_id, receiver_id, amount, "BLOCKED", "FRAUD", fraud_prob)
            return False, "Операция заблокирована службой безопасности (Антифрод)"
            
        # Иначе - проводим перевод (LEGIT)
        # Списываем у отправителя
        c.execute('UPDATE accounts SET balance = balance - ? WHERE user_id = ?', (amount, sender_id))
        # Начисляем получателю
        c.execute('UPDATE accounts SET balance = balance + ? WHERE user_id = ?', (amount, receiver_id))
        
        conn.commit()
        # Записываем успешную транзакцию
        record_transaction(sender_id, receiver_id, amount, "COMPLETED", "LEGIT", fraud_prob)
        
    except Exception as e:
        conn.rollback()
        return False, f"Внутренняя ошибка: {str(e)}"
    finally:
        conn.close()
        
    return True, "Перевод успешно выполнен"

# Инициализируем БД при загрузке модуля
init_db()

def get_all_products():
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM products')
    products = [dict(row) for row in c.fetchall()]
    conn.close()
    return products

def buy_product(user_id, product_id):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute('SELECT price FROM products WHERE id = ?', (product_id,))
        product = c.fetchone()
        if not product:
            return False, "Товар не найден"
            
        c.execute('SELECT balance FROM accounts WHERE user_id = ?', (user_id,))
        acc = c.fetchone()
        if not acc or acc['balance'] < product['price']:
            return False, "Недостаточно средств"
            
        c.execute('UPDATE accounts SET balance = balance - ? WHERE user_id = ?', (product['price'], user_id))
        order_id = str(uuid.uuid4())
        c.execute('INSERT INTO orders (id, user_id, product_id, amount, status) VALUES (?, ?, ?, ?, ?)', 
                  (order_id, user_id, product_id, product['price'], 'PAID'))
        conn.commit()
    except Exception as e:
        conn.rollback()
        conn.close()
        return False, str(e)
    conn.close()
    return True, "Товар успешно оплачен"

def apply_loan(user_id, amount, interest_rate):
    conn = get_connection()
    c = conn.cursor()
    loan_id = str(uuid.uuid4())
    try:
        # Добавляем кредит
        c.execute('''
            INSERT INTO loans (id, user_id, amount, interest_rate, remaining_balance)
            VALUES (?, ?, ?, ?, ?)
        ''', (loan_id, user_id, amount, interest_rate, amount * (1 + interest_rate)))
        
        # Начисляем деньги на баланс (Кредит выдан)
        c.execute('UPDATE accounts SET balance = balance + ? WHERE user_id = ?', (amount, user_id))
        
        # Генерируем документ
        doc_id = str(uuid.uuid4())
        c.execute('''
            INSERT INTO documents (id, user_id, title, pdf_url)
            VALUES (?, ?, ?, ?)
        ''', (doc_id, user_id, f"Кредитный договор на {amount} руб", f"/static/docs/{doc_id}.pdf"))
        
        conn.commit()
    except Exception as e:
        conn.rollback()
        conn.close()
        return False, str(e)
    conn.close()
    return True, "Кредит одобрен, деньги зачислены на счет. Договор сформирован."

# --- Новые функции для Ultimate SuperApp ---

def buy_investment(user_id, ticker, amount, price):
    conn = get_connection()
    c = conn.cursor()
    total_cost = amount * price
    try:
        c.execute('SELECT balance FROM accounts WHERE user_id = ?', (user_id,))
        acc = c.fetchone()
        if not acc or acc['balance'] < total_cost:
            return False, "Недостаточно средств для покупки активов"
        
        c.execute('UPDATE accounts SET balance = balance - ? WHERE user_id = ?', (total_cost, user_id))
        c.execute('INSERT INTO investments (id, user_id, ticker, amount, buy_price) VALUES (?, ?, ?, ?, ?)',
                  (str(uuid.uuid4()), user_id, ticker, amount, price))
        conn.commit()
    except Exception as e:
        conn.rollback()
        conn.close()
        return False, str(e)
    conn.close()
    return True, f"Успешно куплено {amount} акций {ticker}"

def send_message(sender_id, receiver_id, text, is_money=False, amount=0.0):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute('INSERT INTO messages (id, sender_id, receiver_id, text, is_money_transfer, amount) VALUES (?, ?, ?, ?, ?, ?)',
                  (str(uuid.uuid4()), sender_id, receiver_id, text, is_money, amount))
        conn.commit()
    except Exception as e:
        conn.rollback()
        conn.close()
        return False, str(e)
    conn.close()
    return True, "Сообщение отправлено"

def get_stories():
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM stories')
    stories = [dict(row) for row in c.fetchall()]
    conn.close()
    return stories

def get_fines(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM gov_fines WHERE user_id = ? AND is_paid = 0', (user_id,))
    fines = [dict(row) for row in c.fetchall()]
    conn.close()
    return fines
