from __future__ import annotations

import ast
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FRAMEWORK_PATH = ROOT / "docs" / "804专业课原子概念框架.json"
EXAM_2024_PATH = ROOT / "backend" / "seed" / "seed_2024_exam.py"
KNOWLEDGE_TREE_PATH = ROOT / "backend" / "seed" / "seed_knowledge.py"

REQUIRED_BUCKETS = {
    "C_MOC": ["选择辨析", "程序阅读", "程序填空/改错", "编程题"],
    "DS_MOC": ["选择辨析", "简答题", "计算题", "分析题", "编程题"],
}

KNOWN_QUESTION_TYPES = {
    "single_choice",
    "multi_choice",
    "fill_blank",
    "program_reading",
    "analysis",
    "calculation",
    "programming",
    "short_answer",
}

QUESTION_MAPPING_RULES = [
    {
        "part": "data_structure",
        "contains": "最后一个元素之后插入一个元素和删除第一个元素",
        "concepts": ["循环链表", "顺序表与链表比较"],
    },
    {
        "part": "data_structure",
        "contains": "while(x >= (y+1)*(y+1))",
        "concepts": ["时间复杂度"],
    },
    {
        "part": "data_structure",
        "contains": "若进队的序列为: a, b, c, d",
        "concepts": ["队列定义"],
    },
    {
        "part": "data_structure",
        "contains": "按行地址优先，已知二维数组A[10][10]",
        "concepts": ["数组地址计算", "二维数组按行存储"],
    },
    {
        "part": "data_structure",
        "contains": "前序遍历序列为 a, e, b, d, c",
        "concepts": ["由遍历序列还原二叉树", "前序遍历", "后序遍历"],
    },
    {
        "part": "data_structure",
        "contains": "哈希表的地址区间为0-16",
        "concepts": ["哈希表", "哈希函数构造", "线性探测法"],
    },
    {
        "part": "data_structure",
        "contains": "元素59应该存放在几号位置",
        "concepts": ["哈希表", "线性探测法", "冲突处理"],
    },
    {
        "part": "data_structure",
        "contains": "快速排序最适合",
        "concepts": ["快速排序"],
    },
    {
        "part": "data_structure",
        "contains": "有关二叉树的说法正确",
        "concepts": ["二叉树定义", "二叉树性质"],
    },
    {
        "part": "data_structure",
        "contains": "最小生成树指的是连通图中",
        "concepts": ["最小生成树"],
    },
    {
        "part": "data_structure",
        "contains": "完全二叉树具有1000个结点",
        "concepts": ["完全二叉树性质", "二叉树性质"],
    },
    {
        "part": "data_structure",
        "contains": "根据题干回答以下排序问题",
        "concepts": ["归并排序", "快速排序", "堆排序"],
    },
    {
        "part": "data_structure",
        "contains": "关键路径分析",
        "concepts": ["AOE网", "关键路径"],
    },
    {
        "part": "data_structure",
        "contains": "SearchBST(BiTree T, int x)",
        "concepts": ["二叉链表", "递归与栈关系"],
    },
    {
        "part": "C_programming",
        "contains": "合法的标识符",
        "concepts": ["标识符与关键字"],
    },
    {
        "part": "C_programming",
        "contains": "正确的函数声明方式",
        "concepts": ["函数声明"],
    },
    {
        "part": "C_programming",
        "contains": "else和之前哪个if配对",
        "concepts": ["if-else配对规则"],
    },
    {
        "part": "C_programming",
        "contains": "至少有一个值为非0",
        "concepts": ["逻辑运算符"],
    },
    {
        "part": "C_programming",
        "contains": "数组名作为函数参数",
        "concepts": ["数组名含义", "strcmp"],
    },
    {
        "part": "C_programming",
        "contains": "struct employee",
        "concepts": ["结构体成员访问", "结构体指针", "箭头运算符"],
    },
    {
        "part": "C_programming",
        "contains": "for(i=0, x=0; !x && i<=5; i++)",
        "concepts": ["for循环", "逻辑运算符"],
    },
    {
        "part": "C_programming",
        "contains": "将前四个字符\"2021\"转换成一个数字",
        "concepts": ["字符型", "类型转换"],
    },
    {
        "part": "C_programming",
        "contains": "文件以只写模式打开",
        "concepts": ["文件指针", "文件打开关闭", "文件读写基础"],
    },
    {
        "part": "C_programming",
        "contains": "(*p)++",
        "concepts": ["解引用", "自增自减"],
    },
    {
        "part": "C_programming",
        "contains": "z = x++, y++, ++y",
        "concepts": ["逗号表达式", "自增自减"],
    },
    {
        "part": "C_programming",
        "contains": "斐波那契数列",
        "concepts": ["递推", "for循环"],
    },
    {
        "part": "C_programming",
        "contains": "统计不及格学生",
        "concepts": ["结构体数组", "结构体成员访问", "if语句"],
    },
    {
        "part": "C_programming",
        "contains": "switch(x)",
        "concepts": ["switch语句", "break语句"],
    },
    {
        "part": "C_programming",
        "contains": "static int a = 3",
        "concepts": ["静态局部变量", "函数调用"],
    },
    {
        "part": "C_programming",
        "contains": "int x;\nint f();",
        "concepts": ["作用域", "局部变量与全局变量"],
    },
    {
        "part": "C_programming",
        "contains": "cos(x)=1 - x²/2!",
        "concepts": ["递推", "while循环"],
    },
    {
        "part": "C_programming",
        "contains": "实现数组的循环左移",
        "concepts": ["一维数组定义", "数组下标", "函数定义"],
    },
    {
        "part": "C_programming",
        "contains": "给定不同面额的硬币coins",
        "concepts": ["数组初始化", "数组下标", "for循环"],
    },
]


