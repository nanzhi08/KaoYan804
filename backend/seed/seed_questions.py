"""初始化示例题库"""
import asyncio
import sys
sys.path.insert(0, ".")

from sqlalchemy import select
from app.database import async_session, init_db
from app.models.knowledge_point import KnowledgePoint
from app.models.question import Question, QuestionKnowledgePoint

SAMPLE_QUESTIONS = [
    # ===== C语言部分 =====
    {
        "type": "single_choice",
        "part": "C_programming",
        "difficulty": 2,
        "content": "以下哪个是C语言中合法的标识符？",
        "options": {"A": "2var", "B": "_var", "C": "int", "D": "var-name"},
        "answer": "B",
        "explanation": "C语言标识符只能由字母、数字和下划线组成，且不能以数字开头，不能是关键字。_var以_开头是合法的。",
        "kp_chapter": "1.1",
    },
    {
        "type": "single_choice",
        "part": "C_programming",
        "difficulty": 2,
        "content": "设有 int a=5, b=3; 则表达式 a/b 的值是？",
        "options": {"A": "1.667", "B": "2", "C": "1", "D": "1.0"},
        "answer": "C",
        "explanation": "两个整数相除，结果为整数（向下取整）。5/3 = 1。若想得到浮点数结果，应写成 5.0/3。",
        "kp_chapter": "1.2",
    },
    {
        "type": "single_choice",
        "part": "C_programming",
        "difficulty": 2,
        "content": "以下代码的输出是什么？\n```c\nint i = 0;\nwhile(i < 3) {\n    printf(\"%d \", i);\n    i++;\n}\n```",
        "options": {"A": "0 1 2 3", "B": "0 1 2", "C": "1 2 3", "D": "0 1 2 "},
        "answer": "B",
        "explanation": "while循环在条件不满足时退出。i从0开始，满足<3时执行循环体并输出，当i=3时条件不满足退出。输出 0 1 2。",
        "code_snippet": "int i = 0;\nwhile(i < 3) {\n    printf(\"%d \", i);\n    i++;\n}",
        "kp_chapter": "1.3",
    },
    {
        "type": "program_reading",
        "part": "C_programming",
        "difficulty": 3,
        "content": "阅读以下程序，写出输出结果：\n```c\n#include <stdio.h>\nint main() {\n    int a = 10, b = 5;\n    if (a > b)\n        if (b > 0)\n            printf(\"A\");\n    else\n        printf(\"B\");\n    return 0;\n}\n```",
        "answer": "A",
        "explanation": "需要注意的是else与最近的未配对if配对。本代码中else与if(b>0)配对。因为a>b且b>0，所以执行打印\"A\"。",
        "code_snippet": "#include <stdio.h>\nint main() {\n    int a = 10, b = 5;\n    if (a > b)\n        if (b > 0)\n            printf(\"A\");\n    else\n        printf(\"B\");\n    return 0;\n}",
        "kp_chapter": "1.3",
    },
    {
        "type": "single_choice",
        "part": "C_programming",
        "difficulty": 2,
        "content": "设有 int a[5] = {1, 2, 3, 4, 5}; 则 a[2] 的值是？",
        "options": {"A": "1", "B": "2", "C": "3", "D": "4"},
        "answer": "C",
        "explanation": "C语言数组下标从0开始。a[0]=1, a[1]=2, a[2]=3。",
        "kp_chapter": "1.4",
    },
    {
        "type": "fill_blank",
        "part": "C_programming",
        "difficulty": 3,
        "content": "使用冒泡排序对数组 int a[5] = {5, 3, 1, 4, 2} 从小到大排序，第一趟排序后数组变为 ____。",
        "answer": "{3, 1, 4, 2, 5}",
        "explanation": "冒泡排序第一趟将最大值5移动到末尾：比较交换过程为 5↔3→{3,5,1,4,2}, 5↔1→{3,1,5,4,2}, 5↔4→{3,1,4,5,2}, 5↔2→{3,1,4,2,5}。",
        "kp_chapter": "1.4",
    },
    {
        "type": "single_choice",
        "part": "C_programming",
        "difficulty": 3,
        "content": "以下关于函数的说法，正确的是？",
        "options": {
            "A": "C语言函数不能嵌套定义",
            "B": "函数必须有返回值",
            "C": "函数定义可以放在调用之后",
            "D": "函数参数传递只能是值传递"
        },
        "answer": "A",
        "explanation": "C语言中函数不能嵌套定义（不能在一个函数体内定义另一个函数）。函数可以没有返回值（void）；函数定义通常应在调用之前，或需要提前声明；参数传递可以是值传递，也可以通过指针实现地址传递。",
        "kp_chapter": "1.5",
    },
    {
        "type": "program_reading",
        "part": "C_programming",
        "difficulty": 4,
        "content": "以下递归函数的输出是什么？\n```c\nint f(int n) {\n    if (n <= 1) return 1;\n    return n * f(n - 1);\n}\nint main() {\n    printf(\"%d\", f(4));\n    return 0;\n}\n```",
        "answer": "24",
        "explanation": "f(4)=4*f(3)=4*3*f(2)=4*3*2*f(1)=4*3*2*1=24。这是阶乘的递归实现。",
        "code_snippet": "int f(int n) {\n    if (n <= 1) return 1;\n    return n * f(n - 1);\n}",
        "kp_chapter": "1.5",
    },
    {
        "type": "single_choice",
        "part": "C_programming",
        "difficulty": 4,
        "content": "设有 int a = 10, *p = &a; 则 *p + 1 的值是？",
        "options": {"A": "11", "B": "a的地址+1", "C": "10", "D": "编译错误"},
        "answer": "A",
        "explanation": "*p 是解引用操作，取得指针p指向的值（即a的值10）。*p + 1 = 10 + 1 = 11。",
        "kp_chapter": "1.6",
    },
    {
        "type": "single_choice",
        "part": "C_programming",
        "difficulty": 3,
        "content": "C语言中，字符串 \"hello\" 在内存中占用的字节数是？",
        "options": {"A": "5", "B": "6", "C": "4", "D": "不确定"},
        "answer": "B",
        "explanation": "C语言字符串以空字符'\\0'结尾，\"hello\"实际存储为 h-e-l-l-o-\\0，占用6个字节。",
        "kp_chapter": "1.6",
    },
    {
        "type": "fill_blank",
        "part": "C_programming",
        "difficulty": 3,
        "content": "C语言中，用于打开文件的函数是 ____。",
        "answer": "fopen",
        "explanation": "fopen()是C标准库中用于打开文件的函数，原型为 FILE *fopen(const char *filename, const char *mode)。",
        "kp_chapter": "1.7",
    },
    # ===== 数据结构部分 =====
    {
        "type": "single_choice",
        "part": "data_structure",
        "difficulty": 2,
        "content": "算法的时间复杂度是指？",
        "options": {
            "A": "算法程序的长度",
            "B": "算法执行过程中所需要的基本运算次数",
            "C": "算法程序中的指令条数",
            "D": "执行算法所需要的时间"
        },
        "answer": "B",
        "explanation": "时间复杂度是指算法执行过程中所需要的基本运算次数（或执行次数），通常用大O记号表示，如O(n)、O(n²)等。",
        "kp_chapter": "2.1",
    },
    {
        "type": "single_choice",
        "part": "data_structure",
        "difficulty": 2,
        "content": "在长度为n的顺序表中插入一个元素，平均需要移动多少个元素？",
        "options": {"A": "n", "B": "n/2", "C": "(n-1)/2", "D": "n-1"},
        "answer": "B",
        "explanation": "在顺序表中插入元素，插入位置从0到n共n+1个位置，平均移动元素个数为 n/2。",
        "kp_chapter": "2.2",
    },
    {
        "type": "single_choice",
        "part": "data_structure",
        "difficulty": 2,
        "content": "单链表中，删除p所指结点的后继结点，正确的操作是？",
        "options": {
            "A": "p->next = p->next->next",
            "B": "p = p->next",
            "C": "p->next = p",
            "D": "p = p->next->next"
        },
        "answer": "A",
        "explanation": "要删除p的后继结点q（即q=p->next），只需让p的next指针跳过q，指向q的下一个结点：p->next = p->next->next。",
        "kp_chapter": "2.2",
    },
    {
        "type": "single_choice",
        "part": "data_structure",
        "difficulty": 2,
        "content": "栈的特点是？",
        "options": {
            "A": "先进先出",
            "B": "先进后出",
            "C": "后进后出",
            "D": "随机存取"
        },
        "answer": "B",
        "explanation": "栈是先进后出（FILO/FILO，First In Last Out）的数据结构，所有操作都在栈顶进行。与之对应，队列是先进先出（FIFO）。",
        "kp_chapter": "2.3",
    },
    {
        "type": "analysis",
        "part": "data_structure",
        "difficulty": 3,
        "content": "分析以下递归函数的功能：\n```c\nint f(int n) {\n    if (n == 0) return 0;\n    else return f(n - 1) + n;\n}\n```\n请说明该函数的功能，并写出 f(5) 的值。",
        "answer": "功能：计算1到n的累加和（即1+2+...+n）。f(5)=15。",
        "explanation": "f(n) = f(n-1) + n，递归展开：f(5)=f(4)+5=f(3)+4+5=...=0+1+2+3+4+5=15。栈与递归关系密切，递归调用过程本质上就是利用栈来保存返回地址。",
        "kp_chapter": "2.3",
    },
    {
        "type": "single_choice",
        "part": "data_structure",
        "difficulty": 2,
        "content": "一个10×10的对称矩阵，采用压缩存储（只存下三角部分），需要多少个存储单元？",
        "options": {"A": "100", "B": "55", "C": "50", "D": "45"},
        "answer": "B",
        "explanation": "对称矩阵只需存储下三角（含对角线），下三角元素个数为 n(n+1)/2 = 10*11/2 = 55。",
        "kp_chapter": "2.4",
    },
    {
        "type": "single_choice",
        "part": "data_structure",
        "difficulty": 2,
        "content": "深度为k的完全二叉树，最多有多少个结点？",
        "options": {"A": "2^k", "B": "2^k - 1", "C": "2^(k-1)", "D": "2k - 1"},
        "answer": "B",
        "explanation": "深度为k的完全二叉树最多是满二叉树，结点数为 2^k - 1。例如深度为3的满二叉树有7个结点。",
        "kp_chapter": "2.5",
    },
    {
        "type": "analysis",
        "part": "data_structure",
        "difficulty": 4,
        "content": "已知二叉树的前序遍历序列为 ABDCEF，中序遍历序列为 DBAECF，请画出该二叉树，并写出后序遍历序列。",
        "answer": "后序遍历序列为 DBEFCA。二叉树结构：A为根，左子树B（左D右空），右子树C（左E右F）。",
        "explanation": "前序首个A为根；在中序中A左边DB为左子树，右边ECF为右子树。对左子树DB：前序BD，B为根，中序DB中D在B左边→D是B的左孩子。对右子树ECF：前序CEF，C为根，中序ECF中E在C左边，F在右边→E是C左孩子，F是C右孩子。",
        "kp_chapter": "2.5",
    },
    {
        "type": "calculation",
        "part": "data_structure",
        "difficulty": 4,
        "content": "给定字符集 {a, b, c, d, e} 及其权值 {5, 2, 9, 7, 3}，构造哈夫曼树，并写出各字符的哈夫曼编码。",
        "answer": "a:10, b:110, c:00, d:01, e:111。编码不唯一，同权重交换左右子树会得到不同的编码方案。",
        "explanation": "哈夫曼树构造步骤：1)选最小的两个2(b)和3(e)合并得5；2)选最小的两个5(a)和5(新)合并得10；3)选最小的两个7(d)和9(c)合并得16；4)合并10和16得26。编码：从根到叶子，左0右1。",
        "kp_chapter": "2.5",
    },
    {
        "type": "single_choice",
        "part": "data_structure",
        "difficulty": 3,
        "content": "一个有n个顶点的无向连通图，至少有多少条边？",
        "options": {"A": "n", "B": "n-1", "C": "n*(n-1)/2", "D": "0"},
        "answer": "B",
        "explanation": "n个顶点的无向连通图至少需要n-1条边（即形成一棵生成树）。如果少于n-1条边，图必然不连通。",
        "kp_chapter": "2.6",
    },
    {
        "type": "single_choice",
        "part": "data_structure",
        "difficulty": 3,
        "content": "使用邻接表存储图时，广度优先遍历(BFS)需要借助的数据结构是？",
        "options": {"A": "栈", "B": "队列", "C": "二叉树", "D": "哈希表"},
        "answer": "B",
        "explanation": "BFS需要按层遍历，先访问的顶点的邻接点应该先被访问，因此需要用到队列（FIFO）。而DFS（深度优先遍历）需要用到栈（或递归实现）。",
        "kp_chapter": "2.6",
    },
    {
        "type": "single_choice",
        "part": "data_structure",
        "difficulty": 3,
        "content": "对有序表 {2, 5, 8, 12, 16, 23, 38, 45, 56, 67} 进行折半查找，在查找关键字16的过程中，依次被比较的元素是？",
        "options": {
            "A": "23, 8, 12, 16",
            "B": "23, 12, 16",
            "C": "23, 8, 16",
            "D": "16, 23, 8"
        },
        "answer": "A",
        "explanation": "折半查找过程：low=0, high=9, mid=4 → a[4]=23>16, high=3；mid=1 → a[1]=8<16, low=2；mid=2 → a[2]=12<16, low=3；mid=3 → a[3]=16，找到。比较顺序：23, 8, 12, 16。",
        "kp_chapter": "2.7",
    },
    {
        "type": "fill_blank",
        "part": "data_structure",
        "difficulty": 3,
        "content": "哈希表处理冲突的方法主要有 ____ 和 ____ 两种。",
        "answer": "开放定址法 和 链地址法",
        "explanation": "开放定址法（包括线性探测、二次探测、双重散列）和链地址法（拉链法）是解决哈希冲突的两种主要方法。",
        "kp_chapter": "2.7",
    },
    {
        "type": "single_choice",
        "part": "data_structure",
        "difficulty": 2,
        "content": "以下哪种排序算法是稳定的？",
        "options": {"A": "快速排序", "B": "归并排序", "C": "堆排序", "D": "选择排序"},
        "answer": "B",
        "explanation": "归并排序是稳定的排序算法。快速排序、堆排序、选择排序都是不稳定的。稳定的排序算法还包括：冒泡排序、插入排序、基数排序。",
        "kp_chapter": "2.8",
    },
    {
        "type": "single_choice",
        "part": "data_structure",
        "difficulty": 3,
        "content": "快速排序在什么情况下退化为O(n²)的时间复杂度？",
        "options": {
            "A": "待排序序列已经有序",
            "B": "待排序序列逆序",
            "C": "待排序序列随机排列",
            "D": "A和B都是"
        },
        "answer": "D",
        "explanation": "快速排序在序列已经有序（正序或逆序）且每次选取第一个或最后一个元素作为基准时，每次划分都极度不平衡（一侧为空），时间复杂度退化为O(n²)。解决方案是随机选取基准或三数取中法。",
        "kp_chapter": "2.8",
    },
    {
        "type": "calculation",
        "part": "data_structure",
        "difficulty": 4,
        "content": "对序列 {49, 38, 65, 97, 76, 13, 27, 50} 进行堆排序，请写出建成的初始大顶堆。",
        "answer": "{97, 76, 65, 50, 49, 13, 27, 38}",
        "explanation": "堆排序建堆过程：从最后一个非叶子结点开始（n/2=4，即元素76），依次向上调整。调整后得到的初始大顶堆为 97, 76, 65, 50, 49, 13, 27, 38（可能因调整顺序不同有所差异，但必须满足大顶堆性质：父≥子）。",
        "kp_chapter": "2.8",
    },
]


async def seed():
    await init_db()

    async with async_session() as session:
        # Check if already seeded
        result = await session.execute(select(Question).limit(1))
        if result.scalars().first():
            print("题库数据已存在，跳过初始化。")
            return

        # Get knowledge points by chapter
        kp_result = await session.execute(select(KnowledgePoint))
        kps = {kp.chapter: kp for kp in kp_result.scalars().all() if kp.chapter}

        count = 0
        for q_data in SAMPLE_QUESTIONS:
            chapter = q_data.pop("kp_chapter")
            kp = kps.get(chapter)
            if not kp:
                print(f"  Warning: 找不到章节 {chapter}，跳过题目。")
                continue

            question = Question(**q_data)
            session.add(question)
            await session.flush()

            session.add(QuestionKnowledgePoint(
                question_id=question.id,
                knowledge_point_id=kp.id,
            ))
            count += 1

        await session.commit()
        print(f"示例题目初始化完成！共导入 {count} 道题目。")
        print("题型分布：选择题、填空题、程序阅读题、分析题、计算题")


if __name__ == "__main__":
    asyncio.run(seed())
