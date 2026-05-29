"""初始化804考试知识点树"""
import asyncio
import sys
sys.path.insert(0, ".")

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session, init_db, engine, Base
from app.models.knowledge_point import KnowledgePoint
from app.models.knowledge_mastery import KnowledgeMastery

KNOWLEDGE_TREE = {
    "name": "数据结构与高级程序设计（804）",
    "part": "root",
    "children": [
        {
            "name": "第一部分：C语言高级程序设计",
            "part": "C_programming",
            "children": [
                {
                    "name": "1.1 程序基本结构与数据类型",
                    "part": "C_programming",
                    "chapter": "1.1",
                    "difficulty": 2,
                    "exam_weight": "高频",
                    "description": "C语言程序的基本结构；变量声明与数据类型；变量声明与赋值操作。"
                },
                {
                    "name": "1.2 运算符与表达式",
                    "part": "C_programming",
                    "chapter": "1.2",
                    "difficulty": 2,
                    "exam_weight": "高频",
                    "description": "C语言运算符（算术、关系、逻辑、位运算）；关系表达式；运算符优先级与结合性。"
                },
                {
                    "name": "1.3 循环结构与分支结构",
                    "part": "C_programming",
                    "chapter": "1.3",
                    "difficulty": 3,
                    "exam_weight": "高频",
                    "description": "for循环、while循环、do-while循环；if-else、switch分支结构；枚举法的基本思想与应用。"
                },
                {
                    "name": "1.4 数组与结构体",
                    "part": "C_programming",
                    "chapter": "1.4",
                    "difficulty": 3,
                    "exam_weight": "高频",
                    "description": "一维数组与二维数组的定义与使用；筛法与排序法的基本算法；结构体定义与使用；结构体数组。"
                },
                {
                    "name": "1.5 函数、递推与递归",
                    "part": "C_programming",
                    "chapter": "1.5",
                    "difficulty": 4,
                    "exam_weight": "高频",
                    "description": "函数定义、声明、调用与返回值；参数传递机制；递推数列的算法实现；递归的基本思路与方法。"
                },
                {
                    "name": "1.6 指针与引用",
                    "part": "C_programming",
                    "chapter": "1.6",
                    "difficulty": 5,
                    "exam_weight": "高频",
                    "description": "指针的基本概念与操作；指针与一维数组；字符串处理；指针与结构体；引用概念与参数传递；值传递、指针传递、引用传递的比较。"
                },
                {
                    "name": "1.7 流与文件操作",
                    "part": "C_programming",
                    "chapter": "1.7",
                    "difficulty": 3,
                    "exam_weight": "中频",
                    "description": "I/O流的基本概念；标准输入输出流；文件流的打开、读写、关闭操作；格式控制。"
                },
            ]
        },
        {
            "name": "第二部分：数据结构",
            "part": "data_structure",
            "children": [
                {
                    "name": "2.1 数据结构与算法基础概念",
                    "part": "data_structure",
                    "chapter": "2.1",
                    "difficulty": 2,
                    "exam_weight": "中频",
                    "description": "数据结构的基本概念与术语；算法的定义与特性；时间复杂度与空间复杂度分析。"
                },
                {
                    "name": "2.2 线性表",
                    "part": "data_structure",
                    "chapter": "2.2",
                    "difficulty": 3,
                    "exam_weight": "高频",
                    "description": "顺序线性表（顺序表）的定义与基本操作；链式线性表（单链表、双向链表、循环链表）的定义与基本操作；顺序存储与链式存储的优缺点比较；线性表的简单应用。"
                },
                {
                    "name": "2.3 栈与队列",
                    "part": "data_structure",
                    "chapter": "2.3",
                    "difficulty": 3,
                    "exam_weight": "高频",
                    "description": "栈的结构特征（FILO）与顺序存储实现；队列的结构特征（FIFO）与顺序存储实现；栈与队列的基本操作；栈与递归的关系；递归的核心概念。"
                },
                {
                    "name": "2.4 数组与特殊矩阵",
                    "part": "data_structure",
                    "chapter": "2.4",
                    "difficulty": 3,
                    "exam_weight": "中频",
                    "description": "数组的定义与地址计算公式；特殊矩阵（对称矩阵、三角矩阵、对角矩阵）的压缩存储与地址公式；稀疏矩阵的三元组存储方式及基本运算；广义表的基本概念。"
                },
                {
                    "name": "2.5 树与二叉树",
                    "part": "data_structure",
                    "chapter": "2.5",
                    "difficulty": 5,
                    "exam_weight": "高频",
                    "description": "树的基本概念与术语；二叉树的基本概念、性质（5条性质）与存储结构（顺序、链式）；二叉树遍历（前序、中序、后序、层次遍历）与恢复（由遍历序列恢复二叉树）；树、森林与二叉树的相互转换；哈夫曼树的构造与哈夫曼编码算法。"
                },
                {
                    "name": "2.6 图",
                    "part": "data_structure",
                    "chapter": "2.6",
                    "difficulty": 5,
                    "exam_weight": "高频",
                    "description": "图的基本概念（有向图、无向图、度、路径、连通等）；图的存储结构（邻接矩阵、邻接表）；图的基本类型与运算（连通图、有向无环图）；图的遍历（DFS、BFS）；最小生成树（Prim、Kruskal）；拓扑排序；关键路径；最短路径（Dijkstra、Floyd）。"
                },
                {
                    "name": "2.7 查找",
                    "part": "data_structure",
                    "chapter": "2.7",
                    "difficulty": 4,
                    "exam_weight": "高频",
                    "description": "顺序查找；折半查找（二分查找）；分块查找；二叉排序树（BST）的查找、插入与删除；平衡二叉树（AVL）的基本概念；静态查找与动态查找的区别；哈希表的基本思想、哈希函数构造方法、冲突处理方法（开放定址法、链地址法）。"
                },
                {
                    "name": "2.8 内部排序",
                    "part": "data_structure",
                    "chapter": "2.8",
                    "difficulty": 4,
                    "exam_weight": "高频",
                    "description": "排序的基本概念（稳定性、时间复杂度、空间复杂度）；插入排序（直接插入、二分插入）；希尔排序；冒泡排序；快速排序；选择排序；堆排序（堆的构建与调整）；归并排序；基数排序；各种排序方法的比较与适用场合。"
                },
            ]
        }
    ]
}


