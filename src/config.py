"""项目配置文件"""
import os
from dotenv import load_dotenv
from pathlib import Path

# 获取项目根目录
CURRENT_DIR = Path(__file__).parent.parent
PROJECTS_DIR = CURRENT_DIR / "projects"

# 检测是否在子项目目录中
# 通过检查是否存在 config/.env 文件来判断
project_env = None
if Path("config/.env").exists():
    # 在子项目目录中
    load_dotenv("config/.env")
    project_env = Path("config/.env")
elif Path("projects").exists():
    # 在主项目目录中，尝试找到子项目
    for project_dir in Path("projects").iterdir():
        if project_dir.is_dir():
            env_file = project_dir / "config" / ".env"
            if env_file.exists():
                # 找到了子项目的配置，尝试使用
                # 但需要用户明确指定，这里暂时跳过
                pass

# 默认加载根目录的 .env
if not Path("config/.env").exists():
    load_dotenv()

# 检测是否为子项目模式
PROJECT_NAME = os.getenv("PROJECT_NAME", "default")
if PROJECT_NAME != "default":
    # 子项目模式：加载子项目的配置
    project_config_file = PROJECTS_DIR / PROJECT_NAME / "config" / ".env"
    if project_config_file.exists():
        load_dotenv(project_config_file, override=True)
        IS_SUBPROJECT = True
    else:
        IS_SUBPROJECT = False
else:
    IS_SUBPROJECT = False

class Config:
    """全局配置类"""

    # ========== 智谱 AI 配置 ==========
    ZHIPU_API_KEY = os.getenv("ZHIPU_API_KEY")
    ZHIPU_API_BASE = os.getenv("ZHIPU_API_BASE", "https://open.bigmodel.cn/api/coding/paas/v4")
    ZHIPU_MODEL = os.getenv("ZHIPU_MODEL", "glm-4.5-air")

    # LLM 调用参数
    LLM_TEMPERATURE = 0.7
    LLM_MAX_TOKENS = 2000
    LLM_TIMEOUT = 60

    # 深度思考配置
    # 是否启用深度思考模式（适用于支持思考的模型如 glm-4.5, glm-4.6, glm-4.7, glm-5 等）
    ENABLE_THINKING = os.getenv("ENABLE_THINKING", "false").lower() == "true"
    # 思考模式类型：enabled（启用）/ disabled（禁用）/ auto（自动判断）
    THINKING_TYPE = os.getenv("THINKING_TYPE", "auto")

    # ========== Neo4j 配置 ==========
    NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
    NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
    NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")

    # Neo4j 连接池配置
    NEO4J_MAX_CONNECTION_LIFETIME = 3600
    NEO4J_MAX_TRANSACTION_RETRY_TIME = 30
    NEO4J_CONNECTION_ACQUISITION_TIMEOUT = 60

    # ========== 子项目配置 ==========
    # 子项目名称，用于在单数据库模式下区分子项目数据
    PROJECT_NAME = os.getenv("PROJECT_NAME", "default")
    # 是否为子项目模式
    IS_SUBPROJECT = os.path.exists(os.path.join(os.path.dirname(__file__), "..", "projects", PROJECT_NAME))

    # ========== 应用配置 ==========
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    # 数据路径
    DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
    INPUT_DIR = os.path.join(DATA_DIR, "input")
    OUTPUT_DIR = os.path.join(DATA_DIR, "output")

    # ========== 日志配置 ==========
    # 日志数据库路径
    LOG_DB_PATH = os.getenv("LOG_DB_PATH", "logs/app.db")
    # 是否启用 LLM 调用日志
    ENABLE_LLM_LOGGING = os.getenv("ENABLE_LLM_LOGGING", "true").lower() == "true"
    # 是否启用 Neo4j 操作日志
    ENABLE_NEO4J_LOGGING = os.getenv("ENABLE_NEO4J_LOGGING", "true").lower() == "true"
    # 日志保留天数
    LOG_RETENTION_DAYS = int(os.getenv("LOG_RETENTION_DAYS", "30"))

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
