"""SQLite 日志存储层"""
import sqlite3
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path

from src.models.log_schemas import LLMLogEntry, Neo4jLogEntry, SystemLogEntry

logger = logging.getLogger(__name__)


class LogStorage:
    """SQLite 日志存储"""

    def __init__(self, db_path: str = "logs/app.db"):
        """
        初始化日志存储

        Args:
            db_path: 数据库文件路径
        """
        self.db_path = db_path
        self._ensure_db_exists()
        self._create_tables()

    def _ensure_db_exists(self):
        """确保数据库目录存在"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

    def _get_connection(self) -> sqlite3.Connection:
        """获取数据库连接"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # 返回字典格式
        return conn

    def _create_tables(self):
        """创建日志表"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()

            # LLM 日志表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS llm_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    log_type TEXT NOT NULL,
                    model TEXT NOT NULL,
                    request_messages TEXT,
                    response_content TEXT,
                    response_model TEXT,
                    prompt_tokens INTEGER,
                    completion_tokens INTEGER,
                    total_tokens INTEGER,
                    temperature REAL,
                    max_tokens INTEGER,
                    duration_ms REAL,
                    success BOOLEAN NOT NULL,
                    error_message TEXT
                )
            """)

            # Neo4j 日志表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS neo4j_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    log_type TEXT NOT NULL,
                    query TEXT,
                    parameters TEXT,
                    result_count INTEGER,
                    duration_ms REAL,
                    success BOOLEAN NOT NULL,
                    error_message TEXT
                )
            """)

            # 系统日志表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS system_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    level TEXT NOT NULL,
                    module TEXT NOT NULL,
                    message TEXT NOT NULL,
                    extra_data TEXT
                )
            """)

            # 创建索引
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_llm_timestamp ON llm_logs(timestamp)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_llm_model ON llm_logs(model)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_neo4j_timestamp ON neo4j_logs(timestamp)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_system_timestamp ON system_logs(timestamp)")

            conn.commit()
            logger.info(f"日志数据库初始化完成: {self.db_path}")

        except Exception as e:
            logger.error(f"创建日志表失败: {e}")
            raise
        finally:
            conn.close()

    # ========== LLM 日志 ==========

    def save_llm_log(self, log_entry: LLMLogEntry) -> int:
        """
        保存 LLM 日志

        Args:
            log_entry: LLM 日志条目

        Returns:
            插入记录的 ID
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO llm_logs (
                    timestamp, log_type, model, request_messages, response_content,
                    response_model, prompt_tokens, completion_tokens, total_tokens,
                    temperature, max_tokens, duration_ms, success, error_message
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                log_entry.timestamp.isoformat(),
                log_entry.log_type.value,
                log_entry.model,
                log_entry.request_messages,
                log_entry.response_content,
                log_entry.response_model,
                log_entry.prompt_tokens,
                log_entry.completion_tokens,
                log_entry.total_tokens,
                log_entry.temperature,
                log_entry.max_tokens,
                log_entry.duration_ms,
                log_entry.success,
                log_entry.error_message
            ))
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            logger.error(f"保存 LLM 日志失败: {e}")
            raise
        finally:
            conn.close()

    def get_llm_logs(
        self,
        limit: int = 100,
        offset: int = 0,
        model: Optional[str] = None,
        success_only: bool = False
    ) -> List[Dict[str, Any]]:
        """
        查询 LLM 日志

        Args:
            limit: 返回记录数
            offset: 偏移量
            model: 过滤模型
            success_only: 只返回成功的记录

        Returns:
            日志列表
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()

            query = "SELECT * FROM llm_logs WHERE 1=1"
            params = []

            if model:
                query += " AND model = ?"
                params.append(model)

            if success_only:
                query += " AND success = 1"

            query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])

            cursor.execute(query, params)
            rows = cursor.fetchall()

            return [dict(row) for row in rows]
        finally:
            conn.close()

    # ========== Neo4j 日志 ==========

    def save_neo4j_log(self, log_entry: Neo4jLogEntry) -> int:
        """
        保存 Neo4j 日志

        Args:
            log_entry: Neo4j 日志条目

        Returns:
            插入记录的 ID
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO neo4j_logs (
                    timestamp, log_type, query, parameters, result_count,
                    duration_ms, success, error_message
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                log_entry.timestamp.isoformat(),
                log_entry.log_type.value,
                log_entry.query,
                log_entry.parameters,
                log_entry.result_count,
                log_entry.duration_ms,
                log_entry.success,
                log_entry.error_message
            ))
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            logger.error(f"保存 Neo4j 日志失败: {e}")
            raise
        finally:
            conn.close()

    def get_neo4j_logs(
        self,
        limit: int = 100,
        offset: int = 0,
        log_type: Optional[str] = None,
        success_only: bool = False
    ) -> List[Dict[str, Any]]:
        """
        查询 Neo4j 日志

        Args:
            limit: 返回记录数
            offset: 偏移量
            log_type: 过滤日志类型
            success_only: 只返回成功的记录

        Returns:
            日志列表
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()

            query = "SELECT * FROM neo4j_logs WHERE 1=1"
            params = []

            if log_type:
                query += " AND log_type = ?"
                params.append(log_type)

            if success_only:
                query += " AND success = 1"

            query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])

            cursor.execute(query, params)
            rows = cursor.fetchall()

            return [dict(row) for row in rows]
        finally:
            conn.close()

    # ========== 系统日志 ==========

    def save_system_log(self, log_entry: SystemLogEntry) -> int:
        """
        保存系统日志

        Args:
            log_entry: 系统日志条目

        Returns:
            插入记录的 ID
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO system_logs (
                    timestamp, level, module, message, extra_data
                ) VALUES (?, ?, ?, ?, ?)
            """, (
                log_entry.timestamp.isoformat(),
                log_entry.level.value,
                log_entry.module,
                log_entry.message,
                log_entry.extra_data
            ))
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            logger.error(f"保存系统日志失败: {e}")
            raise
        finally:
            conn.close()

    # ========== 统计信息 ==========

    def get_statistics(self) -> Dict[str, Any]:
        """获取日志统计信息"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()

            # LLM 统计
            cursor.execute("SELECT COUNT(*) FROM llm_logs")
            llm_total = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM llm_logs WHERE success = 1")
            llm_success = cursor.fetchone()[0]

            cursor.execute("SELECT SUM(total_tokens) FROM llm_logs WHERE success = 1")
            llm_tokens = cursor.fetchone()[0] or 0

            # Neo4j 统计
            cursor.execute("SELECT COUNT(*) FROM neo4j_logs")
            neo4j_total = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM neo4j_logs WHERE success = 1")
            neo4j_success = cursor.fetchone()[0]

            # 系统日志统计
            cursor.execute("SELECT COUNT(*) FROM system_logs")
            system_total = cursor.fetchone()[0]

            return {
                "llm": {
                    "total": llm_total,
                    "success": llm_success,
                    "failed": llm_total - llm_success,
                    "total_tokens": llm_tokens
                },
                "neo4j": {
                    "total": neo4j_total,
                    "success": neo4j_success,
                    "failed": neo4j_total - neo4j_success
                },
                "system": {
                    "total": system_total
                }
            }
        finally:
            conn.close()

    def clear_old_logs(self, days: int = 30) -> int:
        """
        清理旧日志

        Args:
            days: 保留天数

        Returns:
            删除的记录数
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cutoff_date = (datetime.now()).timestamp()

            deleted = 0
            for table in ["llm_logs", "neo4j_logs", "system_logs"]:
                cursor.execute(f"""
                    DELETE FROM {table}
                    WHERE datetime(timestamp) < datetime('now', '-{days} days')
                """)
                deleted += cursor.rowcount

            conn.commit()
            logger.info(f"清理了 {deleted} 条旧日志（{days} 天前）")
            return deleted
        finally:
            conn.close()
