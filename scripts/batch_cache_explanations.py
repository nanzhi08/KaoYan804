"""对缺失AI讲解的叶子知识点逐个调用 /api/ai/explain/save 生成缓存"""
import httpx
import sqlite3
import time
import sys
import os

BASE_URL = "http://localhost:8000"
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "knowledge.db")


def get_missing_leaf_ids():
    conn = sqlite3.connect(DB_PATH)
    all_kps = set(r[0] for r in conn.execute("SELECT id FROM knowledge_points").fetchall())
    parent_ids = set(r[0] for r in conn.execute(
        "SELECT DISTINCT parent_id FROM knowledge_points WHERE parent_id IS NOT NULL"
    ).fetchall())
    cached_ids = set(r[0] for r in conn.execute(
        "SELECT id FROM knowledge_points WHERE ai_explanation IS NOT NULL AND ai_explanation != ''"
    ).fetchall())
    leaf_ids = sorted(all_kps - parent_ids - cached_ids)

    # 获取章节信息
    result = []
    for lid in leaf_ids:
        row = conn.execute(
            "SELECT id, name, part, chapter FROM knowledge_points WHERE id=?", (lid,)
        ).fetchone()
        if row:
            result.append(row)

    conn.close()
    return result


def main():
    kps = get_missing_leaf_ids()
    total = len(kps)
    print(f"共 {total} 个缺失AI讲解的叶子知识点\n")

    if total == 0:
        print("所有叶子节点均已缓存，无需生成。")
        return

    client = httpx.Client(timeout=httpx.Timeout(300.0))
    success = 0
    failed = []

    start_all = time.time()
    for i, (kp_id, name, part, chapter) in enumerate(kps, 1):
        print(f"[{i}/{total}] [{part}/{chapter}] {name} ... ", end="", flush=True)
        t0 = time.time()
        try:
            resp = client.post(
                f"{BASE_URL}/api/ai/explain/save",
                params={"kp_id": kp_id, "provider": "deepseek"},
            )
            if resp.status_code == 200:
                elapsed = time.time() - t0
                print(f"OK ({elapsed:.1f}s)")
                success += 1
            else:
                print(f"FAIL (HTTP {resp.status_code})")
                failed.append((kp_id, name, f"HTTP {resp.status_code}"))
        except Exception as e:
            print(f"ERROR: {e}")
            failed.append((kp_id, name, str(e)))

        # 短暂延迟避免API限流
        if i < total:
            time.sleep(1)

    elapsed_total = time.time() - start_all
    print()
    print("=" * 50)
    print(f"完成! 成功: {success}/{total}, 失败: {len(failed)}")
    print(f"总耗时: {elapsed_total:.0f}s ({elapsed_total/60:.1f}min)")
    if failed:
        print("失败列表:")
        for kp_id, name, err in failed:
            print(f"  [{kp_id}] {name}: {err}")

    client.close()


if __name__ == "__main__":
    main()
