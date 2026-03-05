import sqlite3
from datetime import datetime
from typing import Optional, List, Dict, Tuple
import json

class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                name TEXT NOT NULL,
                age INTEGER NOT NULL,
                gender TEXT NOT NULL,
                looking_for TEXT NOT NULL,
                bio TEXT,
                photo_id TEXT,
                city TEXT,
                active INTEGER DEFAULT 1,
                min_age INTEGER DEFAULT 18,
                max_age INTEGER DEFAULT 100,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS likes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                from_user_id INTEGER NOT NULL,
                to_user_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(from_user_id, to_user_id),
                FOREIGN KEY (from_user_id) REFERENCES users(user_id),
                FOREIGN KEY (to_user_id) REFERENCES users(user_id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS matches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user1_id INTEGER NOT NULL,
                user2_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user1_id, user2_id),
                FOREIGN KEY (user1_id) REFERENCES users(user_id),
                FOREIGN KEY (user2_id) REFERENCES users(user_id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                from_user_id INTEGER NOT NULL,
                to_user_id INTEGER NOT NULL,
                message TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                read INTEGER DEFAULT 0,
                FOREIGN KEY (from_user_id) REFERENCES users(user_id),
                FOREIGN KEY (to_user_id) REFERENCES users(user_id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                stars_amount INTEGER NOT NULL,
                feature TEXT NOT NULL,
                payment_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS profile_views (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                viewer_id INTEGER NOT NULL,
                viewed_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (viewer_id) REFERENCES users(user_id),
                FOREIGN KEY (viewed_id) REFERENCES users(user_id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_statistics (
                user_id INTEGER PRIMARY KEY,
                total_views INTEGER DEFAULT 0,
                total_likes_sent INTEGER DEFAULT 0,
                total_likes_received INTEGER DEFAULT 0,
                total_matches INTEGER DEFAULT 0,
                total_messages_sent INTEGER DEFAULT 0,
                total_messages_received INTEGER DEFAULT 0,
                last_active TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_state (
                user_id INTEGER PRIMARY KEY,
                state TEXT,
                data TEXT,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_user(self, user_id: int, username: str, first_name: str, 
                   name: str, age: int, gender: str, looking_for: str, 
                   bio: str, photo_id: str = None, city: str = None):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO users 
            (user_id, username, first_name, name, age, gender, looking_for, bio, photo_id, city)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, username, first_name, name, age, gender, looking_for, bio, photo_id, city))
        conn.commit()
        conn.close()
    
    def get_user(self, user_id: int) -> Optional[Dict]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    def user_exists(self, user_id: int) -> bool:
        return self.get_user(user_id) is not None
    
    def get_candidates(self, user_id: int, limit: int = 1) -> List[Dict]:
        user = self.get_user(user_id)
        if not user:
            return []
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        min_age = user.get('min_age', 18)
        max_age = user.get('max_age', 100)
        
        cursor.execute('''
            SELECT * FROM users 
            WHERE user_id != ? 
            AND active = 1
            AND gender = ?
            AND age BETWEEN ? AND ?
            AND user_id NOT IN (
                SELECT to_user_id FROM likes WHERE from_user_id = ?
            )
            ORDER BY RANDOM()
            LIMIT ?
        ''', (user_id, user['looking_for'], min_age, max_age, user_id, limit))
        
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def add_like(self, from_user_id: int, to_user_id: int) -> bool:
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO likes (from_user_id, to_user_id)
                VALUES (?, ?)
            ''', (from_user_id, to_user_id))
            conn.commit()
            
            cursor.execute('''
                SELECT COUNT(*) as count FROM likes 
                WHERE from_user_id = ? AND to_user_id = ?
            ''', (to_user_id, from_user_id))
            
            is_match = cursor.fetchone()['count'] > 0
            
            if is_match:
                user1_id = min(from_user_id, to_user_id)
                user2_id = max(from_user_id, to_user_id)
                cursor.execute('''
                    INSERT OR IGNORE INTO matches (user1_id, user2_id)
                    VALUES (?, ?)
                ''', (user1_id, user2_id))
                conn.commit()
            
            conn.close()
            return is_match
        except sqlite3.IntegrityError:
            conn.close()
            return False
    
    def get_matches(self, user_id: int) -> List[Dict]:
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT u.* FROM users u
            INNER JOIN matches m ON (
                (m.user1_id = ? AND m.user2_id = u.user_id) OR
                (m.user2_id = ? AND m.user1_id = u.user_id)
            )
            ORDER BY m.created_at DESC
        ''', (user_id, user_id))
        
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def is_match(self, user1_id: int, user2_id: int) -> bool:
        conn = self.get_connection()
        cursor = conn.cursor()
        
        user_a = min(user1_id, user2_id)
        user_b = max(user1_id, user2_id)
        
        cursor.execute('''
            SELECT COUNT(*) as count FROM matches 
            WHERE user1_id = ? AND user2_id = ?
        ''', (user_a, user_b))
        
        result = cursor.fetchone()['count'] > 0
        conn.close()
        return result
    
    def save_message(self, from_user_id: int, to_user_id: int, message: str):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO messages (from_user_id, to_user_id, message)
            VALUES (?, ?, ?)
        ''', (from_user_id, to_user_id, message))
        conn.commit()
        conn.close()
    
    def get_messages(self, user1_id: int, user2_id: int, limit: int = 50) -> List[Dict]:
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM messages 
            WHERE (from_user_id = ? AND to_user_id = ?) 
               OR (from_user_id = ? AND to_user_id = ?)
            ORDER BY created_at DESC
            LIMIT ?
        ''', (user1_id, user2_id, user2_id, user1_id, limit))
        
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in reversed(rows)]
    
    def get_who_liked_me(self, user_id: int) -> List[Dict]:
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT u.* FROM users u
            INNER JOIN likes l ON l.from_user_id = u.user_id
            WHERE l.to_user_id = ?
            AND NOT EXISTS (
                SELECT 1 FROM likes 
                WHERE from_user_id = ? AND to_user_id = u.user_id
            )
            ORDER BY l.created_at DESC
        ''', (user_id, user_id))
        
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def add_payment(self, user_id: int, stars_amount: int, feature: str, payment_id: str = None):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO payments (user_id, stars_amount, feature, payment_id)
            VALUES (?, ?, ?, ?)
        ''', (user_id, stars_amount, feature, payment_id))
        conn.commit()
        conn.close()
    
    def has_paid_for_feature(self, user_id: int, feature: str) -> bool:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT COUNT(*) as count FROM payments 
            WHERE user_id = ? AND feature = ?
        ''', (user_id, feature))
        result = cursor.fetchone()['count'] > 0
        conn.close()
        return result
    
    def set_user_state(self, user_id: int, state: str, data: Dict = None):
        conn = self.get_connection()
        cursor = conn.cursor()
        data_json = json.dumps(data) if data else None
        cursor.execute('''
            INSERT OR REPLACE INTO user_state (user_id, state, data)
            VALUES (?, ?, ?)
        ''', (user_id, state, data_json))
        conn.commit()
        conn.close()
    
    def get_user_state(self, user_id: int) -> Tuple[Optional[str], Optional[Dict]]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT state, data FROM user_state WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            state = row['state']
            data = json.loads(row['data']) if row['data'] else None
            return state, data
        return None, None
    
    def clear_user_state(self, user_id: int):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM user_state WHERE user_id = ?', (user_id,))
        conn.commit()
        conn.close()
    
    def get_unread_count(self, user_id: int) -> int:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT COUNT(*) as count FROM messages 
            WHERE to_user_id = ? AND read = 0
        ''', (user_id,))
        result = cursor.fetchone()['count']
        conn.close()
        return result
    
    def mark_messages_read(self, user_id: int, from_user_id: int):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE messages SET read = 1 
            WHERE to_user_id = ? AND from_user_id = ?
        ''', (user_id, from_user_id))
        conn.commit()
        conn.close()
    
    def track_profile_view(self, viewer_id: int, viewed_id: int):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO profile_views (viewer_id, viewed_id)
            VALUES (?, ?)
        ''', (viewer_id, viewed_id))
        
        cursor.execute('''
            INSERT OR IGNORE INTO user_statistics (user_id, total_views)
            VALUES (?, 0)
        ''',(viewed_id,))
        
        cursor.execute('''
            UPDATE user_statistics 
            SET total_views = total_views + 1,
                last_active = CURRENT_TIMESTAMP
            WHERE user_id = ?
        ''', (viewed_id,))
        
        conn.commit()
        conn.close()
    
    def update_like_stats(self, from_user_id: int, to_user_id: int):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR IGNORE INTO user_statistics (user_id)
            VALUES (?)
        ''', (from_user_id,))
        
        cursor.execute('''
            INSERT OR IGNORE INTO user_statistics (user_id)
            VALUES (?)
        ''', (to_user_id,))
        
        cursor.execute('''
            UPDATE user_statistics 
            SET total_likes_sent = total_likes_sent + 1,
                last_active = CURRENT_TIMESTAMP
            WHERE user_id = ?
        ''', (from_user_id,))
        
        cursor.execute('''
            UPDATE user_statistics 
            SET total_likes_received = total_likes_received + 1
            WHERE user_id = ?
        ''', (to_user_id,))
        
        conn.commit()
        conn.close()
    
    def update_match_stats(self, user1_id: int, user2_id: int):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE user_statistics 
            SET total_matches = total_matches + 1
            WHERE user_id IN (?, ?)
        ''', (user1_id, user2_id))
        
        conn.commit()
        conn.close()
    
    def update_message_stats(self, from_user_id: int, to_user_id: int):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR IGNORE INTO user_statistics (user_id)
            VALUES (?)
        ''', (from_user_id,))
        
        cursor.execute('''
            UPDATE user_statistics 
            SET total_messages_sent = total_messages_sent + 1,
                last_active = CURRENT_TIMESTAMP
            WHERE user_id = ?
        ''', (from_user_id,))
        
        cursor.execute('''
            UPDATE user_statistics 
            SET total_messages_received = total_messages_received + 1
            WHERE user_id = ?
        ''', (to_user_id,))
        
        conn.commit()
        conn.close()
    
    def get_admin_stats(self) -> Dict:
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) as total FROM users')
        total_users = cursor.fetchone()['total']
        
        cursor.execute('SELECT COUNT(*) as total FROM matches')
        total_matches = cursor.fetchone()['total']
        
        cursor.execute('SELECT COUNT(*) as total FROM messages')
        total_messages = cursor.fetchone()['total']
        
        cursor.execute('SELECT COUNT(*) as total FROM payments')
        total_payments = cursor.fetchone()['total']
        
        cursor.execute('SELECT SUM(stars_amount) as total FROM payments')
        total_stars = cursor.fetchone()['total'] or 0
        
        cursor.execute('''
            SELECT COUNT(DISTINCT user_id) as total FROM users
            WHERE created_at >= datetime('now', '-24 hours')
        ''')
        new_users_24h = cursor.fetchone()['total']
        
        cursor.execute('''
            SELECT COUNT(DISTINCT user_id) as total FROM users
            WHERE created_at >= datetime('now', '-7 days')
        ''')
        new_users_7d = cursor.fetchone()['total']
        
        conn.close()
        
        return {
            'total_users': total_users,
            'total_matches': total_matches,
            'total_messages': total_messages,
            'total_payments': total_payments,
            'total_stars': total_stars,
            'new_users_24h': new_users_24h,
            'new_users_7d': new_users_7d
        }
    
    def get_top_users(self, limit: int = 10) -> List[Dict]:
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                u.user_id,
                u.name,
                u.age,
                u.city,
                s.total_views,
                s.total_likes_received,
                s.total_matches,
                CASE 
                    WHEN s.total_views > 0 
                    THEN ROUND(CAST(s.total_likes_received AS FLOAT) / s.total_views * 100, 2)
                    ELSE 0 
                END as like_rate
            FROM users u
            LEFT JOIN user_statistics s ON u.user_id = s.user_id
            WHERE s.total_views > 0
            ORDER BY like_rate DESC, s.total_likes_received DESC
            LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def get_user_stats(self, user_id: int) -> Optional[Dict]:
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM user_statistics WHERE user_id = ?
        ''', (user_id,))
        
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    def set_age_filter(self, user_id: int, min_age: int, max_age: int):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE users SET min_age = ?, max_age = ? WHERE user_id = ?
        ''', (min_age, max_age, user_id))
        conn.commit()
        conn.close()
