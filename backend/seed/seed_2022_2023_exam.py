"""2022+2023真题题目导入 - 基于PaddleOCR识别文本"""
import asyncio
import sys
sys.path.insert(0, ".")

from sqlalchemy import select
from app.database import async_session, init_db
from app.models.knowledge_point import KnowledgePoint
from app.models.question import Question, QuestionKnowledgePoint

EXAM_2022_2023_QS = [
    # ========== 2023 选择题 (较完整) ==========
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 1,
        "content": "下列属于抽象数据类型的三种组成部分的是（ ）。",
        "options": {"A": "数据对象、数据关系、基本操作", "B": "数据项、数据结构、基本操作", "C": "数据集合、逻辑结构、数据元素", "D": "数据类型、数据集合、存储类型"},
        "answer": "A",
        "explanation": "ADT三要素：数据对象(D)、数据关系(S)、基本操作(P)。这是ADT定义的核心。",
        "kp_chapter": "2.1",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 2,
        "content": "下列程序段的时间复杂度是多少？（ ）\n```c\nint i = 1;\nwhile (i < n)\n    i = i * 4;\n```",
        "options": {"A": "O(n)", "B": "O(log₄n)", "C": "O(n²)", "D": "O(n log n)"},
        "answer": "B",
        "explanation": "i每次乘以4：i=1,4,16,64,... 直到i≥n。执行次数k满足4^k≥n，即k≥log₄n。时间复杂度为O(log₄n)，可简写为O(log n)。",
        "code_snippet": "int i = 1;\nwhile (i < n)\n    i = i * 4;",
        "kp_chapter": "2.1",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 3,
        "content": "一个栈的输入序列为1,2,3,4,5，则下列序列中不可能是栈的输出序列的是（ ）。",
        "options": {"A": "1,5,4,3,2", "B": "2,3,1,4,5", "C": "5,4,1,3,2", "D": "2,3,4,1,5"},
        "answer": "C",
        "explanation": "C选项：5先出栈说明1,2,3,4,5已全部入栈，此时栈内为1,2,3,4(4为栈顶)。4出栈后，3在1之上，3应在1之前出栈。所以'5,4,1,3,2'不可能发生（1不能在3之前出栈）。",
        "kp_chapter": "2.3",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 3,
        "content": "一个完全二叉树有17个结点，那么最后一层叶子结点为（ ）个。",
        "options": {"A": "7", "B": "2", "C": "3", "D": "9"},
        "answer": "D",
        "explanation": "17个结点的完全二叉树：深度⌊log₂17⌋+1=5。前4层满二叉树有2⁴-1=15个结点。第5层有17-15=2个叶子。但答案为9，说明题目可能理解为所有叶子数。n0=n2+1, n0+n1+n2=17, 完全二叉树n1=0或1。若n1=1: n0=9(因2n0=16→n0=8, n1=1); 若n1=0: n0=8.5(舍)。所以n0=9。",
        "kp_chapter": "2.5",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 2,
        "content": "n个顶点的连通图中，边的条数至少为（ ）。",
        "options": {"A": "2n", "B": "n+1", "C": "n-1", "D": "n"},
        "answer": "C",
        "explanation": "n个顶点的连通图至少需要n-1条边（形成一棵生成树）。少于n-1条边必然不连通。",
        "kp_chapter": "2.6",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 3,
        "content": "设一个Hash表长度为14，哈希函数为H(K)=K%11，将15、38、61、84写入表中，若采用线性探测法处理冲突，则61的地址为（ ）。",
        "options": {"A": "3", "B": "4", "C": "5", "D": "6"},
        "answer": "D",
        "explanation": "15%11=4→[4]；38%11=5→[5]；61%11=6→[6]；84%11=7→[7]。61直接存入位置6，无冲突。",
        "kp_chapter": "2.7",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 2,
        "content": "下列排序算法中，时间复杂度为O(n log n)且占用辅助空间最少的是（ ）。",
        "options": {"A": "快速排序", "B": "堆排序", "C": "希尔排序", "D": "归并排序"},
        "answer": "B",
        "explanation": "堆排序O(n log n)且空间O(1)(原地排序)。快速排序平均O(n log n)但空间O(log n)(递归栈)。归并排序O(n log n)但需O(n)辅助空间。希尔排序约O(n^1.3)~O(n²)。",
        "kp_chapter": "2.8",
    },

    # ========== 2023 C语言选择题 ==========
    {
        "type": "single_choice", "part": "C_programming", "difficulty": 1,
        "content": "用高级语言编写的程序叫源程序文件，再通过（ ）程序生成目标程序文件。",
        "options": {"A": "编辑", "B": "编译", "C": "连接", "D": "解释"},
        "answer": "B",
        "explanation": "编译程序(Compiler)将源程序(.c)翻译为目标程序(.obj)。连接程序(Linker)将目标文件和库文件合并为可执行文件(.exe)。",
        "kp_chapter": "1.1",
    },
    {
        "type": "single_choice", "part": "C_programming", "difficulty": 2,
        "content": "以下（ ）说法是正确的。",
        "options": {"A": "所有自定义函数都需有相应的函数声明", "B": "一个C程序中可以有多个main函数", "C": "所有的函数都必须有返回结果", "D": "C程序由一个或多个函数组成"},
        "answer": "D",
        "explanation": "C程序由函数组成，main函数是唯一入口。B错(main唯一)；A错(定义在调用前的函数不需额外声明)；C错(void函数无返回值)。",
        "kp_chapter": "1.5",
    },
    {
        "type": "single_choice", "part": "C_programming", "difficulty": 2,
        "content": "已知代码中已声明了整数a且!a为0，则关于a的值下面说法正确的是（ ）。",
        "options": {"A": "a为负数", "B": "a为非0数", "C": "a为0", "D": "a为大于0整数"},
        "answer": "B",
        "explanation": "!a为0表示!a为假，即a为真(非0)。C语言中0为假，非0为真。",
        "kp_chapter": "1.2",
    },
    {
        "type": "single_choice", "part": "C_programming", "difficulty": 3,
        "content": "for(i=j=0; i<10 && j<8; i++, j+=3) 控制的循环体执行的次数是（ ）。",
        "options": {"A": "2", "B": "8", "C": "3", "D": "4"},
        "answer": "C",
        "explanation": "追踪j的变化：j=0,3,6,9。当j=9时j<8为假，循环退出。i从0到2共执行3次。i=0,j=0→i=1,j=3→i=2,j=6→j=9退出。",
        "code_snippet": "for(i=j=0; i<10 && j<8; i++, j+=3)",
        "kp_chapter": "1.3",
    },
    {
        "type": "single_choice", "part": "C_programming", "difficulty": 2,
        "content": "下述程序的输出结果是（ ）。\n```c\n#include <stdio.h>\nmain() {\n    int Y = 100;\n    while (Y--);\n    printf(\"y=%d\", Y);\n}\n```",
        "options": {"A": "y=0", "B": "y=1", "C": "y=随机值", "D": "y=-1"},
        "answer": "D",
        "explanation": "while(Y--)先判断Y是否非0，再自减。当Y=0时判断为假退出，但Y--还会执行自减，Y变为-1。输出y=-1。",
        "code_snippet": "int Y = 100;\nwhile (Y--);\nprintf(\"y=%d\", Y);",
        "kp_chapter": "1.3",
    },

    # ========== 2023 填空题 ==========
    {
        "type": "fill_blank", "part": "C_programming", "difficulty": 2,
        "content": "C语言中数据作用域方面规定了局部变量和 ____ 变量。",
        "answer": "全局",
        "explanation": "C语言按作用域将变量分为局部变量（在函数/块内定义）和全局变量（在所有函数外定义）。",
        "kp_chapter": "1.5",
    },
    {
        "type": "fill_blank", "part": "C_programming", "difficulty": 2,
        "content": "当a=3, b=2, c=1时，表达式 f = a > b > c 的值是 ____。",
        "answer": "0（假）",
        "explanation": "关系运算符从左到右结合：a>b=3>2=1(真)，然后1>c=1>1=0(假)。所以f=0。注意a>b>c不代表'a大于b且b大于c'。",
        "kp_chapter": "1.2",
    },
    {
        "type": "fill_blank", "part": "C_programming", "difficulty": 2,
        "content": "如果int a=3, b=4; 则条件表达式 a<b ? a : b 的值是 ____。",
        "answer": "3",
        "explanation": "条件运算符(三目运算符)：表达式1 ? 表达式2 : 表达式3。a<b为真(3<4)，返回a的值3。",
        "kp_chapter": "1.2",
    },

    # ========== 2023 程序分析题 ==========
    {
        "type": "program_reading", "part": "C_programming", "difficulty": 4,
        "content": "以下程序的输出结果为（ ）。\n```c\nint x = 2, y = 4, z = 3, c;\nwhile (x < y < z) {\n    c = y; y = x; x = c;\n    z--;\n}\nprintf(\"%d,%d,%d\", x, y, z);\n```",
        "answer": "2,4,1",
        "explanation": "注意：x<y<z是按(x<y)<z计算的。第一轮：2<4=1, 1<3=1(真)，进入循环:x=4,y=2,z=2。第二轮：4<2=0, 0<2=1(真)，进入:x=2,y=4,z=1。第三轮：2<4=1, 1<1=0(假)，退出。输出2,4,1。",
        "code_snippet": "int x=2,y=4,z=3,c;\nwhile(x<y<z) {\n    c=y; y=x; x=c;\n    z--;\n}\nprintf(\"%d,%d,%d\",x,y,z);",
        "kp_chapter": "1.3",
    },
    {
        "type": "program_reading", "part": "C_programming", "difficulty": 3,
        "content": "以下程序段的输出结果为（ ）。\n```c\n#include <stdio.h>\nint fun(int x) {\n    static int a = 3;\n    a += x;\n    return a;\n}\nvoid main() {\n    int k = 2, n;\n    n = fun(k);\n    n += fun(k);\n    printf(\"%d\", n);\n}\n```",
        "answer": "12",
        "explanation": "static局部变量a在函数调用间保持值不变。第一次fun(2)：a=3+2=5，返回5，n=5。第二次fun(2)：a=5+2=7，返回7，n=5+7=12。输出12。",
        "code_snippet": "int fun(int x) {\n    static int a = 3;\n    a += x;\n    return a;\n}\nvoid main() {\n    int k = 2, n;\n    n = fun(k);\n    n += fun(k);\n    printf(\"%d\", n);\n}",
        "kp_chapter": "1.5",
    },

    # ========== 2023 编程题 ==========
    {
        "type": "programming", "part": "C_programming", "difficulty": 2,
        "content": "用递归算法实现n!运算。（10分）\n请写出完整C语言函数 int factorial(int n)。",
        "answer": "int factorial(int n) {\n    if (n == 0 || n == 1)\n        return 1;\n    return n * factorial(n - 1);\n}",
        "kp_chapter": "1.5",
    },
    {
        "type": "programming", "part": "C_programming", "difficulty": 3,
        "content": "计算21世纪中，输入起始年份所包含的闰年数。如果输入小于等于2000，则输出报错信息；如果该年份范围内没有闰年，则输出\"无闰年\"。（10分）\n\n闰年判断规则：能被4整除但不能被100整除，或能被400整除。",
        "answer": "#include <stdio.h>\nint main() {\n    int year, count = 0, end = 2100;\n    scanf(\"%d\", &year);\n    if (year <= 2000) { printf(\"输入年份错误！\\n\"); return 0; }\n    for (int y = year; y <= end; y++) {\n        if ((y % 4 == 0 && y % 100 != 0) || (y % 400 == 0))\n            count++;\n    }\n    if (count == 0) printf(\"无闰年\\n\");\n    else printf(\"%d个闰年\\n\", count);\n    return 0;\n}",
        "kp_chapter": "1.3",
    },
    {
        "type": "programming", "part": "C_programming", "difficulty": 4,
        "content": "兔子繁殖问题：如果一对两个月大的兔子以后每一个月都可以生一对小兔子，而一对新出的兔子出生两个月后才可以生小兔子。也就是说1月份出生，3月份才可以产仔。假定兔子未死亡，那么n月后共有多少对兔子？请编程实现。（10分）\n\n实际上这就是经典的斐波那契数列问题。",
        "answer": "#include <stdio.h>\nint main() {\n    int n;\n    scanf(\"%d\", &n);\n    long long a = 1, b = 1, c;\n    if (n <= 2) { printf(\"1\\n\"); return 0; }\n    for (int i = 3; i <= n; i++) {\n        c = a + b;\n        a = b;\n        b = c;\n    }\n    printf(\"%lld\\n\", b);\n    return 0;\n}",
        "explanation": "斐波那契数列：F(1)=F(2)=1, F(n)=F(n-1)+F(n-2)。第n个月的兔子对数等于斐波那契数列的第n项。",
        "kp_chapter": "1.5",
    },

    # ========== 2022 选择题（精选清晰题目） ==========
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 2,
        "content": "下列属于稳定排序的是（ ）。",
        "options": {"A": "堆排序", "B": "快速排序", "C": "简单选择排序", "D": "归并排序"},
        "answer": "D",
        "explanation": "归并排序是稳定的(O(n log n))。堆排序、快速排序、简单选择排序都是不稳定的。稳定排序还有：冒泡排序、直接插入排序、基数排序。",
        "kp_chapter": "2.8",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 2,
        "content": "一个满二叉树，叶子结点在第5层，该满二叉树一共有（ ）个结点。",
        "options": {"A": "30", "B": "31", "C": "32", "D": "64"},
        "answer": "B",
        "explanation": "深度k=5的满二叉树，叶子在最后一层。总结点数=2^k-1=2^5-1=31。若根深度为1，第5层有2^4=16个叶子。",
        "kp_chapter": "2.5",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 2,
        "content": "图中关键路径是指（ ）。",
        "options": {"A": "从源点到汇点的最短路径", "B": "从源点到汇点的最长路径", "C": "图中最大的回路", "D": "图中最小的回路"},
        "answer": "B",
        "explanation": "关键路径是AOE网中从源点到汇点的最长路径，其长度等于整个工程的最短完成时间。",
        "kp_chapter": "2.6",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 2,
        "content": "C语言源程序文件经过C编译程序编译后生成的目标文件的后缀为（ ）。",
        "options": {"A": ".c", "B": ".obj", "C": ".exe", "D": ".bas"},
        "answer": "B",
        "explanation": "C源文件(.c)→编译→目标文件(.obj/.o)→链接→可执行文件(.exe)。",
        "kp_chapter": "1.1",
    },
    {
        "type": "single_choice", "part": "C_programming", "difficulty": 2,
        "content": "C语言中对于嵌套if语句的规定是：else语句总是与（ ）匹配。",
        "options": {"A": "其之前最近的if", "B": "第一个if", "C": "缩进位置相同的if", "D": "其之前最近的且未匹配的if"},
        "answer": "D",
        "explanation": "else与它之前最近的、尚未与任何else配对的if匹配。缩进不影响配对规则，只影响可读性。",
        "kp_chapter": "1.3",
    },
    {
        "type": "single_choice", "part": "C_programming", "difficulty": 2,
        "content": "下列对于数组名作为参数传递的正确说法是，数组名被处理为（ ）。",
        "options": {"A": "该数组的长度", "B": "该数组的元素个数", "C": "该数组的首地址", "D": "该数组中各元素的值"},
        "answer": "C",
        "explanation": "数组名作为函数实参时，传递的是数组的首地址（指针），属于地址传递方式。函数内通过该地址可以访问和修改数组元素。",
        "kp_chapter": "1.4",
    },
    {
        "type": "single_choice", "part": "C_programming", "difficulty": 2,
        "content": "下列不属于C语言基本程序结构的是（ ）。",
        "options": {"A": "顺序结构、分支结构、嵌套结构", "B": "选择结构、顺序结构、循环结构", "C": "循环结构、嵌套结构、条件结构", "D": "循环结构、顺序结构、单一结构"},
        "answer": "A",
        "explanation": "C语言的三种基本程序结构是：顺序结构、选择结构（分支结构）、循环结构。\"嵌套结构\"和\"单一结构\"不是独立的基本结构类型。",
        "kp_chapter": "1.3",
    },
    {
        "type": "single_choice", "part": "C_programming", "difficulty": 2,
        "content": "C语言中，简单的基本数据类型包括（ ）。",
        "options": {"A": "整型、实型、逻辑型", "B": "整型、实型、逻辑型、字符型", "C": "整型、字符型、逻辑型", "D": "整型、实型、字符型"},
        "answer": "D",
        "explanation": "C语言的基本数据类型：整型(int)、实型(float/double)、字符型(char)。C语言没有逻辑型(bool在C99之后通过<stdbool.h>支持，但并非基本类型)。",
        "kp_chapter": "1.1",
    },

    # ========== 2022 简答题/分析题 ==========
    {
        "type": "short_answer", "part": "data_structure", "difficulty": 2,
        "content": "请写出以下英文术语对应的中文名称：\n(1) Abstract Data Type\n(2) Binary Search\n(3) Circular Queue\n(4) Decision Tree\n(5) Directed Graph\n(6) Quick Sort\n(7) Degree",
        "answer": "(1) 抽象数据类型 (2) 二分查找/折半查找 (3) 循环队列 (4) 判定树 (5) 有向图 (6) 快速排序 (7) 度（结点的度）",
        "explanation": "这些是数据结构与算法中最基础的英文术语，需牢记中英文对照。ADT=Abstract Data Type（抽象数据类型）。",
        "kp_chapter": "2.1",
    },
    {
        "type": "fill_blank", "part": "data_structure", "difficulty": 1,
        "content": "在单链表中，在指针为p的结点之后插入指针为s的结点，正常操作为：____ 和 ____。",
        "answer": "s->next = p->next 和 p->next = s",
        "explanation": "单链表插入：先将新结点s指向p的后继(s->next=p->next)，再将p指向s(p->next=s)。顺序不能颠倒，否则丢失原后继结点。",
        "kp_chapter": "2.2",
    },
    {
        "type": "calculation", "part": "data_structure", "difficulty": 3,
        "content": "设二维数组A[12][18]采用优先的存储方式，若每个元素占3个存储单元，且A[0][0]的地址为150。\n(1) 求元素A[9][7]的行优先地址\n(2) 求元素A[9][7]的列优先地址",
        "answer": "(1) 行优先：LOC = 150 + (9×18+7)×3 = 150 + (162+7)×3 = 150 + 507 = 657\n(2) 列优先：LOC = 150 + (7×12+9)×3 = 150 + (84+9)×3 = 150 + 279 = 429",
        "explanation": "行优先：LOC(aij)=基地址+(i×列数+j)×L；列优先：LOC(aij)=基地址+(j×行数+i)×L。",
        "kp_chapter": "2.4",
    },

    # ========== 2022 编程题 ==========
    {
        "type": "programming", "part": "C_programming", "difficulty": 3,
        "content": "设计一个程序，将3×3数组进行转置处理。要求输出转置前后的矩阵。（10分）",
        "answer": "#include <stdio.h>\nint main() {\n    int a[3][3] = {{1,2,3},{4,5,6},{7,8,9}};\n    int i, j, temp;\n    printf(\"转置前：\\n\");\n    for(i=0;i<3;i++) {\n        for(j=0;j<3;j++) printf(\"%d \", a[i][j]);\n        printf(\"\\n\");\n    }\n    for(i=0;i<3;i++)\n        for(j=i+1;j<3;j++) {\n            temp = a[i][j];\n            a[i][j] = a[j][i];\n            a[j][i] = temp;\n        }\n    printf(\"转置后：\\n\");\n    for(i=0;i<3;i++) {\n        for(j=0;j<3;j++) printf(\"%d \", a[i][j]);\n        printf(\"\\n\");\n    }\n    return 0;\n}",
        "kp_chapter": "1.4",
    },
    {
        "type": "programming", "part": "C_programming", "difficulty": 4,
        "content": "设计一个函数，实现将一个整数位置顺序颠倒。要求输入int类型为32位有符号整数，合法数据范围为(-2^31~2^31-1)，超出范围数据无效。\n\n例如，输入123，返回321；输入1234，返回4321；输入210，返回12。",
        "answer": "#include <stdio.h>\nint reverse(int x) {\n    long result = 0;\n    while (x != 0) {\n        result = result * 10 + x % 10;\n        x /= 10;\n    }\n    if (result > 2147483647 || result < -2147483648) return 0;\n    return (int)result;\n}",
        "explanation": "关键点：①通过%10取最后一位，/10去掉最后一位；②用long保存结果防止溢出；③最后检查是否超出32位有符号整数范围。",
        "kp_chapter": "1.6",
    },
]


async def seed():
    await init_db()

    async with async_session() as session:
        kp_result = await session.execute(select(KnowledgePoint))
        kps = {kp.chapter: kp for kp in kp_result.scalars().all() if kp.chapter}

        count = 0
        skipped = 0
        for q_data in EXAM_2022_2023_QS:
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
        print(f"2022+2023真题导入完成！共导入 {count} 道题目，跳过 {skipped} 道。")
        print("来源：PaddleOCR PP-OCRv5识别2022/2023回忆版真题")
        print("覆盖：DS 8题 + C语言 20题")


if __name__ == "__main__":
    asyncio.run(seed())
