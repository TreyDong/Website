import json
import logging
import random
import string

import pymysql

from config import DB_CONFIG

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def generate_authorization_code(length=8):
    """Generate a random authorization code"""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def init_database():
    """Initialize database and tables"""
    try:
        # Connect to MySQL server
        connection = pymysql.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            charset='utf8mb4'
        )
        
        with connection.cursor() as cursor:
            # Create database if not exists
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
            cursor.execute(f"USE {DB_CONFIG['database']}")
            
            # Create record table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS record (
                    authorization_code VARCHAR(64) PRIMARY KEY,
                    single_read_time_seconds INTEGER NOT NULL,
                    run_time_config VARCHAR(128) NOT NULL,
                    config_method ENUM('bash', 'qrcode') NOT NULL,
                    user_info JSON,
                    is_active BOOLEAN DEFAULT TRUE,
                    last_validated_at TIMESTAMP NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    credentials JSON NOT NULL
                )
            """)
            
            # Create execution_log table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS execution_log (
                    log_id BIGINT AUTO_INCREMENT PRIMARY KEY,
                    authorization_code VARCHAR(64) NOT NULL,
                    start_time TIMESTAMP NOT NULL,
                    end_time TIMESTAMP NULL,
                    status ENUM('running', 'success', 'failure', 'invalid_credentials') NOT NULL,
                    details TEXT,
                    FOREIGN KEY (authorization_code) REFERENCES record(authorization_code)
                )
            """)
            
            # Create qrcode_sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS qrcode_sessions (
                    session_id VARCHAR(64) PRIMARY KEY,
                    status ENUM('pending', 'scanned', 'confirmed', 'expired') NOT NULL DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NOT NULL,
                    qrcode_data TEXT,
                    credentials JSON
                )
            """)
            
            # Create authorization_codes table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS authorization_codes (
                    code VARCHAR(64) PRIMARY KEY,
                    is_used BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    used_at TIMESTAMP NULL,
                    used_by VARCHAR(255) NULL
                )
            """)
            
            # Create system_log table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS system_log (
                    log_id BIGINT AUTO_INCREMENT PRIMARY KEY,
                    level VARCHAR(10) NOT NULL,
                    message TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    context JSON
                )
            """)
            
            # Generate initial authorization codes if needed
            cursor.execute("SELECT COUNT(*) FROM authorization_codes WHERE is_used = FALSE")
            result = cursor.fetchone()
            available_codes = result[0] if result else 0
            
            if available_codes < 1000:
                codes_to_generate = 1000 - available_codes
                logger.info(f"Generating {codes_to_generate} new authorization codes")
                
                new_codes = [(generate_authorization_code(),) for _ in range(codes_to_generate)]
                cursor.executemany(
                    "INSERT IGNORE INTO authorization_codes (code) VALUES (%s)",
                    new_codes
                )
                
                logger.info(f"Generated {len(new_codes)} new authorization codes")
            
        connection.commit()
        logger.info("Database and tables created successfully!")
        
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise


def log_system_event(level, message, context=None):
    """Log system events to the database"""
    try:
        connection = pymysql.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_CONFIG['database'],
            charset='utf8mb4'
        )
        
        with connection.cursor() as cursor:
            sql = """
                INSERT INTO system_log 
                (level, message, context)
                VALUES (%s, %s, %s)
            """
            cursor.execute(sql, (
                level,
                message,
                json.dumps(context) if context else None
            ))
            
        connection.commit()
        
    except Exception as e:
        logger.error(f"Error logging system event: {str(e)}")

def check_authorization_code(code):
    """Check if an authorization code is valid and mark it as used"""
    try:
        connection = pymysql.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_CONFIG['database'],
            charset='utf8mb4'
        )
        
        with connection.cursor() as cursor:
            # Check if code exists and is unused
            cursor.execute("""
                SELECT code FROM authorization_codes 
                WHERE code = %s AND is_used = FALSE
            """, (code,))
            
            result = cursor.fetchone()
            
            if result:
                # Mark code as used
                cursor.execute("""
                    UPDATE authorization_codes 
                    SET is_used = TRUE, used_at = CURRENT_TIMESTAMP
                    WHERE code = %s
                """, (code,))
                
                connection.commit()
                log_system_event('INFO', f'Authorization code {code} used')
                
                # Generate new code to maintain count
                new_code = generate_authorization_code()
                cursor.execute(
                    "INSERT INTO authorization_codes (code) VALUES (%s)",
                    (new_code,)
                )
                connection.commit()
                
                return True
                
            return False
            
    except Exception as e:
        logger.error(f"Error checking authorization code: {str(e)}")
        return False

if __name__ == "__main__":
    init_database() 