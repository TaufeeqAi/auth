import asyncio
import asyncpg
from passlib.context import CryptContext
import uuid
from datetime import datetime

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_tables():
    # Connect to the database
    conn = await asyncpg.connect('postgresql://postgres:elecon@localhost:5433/meetings_db')
    
    try:
        # Drop tables in correct order (dependent tables first)
        await conn.execute('DROP TABLE IF EXISTS audit_logs CASCADE')
        print("Audit logs table dropped successfully!")
    except Exception as e:
        print(f"Error dropping audit_logs table: {e}")
        
    try:
        # Drop user_sessions table
        await conn.execute('DROP TABLE IF EXISTS user_sessions CASCADE')
        print("User sessions table dropped successfully!")
    except Exception as e:
        print(f"Error dropping user_sessions table: {e}")
        
    try:
        # Drop refresh_tokens table
        await conn.execute('DROP TABLE IF EXISTS refresh_tokens CASCADE')
        print("Refresh tokens table dropped successfully!")
    except Exception as e:
        print(f"Error dropping refresh_tokens table: {e}")
        
    try:
        # Drop devices table
        await conn.execute('DROP TABLE IF EXISTS devices CASCADE')
        print("Devices table dropped successfully!")
    except Exception as e:
        print(f"Error dropping devices table: {e}")
        
    try:
        # Drop user_preferences table
        await conn.execute('DROP TABLE IF EXISTS user_preferences CASCADE')
        print("User preferences table dropped successfully!")
    except Exception as e:
        print(f"Error dropping user_preferences table: {e}")
        
    try:
        # Drop the enum type if it exists
        await conn.execute('DROP TYPE IF EXISTS userrole')
        print("Enum type 'userrole' dropped successfully!")
    except Exception as e:
        print(f"Error dropping enum type: {e}")
    
    try:
        # Drop the users table if it exists
        await conn.execute('DROP TABLE IF EXISTS users CASCADE')
        print("Users table dropped successfully!")
    except Exception as e:
        print(f"Error dropping users table: {e}")
    
    try:
        # Create the enum type for user roles
        await conn.execute('''
            CREATE TYPE userrole AS ENUM ('attendee', 'manager', 'admin')
        ''')
        print("Enum type 'userrole' created successfully!")
        
        # Create users table with UUID primary key
        await conn.execute('''
            CREATE TABLE users (
                id UUID PRIMARY KEY,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE,
                email VARCHAR(255) UNIQUE NOT NULL,
                username VARCHAR(100) UNIQUE,
                full_name VARCHAR(255),
                organization_name VARCHAR(255),
                department_id VARCHAR(100),
                password_hash VARCHAR(255),
                role userrole NOT NULL DEFAULT 'attendee',
                is_active BOOLEAN NOT NULL DEFAULT TRUE,
                is_verified BOOLEAN NOT NULL DEFAULT FALSE,
                google_id VARCHAR(255) UNIQUE,
                apple_id VARCHAR(255) UNIQUE,
                biometric_enabled BOOLEAN DEFAULT FALSE,
                biometric_public_key TEXT,
                avatar_url VARCHAR(500),
                phone_number VARCHAR(20),
                last_login TIMESTAMP WITH TIME ZONE
            )
        ''')
        print("Users table created successfully!")
        
        # Create indexes
        await conn.execute('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)')
        await conn.execute('CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)')
        await conn.execute('CREATE INDEX IF NOT EXISTS idx_users_google_id ON users(google_id)')
        await conn.execute('CREATE INDEX IF NOT EXISTS idx_users_apple_id ON users(apple_id)')
        await conn.execute('CREATE INDEX IF NOT EXISTS idx_users_phone_number ON users(phone_number)')
        
        # Create refresh_tokens table
        await conn.execute('''
            CREATE TABLE refresh_tokens (
                id UUID PRIMARY KEY,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE,
                user_id UUID NOT NULL,
                token_hash VARCHAR(64) UNIQUE NOT NULL,
                device_id VARCHAR(255) NOT NULL,
                expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
                last_used TIMESTAMP WITH TIME ZONE,
                is_active BOOLEAN NOT NULL DEFAULT TRUE,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        print("Refresh tokens table created successfully!")
        
        # Create devices table
        await conn.execute('''
            CREATE TABLE devices (
                id UUID PRIMARY KEY,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE,
                user_id UUID NOT NULL,
                device_id VARCHAR(255) NOT NULL,
                device_name VARCHAR(255),
                device_type VARCHAR(50),
                os_name VARCHAR(50),
                os_version VARCHAR(20),
                push_token VARCHAR(500),
                is_active BOOLEAN NOT NULL DEFAULT TRUE,
                last_seen TIMESTAMP WITH TIME ZONE,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        print("Devices table created successfully!")
        
        # Create user_preferences table
        await conn.execute('''
            CREATE TABLE user_preferences (
                id UUID PRIMARY KEY,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE,
                user_id UUID NOT NULL UNIQUE,
                language VARCHAR(10) NOT NULL DEFAULT 'en',
                timezone VARCHAR(50) NOT NULL DEFAULT 'UTC',
                notification_enabled BOOLEAN NOT NULL DEFAULT TRUE,
                email_notifications BOOLEAN NOT NULL DEFAULT TRUE,
                push_notifications BOOLEAN NOT NULL DEFAULT TRUE,
                meeting_reminders BOOLEAN NOT NULL DEFAULT TRUE,
                summary_frequency VARCHAR(20) NOT NULL DEFAULT 'daily',
                theme VARCHAR(20) NOT NULL DEFAULT 'light',
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        print("User preferences table created successfully!")
        
        print("All tables created successfully!")
        
        # Test inserting a user directly
        try:
            user_id = uuid.uuid4()
            hashed_password = pwd_context.hash("testpassword")
            await conn.execute('''
                INSERT INTO users (id, email, username, full_name, password_hash, role, is_active, is_verified)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            ''', str(user_id), 'test@example.com', 'testuser', 'Test User', hashed_password, 'attendee', True, False)
            print("Test user inserted successfully!")
        except Exception as e:
            print(f"Error inserting test user: {e}")
        
    except Exception as e:
        print(f"Error creating tables: {e}")
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(create_tables())