def load_python_literal(path: Path, symbol_name: str):
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == symbol_name:
                    return ast.literal_eval(node.value)
    raise ValueError(f"Could not find {symbol_name} in {path}")


def load_framework() -> dict:
    return json.loads(FRAMEWORK_PATH.read_text(encoding="utf-8"))


def collect_concepts(subject_cfg: dict) -> set[str]:
    concepts: set[str] = set()
    for area in subject_cfg["knowledge_areas"]:
        concepts.update(area["concepts"])
    return concepts


def build_chapter_area_index(subject_cfg: dict) -> dict[str, list[str]]:
    index: dict[str, list[str]] = defaultdict(list)
    for area in subject_cfg["knowledge_areas"]:
        for chapter in area["chapter_refs"]["syllabus"]:
            index[chapter].append(area["name"])
    return index


def build_system_chapter_index(knowledge_tree: dict) -> dict[str, str]:
    index: dict[str, str] = {}
    for part_node in knowledge_tree["children"]:
        for child in part_node["children"]:
            chapter = child.get("chapter")
            name = child.get("name")
            if chapter and name:
                index[chapter] = name
    return index


def build_question_search_text(question: dict) -> str:
    parts = [question.get("content", "")]
    options = question.get("options")
    if isinstance(options, dict):
        parts.extend(str(value) for value in options.values())
    if question.get("code_snippet"):
        parts.append(question["code_snippet"])
    return "\n".join(part for part in parts if part)


def find_question_concepts(question: dict, valid_concepts: set[str]) -> list[str]:
    search_text = build_question_search_text(question)
    matched: list[str] = []
    for rule in QUESTION_MAPPING_RULES:
        if rule["part"] != question["part"]:
            continue
        if rule["contains"] in search_text:
            for concept in rule["concepts"]:
                if concept in valid_concepts and concept not in matched:
                    matched.append(concept)
    return matched


def validate_structure(framework: dict) -> list[str]:
    issues: list[str] = []
    subjects = framework.get("subjects", {})

    for subject_key, required_bucket_names in REQUIRED_BUCKETS.items():
        subject_cfg = subjects.get(subject_key)
        if not subject_cfg:
            issues.append(f"Missing subject: {subject_key}")
            continue

        actual_bucket_names = [bucket["name"] for bucket in subject_cfg["exam_buckets"]]
        missing_bucket_names = [name for name in required_bucket_names if name not in actual_bucket_names]
        if missing_bucket_names:
            issues.append(f"{subject_key} missing buckets: {', '.join(missing_bucket_names)}")

        for bucket in subject_cfg["exam_buckets"]:
            unknown_types = [t for t in bucket["system_question_types"] if t not in KNOWN_QUESTION_TYPES]
            if unknown_types:
                issues.append(
                    f"{subject_key} bucket {bucket['name']} uses unknown question types: {', '.join(unknown_types)}"
                )

        concept_counter = Counter()
        for area in subject_cfg["knowledge_areas"]:
            concept_counter.update(area["concepts"])
        duplicates = sorted(concept for concept, count in concept_counter.items() if count > 1)
        if duplicates:
            issues.append(f"{subject_key} has duplicate concepts across knowledge areas: {', '.join(duplicates)}")

    return issues


