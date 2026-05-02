#!/usr/bin/env python3
"""日志查询和管理工具"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.logger.log_storage import LogStorage
from src.config import Config


def show_statistics():
    """显示日志统计信息"""
    print("=" * 60)
    print("日志统计")
    print("=" * 60)

    storage = LogStorage(Config.LOG_DB_PATH)
    stats = storage.get_statistics()

    print(f"\n【LLM 调用日志】")
    print(f"  总调用次数: {stats['llm']['total']}")
    print(f"  成功: {stats['llm']['success']}")
    print(f"  失败: {stats['llm']['failed']}")
    print(f"  总 Token 消耗: {stats['llm']['total_tokens']:,}")

    print(f"\n【Neo4j 操作日志】")
    print(f"  总操作次数: {stats['neo4j']['total']}")
    print(f"  成功: {stats['neo4j']['success']}")
    print(f"  失败: {stats['neo4j']['failed']}")

    print(f"\n【系统日志】")
    print(f"  总日志数: {stats['system']['total']}")


def show_llm_logs(limit=10):
    """显示最近的 LLM 日志"""
    print("\n" + "=" * 60)
    print(f"最近的 {limit} 条 LLM 调用日志")
    print("=" * 60)

    storage = LogStorage(Config.LOG_DB_PATH)
    logs = storage.get_llm_logs(limit=limit)

    if not logs:
        print("\n暂无 LLM 日志")
        return

    for i, log in enumerate(logs, 1):
        print(f"\n[{i}] {log['timestamp']}")
        print(f"  模型: {log['model']}")
        print(f"  类型: {log['log_type']}")
        if log['request_messages']:
            print(f"  请求: {log['request_messages'][:100]}...")
        if log['response_content']:
            print(f"  响应: {log['response_content'][:100]}...")
        if log['total_tokens']:
            print(f"  Tokens: {log['prompt_tokens']} + {log['completion_tokens']} = {log['total_tokens']}")
        if log['duration_ms']:
            print(f"  耗时: {log['duration_ms']:.2f}ms")
        if not log['success']:
            print(f"  错误: {log['error_message']}")


def show_neo4j_logs(limit=10):
    """显示最近的 Neo4j 日志"""
    print("\n" + "=" * 60)
    print(f"最近的 {limit} 条 Neo4j 操作日志")
    print("=" * 60)

    storage = LogStorage(Config.LOG_DB_PATH)
    logs = storage.get_neo4j_logs(limit=limit)

    if not logs:
        print("\n暂无 Neo4j 日志")
        return

    for i, log in enumerate(logs, 1):
        print(f"\n[{i}] {log['timestamp']}")
        print(f"  类型: {log['log_type']}")
        if log['query']:
            print(f"  查询: {log['query'][:80]}...")
        if log['parameters']:
            print(f"  参数: {log['parameters'][:80]}...")
        if log['result_count'] is not None:
            print(f"  结果数: {log['result_count']}")
        if log['duration_ms']:
            print(f"  耗时: {log['duration_ms']:.2f}ms")
        if not log['success']:
            print(f"  错误: {log['error_message']}")


def clear_old_logs(days=30):
    """清理旧日志"""
    print("\n" + "=" * 60)
    print(f"清理 {days} 天前的旧日志")
    print("=" * 60)

    storage = LogStorage(Config.LOG_DB_PATH)
    deleted = storage.clear_old_logs(days=days)
    print(f"\n已删除 {deleted} 条旧日志")


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="日志查询工具")
    parser.add_argument("--stats", action="store_true", help="显示统计信息")
    parser.add_argument("--llm", type=int, nargs="?", const=10, help="显示 LLM 日志，可指定条数")
    parser.add_argument("--neo4j", type=int, nargs="?", const=10, help="显示 Neo4j 日志，可指定条数")
    parser.add_argument("--clear", type=int, help="清理 N 天前的旧日志")

    args = parser.parse_args()

    # 默认显示统计信息
    if not any([args.stats, args.llm is not None, args.neo4j is not None, args.clear]):
        args.stats = True

    if args.stats:
        show_statistics()

    if args.llm is not None:
        show_llm_logs(args.llm)

    if args.neo4j is not None:
        show_neo4j_logs(args.neo4j)

    if args.clear:
        clear_old_logs(args.clear)


if __name__ == "__main__":
    main()