def get_all_kps(node, parent_id=None, order=0):
    """递归展开知识树为平铺列表"""
    result = []
    kp = {
        "name": node["name"],
        "part": node["part"],
        "chapter": node.get("chapter", ""),
        "order": order,
        "difficulty": node.get("difficulty", 1),
        "exam_weight": node.get("exam_weight", ""),
        "description": node.get("description", ""),
        "parent_id": parent_id,
    }
    result.append(kp)
    for i, child in enumerate(node.get("children", [])):
        result.extend(get_all_kps(child, parent_id=None, order=i))  # parent_id will be set after insert
    return result


async def seed():
    await init_db()

    async with async_session() as session:
        # Check if already seeded
        result = await session.execute(select(KnowledgePoint).limit(1))
        if result.scalars().first():
            print("知识点数据已存在，跳过初始化。")
            return

        # Insert root node first
        root = KnowledgePoint(**get_all_kps(KNOWLEDGE_TREE)[0])
        session.add(root)
        await session.flush()

        # Insert C programming part
        for node in KNOWLEDGE_TREE["children"]:
            part_kp = KnowledgePoint(
                name=node["name"],
                part=node["part"],
                parent_id=root.id,
                order=node["part"] == "data_structure" and 1 or 0,
            )
            session.add(part_kp)
            await session.flush()

            order = 0
            for child in node["children"]:
                child_kp = KnowledgePoint(
                    name=child["name"],
                    part=child["part"],
                    chapter=child.get("chapter", ""),
                    difficulty=child.get("difficulty", 1),
                    exam_weight=child.get("exam_weight", ""),
                    description=child.get("description", ""),
                    parent_id=part_kp.id,
                    order=order,
                )
                session.add(child_kp)
                await session.flush()

                # Create mastery record
                mastery = KnowledgeMastery(knowledge_point_id=child_kp.id)
                session.add(mastery)

                order += 1

        await session.commit()
        print(f"知识点树初始化完成！共导入 1 个根节点 + {len(KNOWLEDGE_TREE['children'])} 个部分 + 15 个章节知识点。")
        print("已为每个章节知识点创建掌握度记录。")


if __name__ == "__main__":
    asyncio.run(seed())