def validate_sample_mappings(framework: dict) -> list[str]:
    issues: list[str] = []
    subject_concepts = {
        subject_key: collect_concepts(subject_cfg)
        for subject_key, subject_cfg in framework["subjects"].items()
    }

    for item in framework.get("sample_question_mappings", []):
        subject_key = "C_MOC" if item["part"] == "C_programming" else "DS_MOC"
        valid_concepts = subject_concepts[subject_key]
        missing_concepts = [concept for concept in item["mapped_concepts"] if concept not in valid_concepts]
        if missing_concepts:
            issues.append(
                f"Sample mapping '{item['question_contains']}' references unknown concepts: {', '.join(missing_concepts)}"
            )
    return issues


def validate_chapter_alignment(framework: dict, knowledge_tree: dict) -> list[str]:
    issues: list[str] = []
    system_chapter_index = build_system_chapter_index(knowledge_tree)

    for subject_key, subject_cfg in framework["subjects"].items():
        for area in subject_cfg["knowledge_areas"]:
            expected_system_chapter = area["chapter_refs"]["system_chapter"]
            for chapter in area["chapter_refs"]["syllabus"]:
                actual_system_chapter = system_chapter_index.get(chapter)
                if actual_system_chapter != expected_system_chapter:
                    issues.append(
                        f"{subject_key} chapter {chapter} expected '{expected_system_chapter}' but found "
                        f"'{actual_system_chapter or 'MISSING'}' in seed_knowledge.py"
                    )
    return issues


def validate_exam_coverage(framework: dict, exam_questions: list[dict]) -> tuple[list[str], dict[str, int]]:
    issues: list[str] = []
    stats = {
        "question_count": len(exam_questions),
        "bucket_covered": 0,
        "chapter_covered": 0,
        "concept_mapped": 0,
    }

    subject_cfg_by_part = {
        "C_programming": framework["subjects"]["C_MOC"],
        "data_structure": framework["subjects"]["DS_MOC"],
    }

    for question in exam_questions:
        subject_cfg = subject_cfg_by_part[question["part"]]
        chapter_index = build_chapter_area_index(subject_cfg)
        valid_concepts = collect_concepts(subject_cfg)

        bucket_names = [
            bucket["name"]
            for bucket in subject_cfg["exam_buckets"]
            if question["type"] in bucket["system_question_types"]
        ]
        if bucket_names:
            stats["bucket_covered"] += 1
        else:
            issues.append(
                f"Question type not bucket-covered: {question['part']} / {question['type']} / {question['content'][:40]}"
            )

        if question["kp_chapter"] in chapter_index:
            stats["chapter_covered"] += 1
        else:
            issues.append(
                f"Question chapter not covered: {question['part']} / {question['kp_chapter']} / {question['content'][:40]}"
            )

        matched_concepts = find_question_concepts(question, valid_concepts)
        if matched_concepts:
            stats["concept_mapped"] += 1
        else:
            issues.append(
                f"Question not atomically mapped: {question['part']} / {question['type']} / {question['content'][:60]}"
            )

    return issues, stats


def main() -> int:
    framework = load_framework()
    exam_questions = load_python_literal(EXAM_2024_PATH, "EXAM_2024_QUESTIONS")
    knowledge_tree = load_python_literal(KNOWLEDGE_TREE_PATH, "KNOWLEDGE_TREE")

    issues: list[str] = []
    issues.extend(validate_structure(framework))
    issues.extend(validate_sample_mappings(framework))
    issues.extend(validate_chapter_alignment(framework, knowledge_tree))

    exam_issues, exam_stats = validate_exam_coverage(framework, exam_questions)
    issues.extend(exam_issues)

    c_concepts = len(collect_concepts(framework["subjects"]["C_MOC"]))
    ds_concepts = len(collect_concepts(framework["subjects"]["DS_MOC"]))

    print("804 原子概念框架校验")
    print(f"- C 原子概念数: {c_concepts}")
    print(f"- DS 原子概念数: {ds_concepts}")
    print(f"- 2024 真题题目数: {exam_stats['question_count']}")
    print(f"- 题型桶覆盖: {exam_stats['bucket_covered']}/{exam_stats['question_count']}")
    print(f"- 章节映射覆盖: {exam_stats['chapter_covered']}/{exam_stats['question_count']}")
    print(f"- 原子概念映射覆盖: {exam_stats['concept_mapped']}/{exam_stats['question_count']}")

    if issues:
        print("- 校验结果: FAILED")
        for issue in issues:
            print(f"  * {issue}")
        return 1

    print("- 校验结果: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
