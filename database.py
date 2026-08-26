import aiosqlite

DB_NAME = "real_estate.db"

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        # Ҷадвали хонаҳо
        await db.execute("""
            CREATE TABLE IF NOT EXISTS properties (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                photos TEXT,
                price REAL,
                city TEXT,
                address TEXT,
                rooms INTEGER,
                area REAL,
                description TEXT,
                type TEXT,
                contact TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Ҷадвали интихобшудаҳо (Favorites)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS favorites (
                user_id INTEGER,
                property_id INTEGER,
                PRIMARY KEY (user_id, property_id)
            )
        """)
        
        # Ҷадвали дархостҳо
        await db.execute("""
            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                username TEXT,
                full_name TEXT,
                property_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()

async def add_property(data: dict) -> int:
    async with aiosqlite.connect(DB_NAME) as db:
        photos_str = ",".join(data['photos'])
        cursor = await db.execute("""
            INSERT INTO properties (title, photos, price, city, address, rooms, area, description, type, contact)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data['title'], photos_str, data['price'], data['city'],
            data['address'], data['rooms'], data['area'],
            data['description'], data['type'], data['contact']
        ))
        await db.commit()
        return cursor.lastrowid

async def get_properties(city: str = None, max_price: float = None):
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        query = "SELECT * FROM properties WHERE 1=1"
        params = []
        
        if city:
            query += " AND (LOWER(city) LIKE ? OR LOWER(address) LIKE ?)"
            params.extend([f"%{city.lower()}%", f"%{city.lower()}%"])
        if max_price:
            query += " AND price <= ?"
            params.append(max_price)
            
        query += " ORDER BY id DESC"
        
        async with db.execute(query, params) as cursor:
            return await cursor.fetchall()

async def get_property_by_id(prop_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM properties WHERE id = ?", (prop_id,)) as cursor:
            return await cursor.fetchone()

async def delete_property_db(prop_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("DELETE FROM properties WHERE id = ?", (prop_id,))
        await db.execute("DELETE FROM favorites WHERE property_id = ?", (prop_id,))
        await db.commit()

async def toggle_favorite(user_id: int, prop_id: int) -> bool:
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT 1 FROM favorites WHERE user_id = ? AND property_id = ?", (user_id, prop_id)) as cursor:
            exists = await cursor.fetchone()
            
        if exists:
            await db.execute("DELETE FROM favorites WHERE user_id = ? AND property_id = ?", (user_id, prop_id))
            await db.commit()
            return False
        else:
            await db.execute("INSERT INTO favorites (user_id, property_id) VALUES (?, ?)", (user_id, prop_id))
            await db.commit()
            return True

async def get_favorites(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT p.* FROM properties p
            JOIN favorites f ON p.id = f.property_id
            WHERE f.user_id = ?
            ORDER BY p.id DESC
        """, (user_id,)) as cursor:
            return await cursor.fetchall()

async def save_lead(user_id: int, username: str, full_name: str, prop_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            INSERT INTO leads (user_id, username, full_name, property_id)
            VALUES (?, ?, ?, ?)
        """, (user_id, username, full_name, prop_id))
        await db.commit()

async def get_stats():
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT COUNT(*) FROM properties") as c1:
            total_props = (await c1.fetchone())[0]
        async with db.execute("SELECT COUNT(*) FROM leads") as c2:
            total_leads = (await c2.fetchone())[0]
        return {"properties": total_props, "leads": total_leads}