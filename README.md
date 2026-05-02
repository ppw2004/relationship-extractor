# Relationship Extractor

基于大模型的实体与关系提取工具，通过自然语言处理技术从文本中自动抽取实体及其关系，并构建知识图谱。

## 项目简介

本项目旨在利用大语言模型（LLM）的强大推理能力，从非结构化文本中自动识别实体及其语义关系，并将结果存储到 Neo4j 图数据库中，形成可视化的知识图谱。

## 功能特性

- [ ] 文本实体识别与抽取
- [ ] 实体关系类型推断
- [ ] 支持多种文本格式输入
- [ ] 知识图谱自动构建
- [ ] Neo4j 图数据库存储
- [ ] 提取结果可视化展示
- [ ] 批量文本处理
- [ ] API 接口服务

## 技术栈

- **大语言模型**: [智谱 AI](https://open.bigmodel.cn/) (GLM-4)
- **图数据库**: Neo4j
- **编程语言**: Python 3.10+
- **主要依赖**:
  - `zhipuai` - 智谱 AI SDK
  - `neo4j` - Neo4j 驱动
  - `python-dotenv` - 环境变量管理

## 项目结构

```
relationship-extractor/
├── README.md
├── requirements.txt          # Python 依赖
├── .env.example             # 环境变量示例
├── config.py                # 配置文件
├── src/
│   ├── __init__.py
│   ├── llm/                 # 大模型相关
│   │   ├── __init__.py
│   │   ├── zhipu_client.py  # 智谱客户端封装
│   │   └── prompts.py       # 提示词模板
│   ├── graph/               # 图数据库相关
│   │   ├── __init__.py
│   │   └── neo4j_client.py  # Neo4j 客户端封装
│   ├── extractor.py         # 核心提取逻辑
│   └── api.py               # API 服务（可选）
├── data/                    # 数据目录
│   ├── input/               # 输入文本
│   └── output/              # 输出结果
├── tests/                   # 测试文件
└── examples/                # 使用示例
```

## 快速开始

### 1. 环境准备

确保已安装以下环境：
- Python 3.10 或更高版本
- Neo4j 数据库（Docker 或本地安装）

### 2. 安装 Neo4j

使用 Docker 快速启动：

```bash
docker pull neo4j:5.15
docker run -d \
  --name neo4j \
  -p 7474:7474 \
  -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/your_password \
  -e NEO4J_PLUGINS='["apoc"]' \
  neo4j:5.15
```

访问 Neo4j Browser: http://localhost:7474

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置环境变量

复制 `.env.example` 为 `.env` 并填写配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
# 智谱 AI 配置
ZHIPU_API_KEY=your_api_key_here

# Neo4j 配置
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password_here
```

### 5. 运行示例

```python
from src.extractor import RelationshipExtractor

# 初始化提取器
extractor = RelationshipExtractor()

# 提取文本中的实体和关系
text = "马云是阿里巴巴集团的创始人，阿里巴巴总部位于杭州。"
result = extractor.extract(text)

# 结果自动保存到 Neo4j
print(result)
# 输出: {
#   "entities": [
#     {"name": "马云", "type": "Person"},
#     {"name": "阿里巴巴集团", "type": "Organization"},
#     {"name": "杭州", "type": "Location"}
#   ],
#   "relations": [
#     {"from": "马云", "to": "阿里巴巴集团", "type": "创始人"},
#     {"from": "阿里巴巴集团", "to": "杭州", "type": "总部位于"}
#   ]
# }
```

### 6. 查看知识图谱

访问 Neo4j Browser 执行查询：

```cypher
// 查看所有节点和关系
MATCH (n)-[r]->(m) RETURN n, r, m LIMIT 100

// 查找特定实体的关系网络
MATCH (n {name: "马云"})-[r]-(m) RETURN n, r, m
```

## 配置说明

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `ZHIPU_API_KEY` | 智谱 AI API 密钥 | - |
| `ZHIPU_MODEL` | 使用的模型名称 | `glm-4-flash` |
| `NEO4J_URI` | Neo4j 连接地址 | `bolt://localhost:7687` |
| `NEO4J_USER` | Neo4j 用户名 | `neo4j` |
| `NEO4J_PASSWORD` | Neo4j 密码 | - |

## 开发计划

- [x] 项目初始化
- [ ] 实现智谱 AI 接口封装
- [ ] 实现 Neo4j 连接与操作封装
- [ ] 设计实体与关系提取提示词
- [ ] 实现核心提取逻辑
- [ ] 添加单元测试
- [ ] 支持批量文本处理
- [ ] 添加结果导出功能（JSON/CSV）
- [ ] 开发 REST API 接口
- [ ] 添加 Web 可视化界面

## 贡献指南

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License

## 联系方式

如有问题或建议，欢迎通过 Issue 联系。
