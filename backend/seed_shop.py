import sqlite3
import uuid
import random
from database import DB_PATH

def generate_products():
    categories = ['Electronics', 'Gaming', 'Computers', 'Home', 'Clothing', 'Jewelry', 'Auto', 'Real Estate']
    adjectives = ['Premium', 'Pro', 'Ultra', 'Smart', 'Elite', 'Basic', 'Luxury', 'Eco']
    nouns = ['Device', 'System', 'Monitor', 'Station', 'Setup', 'Gear', 'Unit', 'Gadget']
    
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    c.execute('DELETE FROM products')
    
    products = []
    
    # Real ones
    real = [
        ('iPhone 15 Pro Max', 'Флагманский смартфон Apple, 256GB, Titanium', 120000.0, 'Electronics', 'https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/iphone-15-pro-max-natural-titanium-select?wid=470&hei=556&fmt=png-alpha', 'Вес: 221г\nЭкран: 6.7"\nПамять: 256GB'),
        ('PlayStation 5', 'Игровая консоль Sony PS5 с дисководом', 55000.0, 'Gaming', 'https://gmedia.playstation.com/is/image/SIEPDC/ps5-product-thumbnail-01-en-14sep21', 'Вес: 4.5кг\nПамять: 825GB SSD\nПоддержка 4K: Да'),
        ('MacBook Pro 14', 'Ноутбук Apple на чипе M3 Pro', 250000.0, 'Computers', 'https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/mbp14-spaceblack-select-202310?wid=904&hei=840&fmt=jpeg', 'Вес: 1.61кг\nЭкран: 14.2"\nRAM: 18GB'),
        ('Rolex Submariner', 'Премиальные швейцарские часы', 1250000.0, 'Jewelry', 'https://images.rolex.com/catalogue/images/upright-bba-with-shadow/m124060-0001.png', 'Материал: Oystersteel\nДиаметр: 41 мм\nВодонепроницаемость: 300 м'),
        ('Porsche 911', 'Спортивный автомобиль легендарной серии', 15000000.0, 'Auto', 'https://files.porsche.com/filestore/image/multimedia/none/992-c2-modelimage-sideshot/model/7622dcab-71ec-11eb-80d2-005056bbdc38/porsche-model.png', 'Мощность: 385 л.с.\nРазгон до 100: 4.2с\nМакс. скорость: 293 км/ч'),
    ]
    
    for r in real:
        products.append((str(uuid.uuid4()), r[0], r[1], r[2], r[3], r[4], r[5]))
        
    images = [
        'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500',
        'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500',
        'https://images.unsplash.com/photo-1572569432755-9ebf6d140e69?w=500',
        'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=500',
        'https://images.unsplash.com/photo-1618366712010-f4ae9c647dcb?w=500'
    ]
    
    # Generated ones
    for i in range(45):
        cat = random.choice(categories)
        name = f"{random.choice(adjectives)} {random.choice(nouns)} {random.randint(10, 99)}"
        price = round(random.uniform(500.0, 50000.0), 2)
        desc = f"Потрясающий товар в категории {cat}. Идеальный выбор для каждого."
        img = random.choice(images)
        specs = f"Категория: {cat}\nГод выпуска: 2024\nОценка: 5 звезд"
        products.append((str(uuid.uuid4()), name, desc, price, cat, img, specs))
        
    c.executemany('INSERT INTO products (id, name, description, price, category, image_url, specs) VALUES (?, ?, ?, ?, ?, ?, ?)', products)
    conn.commit()
    conn.close()
    print("50 products seeded successfully!")

if __name__ == "__main__":
    generate_products()
