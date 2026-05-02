"""项目配置文件"""
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Config:
    """全局配置类"""

    # ========== 智谱 AI 配置 ==========
    ZHIPU_API_KEY = os.getenv("ZHIPU_API_KEY")
    ZHIPU_API_BASE = os.getenv("ZHIPU_API_BASE", "https://open.bigmodel.cn/api/coding/paas/v4")
    ZHIPU_MODEL = os.getenv("ZHIPU_MODEL", "glm-4-flash")

    # LLM 调用参数
    LLM_TEMPERATURE = 0.7
    LLM_MAX_TOKENS = 2000
    LLM_TIMEOUT = 60

    # ========== Neo4j 配置 ==========
    NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
    NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

    # Neo4j 连接池配置
    NEO4J_MAX_CONNECTION_LIFETIME = 3600
    NEO4J_MAX_TRANSACTION_RETRY_TIME = 30
    NEO4J_CONNECTION_ACQUISITION_TIMEOUT = 60

    # ========== 应用配置 ==========
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    # 数据路径
    DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
    INPUT_DIR = os.path.join(DATA_DIR, "input")
    OUTPUT_DIR = os.path.join(DATA_DIR, "output")

    @classmethod
    def validate(cls):
        """验证必要配置是否完整"""
        errors = []

        if not cls.ZHIPU_API_KEY:
            errors.append("ZHIPU_API_KEY 未配置")

        if not cls.NEO4J_PASSWORD:
            errors.append("NEO4J_PASSWORD 未配置")

        if errors:
            raise ValueError("配置验证失败:\n" + "\n".join(f"  - {err}" for err in errors))

        return True
