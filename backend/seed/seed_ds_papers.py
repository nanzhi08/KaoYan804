"""数据结构十套卷 题目提取 - 从OCR文本提取的优质题目"""
import asyncio
import sys
sys.path.insert(0, ".")

from sqlalchemy import select
from app.database import async_session, init_db
from app.models.knowledge_point import KnowledgePoint
from app.models.question import Question, QuestionKnowledgePoint

DS_PAPER_QUESTIONS = [
    # ============ 试卷一 选择题 ============
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 1,
        "content": "栈和队列的共同特点是( )。",
        "options": {"A": "只允许在端点处插入和删除元素", "B": "都是先进后出", "C": "都是先进先出", "D": "没有共同点"},
        "answer": "A",
        "explanation": "栈在栈顶操作，队列在队尾插入队头删除，两者都只在线性表的端点处操作。区别在于栈是LIFO，队列是FIFO。",
        "kp_chapter": "2.3",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 2,
        "content": "用链接方式存储的队列，在进行插入运算时( )。",
        "options": {"A": "仅修改头指针", "B": "头、尾指针都要修改", "C": "仅修改尾指针", "D": "头、尾指针可能都要修改"},
        "answer": "D",
        "explanation": "链队插入：一般情况修改尾指针即可。但若队列为空，则插入第一个元素时头尾指针都要修改。因此应选D。",
        "kp_chapter": "2.3",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 1,
        "content": "以下数据结构中哪一个是非线性结构？( )",
        "options": {"A": "队列", "B": "栈", "C": "线性表", "D": "二叉树"},
        "answer": "D",
        "explanation": "队列、栈、线性表都是一对一的线性结构。二叉树是一对多的层次结构，属于非线性结构。",
        "kp_chapter": "2.5",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 2,
        "content": "树最适合用来表示( )。",
        "options": {
            "A": "有序数据元素",
            "B": "无序数据元素",
            "C": "元素之间具有分支层次关系的数据",
            "D": "元素之间无联系的数据"
        },
        "answer": "C",
        "explanation": "树是一种层次结构，最适合表示具有一对多分支关系的数据，如组织结构、目录结构、族谱等。",
        "kp_chapter": "2.5",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 2,
        "content": "二叉树的第k层的结点数最多为( )。",
        "options": {"A": "2k-1", "B": "2k+1", "C": "2^k-1", "D": "2^(k-1)"},
        "answer": "D",
        "explanation": "二叉树第1层最多1个(2^0)，第2层最多2个(2^1)，第k层最多2^(k-1)个。注意与深度为k的总结点数(2^k-1)区分。",
        "kp_chapter": "2.5",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 3,
        "content": "对n个记录的文件进行快速排序，所需要的辅助存储空间大致为( )。",
        "options": {"A": "O(1)", "B": "O(n)", "C": "O(log n)", "D": "O(n²)"},
        "answer": "C",
        "explanation": "快速排序需要递归栈，递规深度平均O(log n)，因此辅助空间为O(log n)。注意与归并排序的O(n)辅助空间区分。",
        "kp_chapter": "2.8",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 2,
        "content": "对于线性表(7,34,55,25,64,46,20,10)进行散列存储时，若选用H(K)=K%9作为散列函数，则散列地址为1的元素有( )个。",
        "options": {"A": "1", "B": "2", "C": "3", "D": "4"},
        "answer": "D",
        "explanation": "计算各元素%9：7%9=7, 34%9=7, 55%9=1, 25%9=7, 64%9=1, 46%9=1, 20%9=2, 10%9=1。地址1的有55,64,46,10共4个。",
        "kp_chapter": "2.7",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 2,
        "content": "设有6个结点的无向图，该图至少应有( )条边才能确保是一个连通图。",
        "options": {"A": "5", "B": "6", "C": "7", "D": "8"},
        "answer": "A",
        "explanation": "n个顶点的连通图至少需要n-1条边（构成一棵树）。6个顶点至少需要5条边。少于n-1条边必然不连通。",
        "kp_chapter": "2.6",
    },

    # ============ 试卷一 填空题 ============
    {
        "type": "fill_blank", "part": "data_structure", "difficulty": 1,
        "content": "通常从四个方面评价算法的质量：____、____、____ 和 ____。",
        "answer": "正确性、可读性、健壮性和高效性（时间效率+空间效率）",
        "explanation": "算法评价四标准：正确性（满足需求）、可读性（易于理解维护）、健壮性（处理异常输入）、高效性（时间复杂度和空间复杂度权衡）。",
        "kp_chapter": "2.1",
    },
    {
        "type": "fill_blank", "part": "data_structure", "difficulty": 3,
        "content": "一个算法的时间复杂度为(n³+n²log₂n+14n)/n²，其数量级表示为 ____。",
        "answer": "O(n)",
        "explanation": "(n³+n²log n+14n)/n² = n + log n + 14/n。当n→∞，最高阶为n，故数量级O(n)。",
        "kp_chapter": "2.1",
    },
    {
        "type": "fill_blank", "part": "data_structure", "difficulty": 3,
        "content": "假定一棵树的广义表表示为A(C,D(E,F,G),H(I,J))，则树中所含的结点数为 ____ 个，树的深度为 ____，树的度为 ____。",
        "answer": "10、3、3",
        "explanation": "结点：A,C,D,E,F,G,H,I,J 共10个。深度：A→D→E/F/G 三层=3。度：A有3个孩子(C,D,H)，D有3个孩子(E,F,G)，最大度=3。",
        "kp_chapter": "2.4",
    },
    {
        "type": "fill_blank", "part": "data_structure", "difficulty": 3,
        "content": "后缀算式 9 2 3 + - 10 2 / - 的值为 ____。中缀算式 (3+4X)-2Y/3 对应的后缀算式为 ____。",
        "answer": "-1 和 3 4 X * + 2 Y * 3 / -",
        "explanation": "后缀求值：9,2,3→2+3=5→9-5=4→10,2→10/2=5→4-5=-1。中缀转后缀：操作数顺序不变，运算符按优先级出栈。",
        "kp_chapter": "2.3",
    },
    {
        "type": "fill_blank", "part": "data_structure", "difficulty": 3,
        "content": "若用链表存储一棵二叉树时，每个结点除数据域外，还有指向左孩子和右孩子的两个指针。在这种存储结构中，n个结点的二叉树共有 ____ 个指针域，其中有 ____ 个指针域是存放了地址，有 ____ 个指针是空指针。",
        "answer": "2n、n-1 和 n+1",
        "explanation": "每个结点2个指针域，共2n个。n个结点有n-1条边，即有n-1个非空指针。空指针=2n-(n-1)=n+1个。这也是线索二叉树的利用基础。",
        "kp_chapter": "2.5",
    },
    {
        "type": "fill_blank", "part": "data_structure", "difficulty": 2,
        "content": "对于一个具有n个顶点和e条边的有向图和无向图，在其对应的邻接表中，所含边结点分别有 ____ 个和 ____ 个。",
        "answer": "e 和 2e",
        "explanation": "无向图每条边在邻接表中出现两次（两个端点各一个边结点），所以有2e个边结点。有向图每条弧只在弧尾的出边表中出现一次，所以有e个。",
        "kp_chapter": "2.6",
    },
    {
        "type": "fill_blank", "part": "data_structure", "difficulty": 2,
        "content": "在一个具有n个顶点的无向完全图中，包含有 ____ 条边，在一个具有n个顶点的有向完全图中，包含有 ____ 条边。",
        "answer": "n(n-1)/2 和 n(n-1)",
        "explanation": "无向完全图：每对顶点间一条边，边数=C(n,2)=n(n-1)/2。有向完全图：每对顶点间有方向相反的两条弧，共n(n-1)条。",
        "kp_chapter": "2.6",
    },
    {
        "type": "fill_blank", "part": "data_structure", "difficulty": 2,
        "content": "在堆排序的过程中，对任一分支结点进行筛运算的时间复杂度为 ____，整个堆排序过程的时间复杂度为 ____。",
        "answer": "O(log n) 和 O(n log n)",
        "explanation": "单次筛(Sift)调整沿树高进行，O(log n)。建堆O(n)，每次取堆顶后调整O(log n)，n次取堆顶=O(n log n)，总计O(n log n)。",
        "kp_chapter": "2.8",
    },
    {
        "type": "fill_blank", "part": "data_structure", "difficulty": 1,
        "content": "在快速排序、堆排序、归并排序中，____ 排序是稳定的。",
        "answer": "归并",
        "explanation": "归并排序在两路合并时保持相等元素的先后次序，是稳定的。快速排序(交换可能破坏顺序)和堆排序(跳跃式交换)都不稳定。",
        "kp_chapter": "2.8",
    },

    # ============ 试卷一 算法填空题 ============
    {
        "type": "fill_blank", "part": "data_structure", "difficulty": 3,
        "content": "以下是二叉搜索树(BST)的递归查找算法，请补全代码：\n```c\nbool Find(BTreeNode* BST, ElemType& item) {\n    if (BST == NULL)\n        return false;\n    else {\n        if (item == BST->data) {\n            item = BST->data;\n            return ____(1)____;\n        }\n        else if (item < BST->data)\n            return Find(____(2)____, item);\n        else\n            return Find(____(3)____, item);\n    }\n}\n```\n(1)____ (2)____ (3)____",
        "answer": "(1) true (2) BST->left (3) BST->right",
        "explanation": "BST查找递归实现：找到返回true；item<当前值去左子树BST->left；item>当前值去右子树BST->right。",
        "code_snippet": "bool Find(BTreeNode* BST, ElemType& item) {\n    if (BST == NULL) return false;\n    if (item == BST->data) { item = BST->data; return true; }\n    if (item < BST->data) return Find(BST->left, item);\n    return Find(BST->right, item);\n}",
        "kp_chapter": "2.7",
    },

    # ============ 试卷二 选择题 ============
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 2,
        "content": "下面关于线性表的叙述错误的是（ ）。",
        "options": {
            "A": "线性表采用顺序存储必须占用一片连续的存储空间",
            "B": "线性表采用链式存储不必占用一片连续的存储空间",
            "C": "线性表采用链式存储便于插入和删除操作的实现",
            "D": "线性表采用顺序存储便于插入和删除操作的实现"
        },
        "answer": "D",
        "explanation": "顺序存储插入和删除需要移动大量元素(O(n))，不便于插入删除。链式存储插入删除只需修改指针(O(1)给定位置)。D选项说反了。",
        "kp_chapter": "2.2",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 3,
        "content": "设某完全无向图有n个顶点，则该完全无向图中有（ ）条边。",
        "options": {"A": "n(n-1)/2", "B": "n(n-1)", "C": "n²", "D": "n²-1"},
        "answer": "A",
        "explanation": "完全无向图：每个顶点与其余n-1个顶点相连，总边数=n(n-1)/2（每条边被两个端点各计算一次，所以要除以2）。",
        "kp_chapter": "2.6",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 2,
        "content": "设某二叉树中度数为0的结点数为N0，度数为1的结点数为N1，度数为2的结点数为N2，则下列等式成立的是（ ）。",
        "options": {"A": "N0=N1+1", "B": "N0=N2+1", "C": "N0=N1+N2", "D": "N0=2N1+1"},
        "answer": "B",
        "explanation": "二叉树性质：叶子结点数=度为2的结点数+1，即n0=n2+1。这是二叉树的基本性质。",
        "kp_chapter": "2.5",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 2,
        "content": "设有序表中有1000个元素，则用二分查找元素X最多需要比较（ ）次。",
        "options": {"A": "10", "B": "11", "C": "25", "D": "500"},
        "answer": "A",
        "explanation": "二分查找最多比较次数=⌊log₂n⌋+1=⌊log₂1000⌋+1=9+1=10次（或直接取ceil(log₂(1000+1))≈10）。",
        "kp_chapter": "2.7",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 3,
        "content": "设一组初始记录关键字序列为(345,253,674,924,627)，则以增量d=3的一趟希尔排序结束后前4条记录的关键字为（ ）。",
        "options": {"A": "345,253,674,924", "B": "345,253,674,627", "C": "345,627,674,924", "D": "627,253,674,924"},
        "answer": "A",
        "explanation": "d=3分组：{345,924}(下标0,3)→排序{345,924}；{253,627}(下标1,4)→排序{253,627}；{674}单元素不变。一趟后：345,253,674,924,627。前4个为345,253,674,924。",
        "kp_chapter": "2.8",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 2,
        "content": "设某强连通图中有n个顶点，则该强连通图中至少有（ ）条边。",
        "options": {"A": "n(n-1)", "B": "n+1", "C": "n", "D": "n(n+1)"},
        "answer": "C",
        "explanation": "有向强连通图至少需要n条边（构成一个环）。无向连通图至少需要n-1条边（一棵树）。注意强连通图是有向图的概念。",
        "kp_chapter": "2.6",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 3,
        "content": "设有5000个待排序的记录关键字，如果需要用最快的方法选出其中最小的10个记录关键字，则用（ ）方法可以达到此目的。",
        "options": {"A": "快速排序", "B": "堆排序", "C": "归并排序", "D": "插入排序"},
        "answer": "B",
        "explanation": "选出最小10个→TopK问题。建小顶堆O(n)，取10次堆顶O(10 log n)。直接用堆排序或部分堆排序最合适。也可维护大小为10的大顶堆，遍历一遍O(n log 10)。",
        "kp_chapter": "2.8",
    },

    # ============ 试卷二 填空题 ============
    {
        "type": "fill_blank", "part": "data_structure", "difficulty": 3,
        "content": "设某棵二叉树的中序遍历序列为ABCDEFG，后序遍历序列为BDCAFGE，则该二叉树的先序遍历序列为 ____。",
        "answer": "EACBDGF",
        "explanation": "后序末字母E为根。中序中E左边ABCD为左子树，右边FG为右子树。左子树：后序BDCA→A为根；左子树的左子树：后序BDC中B为叶子？继续递归推导得：E为根，左子树A（左B右C，C有左D），右子树G（左F）。先序：E,A,B,C,D,G,F→EACBDGF。",
        "kp_chapter": "2.5",
    },
    {
        "type": "fill_blank", "part": "data_structure", "difficulty": 3,
        "content": "设有一个顺序共享栈Share[0..n-1]，其中第一个栈顶指针top1的初值为-1，第二个栈顶指针top2的初值为n，则判断共享栈满的条件是 ____。",
        "answer": "top1 + 1 == top2（或 top2 - top1 == 1）",
        "explanation": "两个栈从数组两端向中间增长。栈1从0→n-1增长(top1++)，栈2从n-1→0增长(top2--)。当top1+1==top2时两个栈顶相遇，栈满。",
        "kp_chapter": "2.3",
    },
]


async def seed():
    await init_db()

    async with async_session() as session:
        kp_result = await session.execute(select(KnowledgePoint))
        kps = {kp.chapter: kp for kp in kp_result.scalars().all() if kp.chapter}

        count = 0
        skipped = 0
        for q_data in DS_PAPER_QUESTIONS:
            chapter = q_data.pop("kp_chapter")
            kp = kps.get(chapter)
            if not kp:
                print(f"  Warning: 找不到章节 {chapter}，跳过题目。")
                skipped += 1
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
        print(f"DS十套卷题目导入完成！共导入 {count} 道题目，跳过 {skipped} 道。")
        print("来源：数据结构十套卷OCR文本（EasyOCR识别）")
        print("覆盖：试卷一(18题) + 试卷二(10题) 的精华题目")


if __name__ == "__main__":
    asyncio.run(seed())
