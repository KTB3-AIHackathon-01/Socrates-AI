import sqlite3
import json
from datetime import datetime
from pathlib import Path

DB_PATH = "./sqlite.db"

def init_db():
  """SQLite 데이터베이스 초기화"""
  Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
  
  conn = sqlite3.connect(DB_PATH)
  cursor = conn.cursor()
  
  # 학습 세션 테이블
  cursor.execute('''
      CREATE TABLE IF NOT EXISTS learning_sessions (
          session_id TEXT PRIMARY KEY,
          topic TEXT,
          created_at TEXT,
          updated_at TEXT,
          status TEXT
      )
  ''')
  
  # 메시지 테이블
  cursor.execute('''
      CREATE TABLE IF NOT EXISTS messages (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          session_id TEXT,
          role TEXT,
          content TEXT,
          timestamp TEXT,
          FOREIGN KEY (session_id) REFERENCES learning_sessions(session_id)
      )
  ''')
  
  # 체크포인트 테이블
  cursor.execute('''
      CREATE TABLE IF NOT EXISTS checkpoints (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          session_id TEXT,
          turn INTEGER,
          phase TEXT,
          progress REAL,
          misconceptions TEXT,
          attempt_count INTEGER,
          saved_at TEXT,
          FOREIGN KEY (session_id) REFERENCES learning_sessions(session_id)
      )
  ''')
  
  conn.commit()
  conn.close()

def save_checkpoint(session_id: str, turn: int, phase: str, progress: float, 
                   misconceptions: list, attempt_count: int):
  """체크포인트 저장"""
  conn = sqlite3.connect(DB_PATH)
  cursor = conn.cursor()
  
  cursor.execute('''
      INSERT INTO checkpoints 
      (session_id, turn, phase, progress, misconceptions, attempt_count, saved_at)
      VALUES (?, ?, ?, ?, ?, ?, ?)
  ''', (session_id, turn, phase, progress, json.dumps(misconceptions), 
        attempt_count, datetime.now().isoformat()))
  
  conn.commit()
  conn.close()

def save_message(session_id: str, role: str, content: str):
  """메시지 저장"""
  conn = sqlite3.connect(DB_PATH)
  cursor = conn.cursor()
  
  cursor.execute('''
      INSERT INTO messages (session_id, role, content, timestamp)
      VALUES (?, ?, ?, ?)
  ''', (session_id, role, content, datetime.now().isoformat()))
  
  conn.commit()
  conn.close()

def create_session(session_id: str, topic: str):
  """새로운 학습 세션 생성"""
  conn = sqlite3.connect(DB_PATH)
  cursor = conn.cursor()
  
  cursor.execute('''
      INSERT INTO learning_sessions (session_id, topic, created_at, updated_at, status)
      VALUES (?, ?, ?, ?, ?)
  ''', (session_id, topic, datetime.now().isoformat(), datetime.now().isoformat(), 'active'))
  
  conn.commit()
  conn.close()

# DB 초기화
init_db()