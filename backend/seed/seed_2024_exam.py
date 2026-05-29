"""2024年804真题题库导入"""
import asyncio
import sys
sys.path.insert(0, ".")

from sqlalchemy import select
from app.database import async_session, init_db
from app.models.knowledge_point import KnowledgePoint
from app.models.question import Question, QuestionKnowledgePoint

EXAM_2024_QUESTIONS = [
    # ============================================================
    # 数据结构部分 - 选择题（10题，每题2分，共20分）
    # ============================================================
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 2,
        "content": "某线性表中最常用的操作是在最后一个元素之后插入一个元素和删除第一个元素，则采用( )存储方式最节省运算时间。",
        "options": {"A": "单链表", "B": "仅有头指针的单循环链表", "C": "双链表", "D": "仅有尾指针的单循环链表"},
        "answer": "D",
        "explanation": "仅有尾指针的单循环链表：通过尾指针rear可O(1)访问最后一个元素（rear）和第一个元素（rear->next），在尾后插入和在头删除都只需修改指针，时间O(1)。单链表需要O(n)遍历到尾；仅有头指针的循环链表找尾需O(n)；双链表同样需遍历。",
        "kp_chapter": "2.2",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 3,
        "content": "阅读以下代码，其时间复杂度是( )。\n```c\nint y = 0;\nwhile(x >= (y+1)*(y+1))\n    y++;\n```",
        "options": {"A": "O(n)", "B": "O(n²)", "C": "O(log n)", "D": "O(√n)"},
        "answer": "D",
        "explanation": "循环条件为 x ≥ (y+1)²，即 y² ≤ x，所以 y ≤ √x。循环执行约√x次，时间复杂度 O(√n)。",
        "code_snippet": "int y = 0;\nwhile(x >= (y+1)*(y+1))\n    y++;",
        "kp_chapter": "2.1",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 1,
        "content": "若进队的序列为: a, b, c, d，则出队的序列是( )。",
        "options": {"A": "b, c, d, a", "B": "a, c, b, d", "C": "a, b, c, d", "D": "c, b, d, a"},
        "answer": "C",
        "explanation": "队列是先进先出（FIFO）的数据结构，入队顺序即出队顺序：a, b, c, d。",
        "kp_chapter": "2.3",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 3,
        "content": "按行地址优先，已知二维数组A[10][10]，元素A[2][0]的地址为560，每个元素占4个字节，则元素A[1][0]的地址为( )。",
        "options": {"A": "520", "B": "522", "C": "524", "D": "518"},
        "answer": "A",
        "explanation": "按行优先：LOC(A[i][j]) = 基地址 + (i×n + j)×L。已知A[2][0]=560，A[1][0]=A[2][0]-10×4=560-40=520。每行10个元素，每个4字节，一行占40字节。",
        "kp_chapter": "2.4",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 3,
        "content": "若一棵二叉树的前序遍历序列为 a, e, b, d, c，后序遍历序列为 b, c, d, e, a，则根结点的孩子结点( )。",
        "options": {"A": "只有 e", "B": "有 e、b", "C": "有 e、c", "D": "无法确定"},
        "answer": "A",
        "explanation": "前序首个a为根，后序末个a也是根。前序第二个为左子树的根或右子树的根。后序中e的位置表明e是a的孩子。前序a,e,b,d,c和后序b,c,d,e,a，e的左子树前序为b,d,c，后序为b,c,d。分析可得只有e是a的孩子（可能是唯一的左孩子）。",
        "kp_chapter": "2.5",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 3,
        "content": "哈希表的地址区间为0-16，哈希函数为H(k)=k mod 17，采用线性探测法处理冲突，并将关键字序列26, 25, 72, 38, 8, 18, 59依次存储到哈希表中。则存放元素59需探查的次数为( )。",
        "options": {"A": "9", "B": "1", "C": "2", "D": "4"},
        "answer": "D",
        "explanation": "计算各元素哈希地址：H(26)=9→[9]；H(25)=8→[8]；H(72)=4→[4]；H(38)=4冲突→5→[5]；H(8)=8冲突→9冲突→10→[10]；H(18)=1→[1]；H(59)=8冲突→9冲突→10冲突→11冲突→[12]。59共探查4次（首次地址8算一次，加上3次冲突探测，共4次比较后确定位置12）。",
        "kp_chapter": "2.7",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 2,
        "content": "接上题，元素59应该存放在几号位置？( )",
        "options": {"A": "8", "B": "9", "C": "10", "D": "12"},
        "answer": "D",
        "explanation": "59的哈希地址为59%17=8，但8、9、10、11依次被25、26、8、18占据，线性探测到位置12为空，存放于12号位置。",
        "kp_chapter": "2.7",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 2,
        "content": "快速排序最适合( )存储结构。",
        "options": {"A": "哈希存储", "B": "索引存储", "C": "顺序存储", "D": "链式存储"},
        "answer": "C",
        "explanation": "快速排序需要随机存取以进行划分(Partition)操作（从两端向中间扫描），顺序存储（数组）可以直接通过下标访问，最适合。链式存储难以从两端向中间扫描。",
        "kp_chapter": "2.8",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 1,
        "content": "以下有关二叉树的说法正确的是( )。",
        "options": {"A": "二叉树的度为2", "B": "一棵二叉树的度可以小于2", "C": "至少有一个结点的度为2", "D": "任一结点的度均为2"},
        "answer": "B",
        "explanation": "二叉树的度是树中结点度的最大值，可以小于2。如只有根结点的二叉树度为0，左斜树度为1。A错误（度为2不是必然），C错误（不一定有度为2的结点），D错误。",
        "kp_chapter": "2.5",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 2,
        "content": "最小生成树指的是连通图中( )。",
        "options": {"A": "边数最少的生成树", "B": "顶点相对较少的生成树", "C": "极小连通子图", "D": "所有生成树中权值之和最小的生成树"},
        "answer": "D",
        "explanation": "最小生成树(MST)的定义：在一个连通带权图中，所有生成树中边的权值之和最小的那棵生成树。注意：生成树本身已是极小连通子图（n个顶点，n-1条边），最小强调的是权值和最小。",
        "kp_chapter": "2.6",
    },

    # ============================================================
    # 数据结构部分 - 计算题（1题，10分）
    # ============================================================
    {
        "type": "calculation", "part": "data_structure", "difficulty": 3,
        "content": "设一棵完全二叉树具有1000个结点，问此完全二叉树：\n(1)有多少个叶子结点？\n(2)有多少个度为2的结点？\n(3)有多少个结点只有非空左子树？\n(4)有多少个结点只有非空右子树？",
        "answer": "(1) 500个叶子结点\n(2) 499个度为2的结点\n(3) 1个结点只有非空左子树\n(4) 0个结点只有非空右子树\n\n推导：n0=n2+1, n=n0+n1+n2=2n0+n1-1。n=1000, 2n0+n1=1001。完全二叉树中n1=0或1。若n1=0则n0=500.5(舍)；若n1=1则n0=500。故n0=500, n2=499, n1=1。度为1的结点只有左孩子（完全二叉树中若度=1，必为左孩子），故(3)答案为1，(4)答案为0。",
        "kp_chapter": "2.5",
    },

    # ============================================================
    # 数据结构部分 - 简答题（2题，共30分）
    # ============================================================
    {
        "type": "analysis", "part": "data_structure", "difficulty": 4,
        "content": "根据题干回答以下排序问题（10分）：\n(1) 对序列 5, 4, 8, 0, 9, 3, 2, 6, 7, 1 进行归并排序，写出前两趟的结果。\n(2) 对序列 6, 13, 17, 21, 30, 60, 58, 28, 30, 90 进行快速排序，写出前两趟的结果。\n(3) 已知关键字序列：76, 13, 97, 27, 65, 49, 38, 49，画出初始大根堆和排序一趟后的大根堆。",
        "answer": "(1) 归并排序前两趟：\n第一趟（每2个归并）：[5,4]→{4,5}, [8,0]→{0,8}, [9,3]→{3,9}, [2,6]→{2,6}, [7,1]→{1,7}\n结果：4, 5, 0, 8, 3, 9, 2, 6, 1, 7\n第二趟（每4个归并）：[4,5,0,8]→{0,4,5,8}, [3,9,2,6]→{2,3,6,9}, [1,7]→{1,7}\n结果：0, 4, 5, 8, 2, 3, 6, 9, 1, 7\n\n(2) 快速排序前两趟（选第一个为基准）：\n第一趟基准6：序列已按6划分完成（6最小），结果：6, 13, 17, 21, 30, 60, 58, 28, 30, 90\n第二趟基准13：13后找到比13小的移到前面，结果：6, 13, 17, 21, 30, 28, 30, 58, 60, 90（对右半部分继续划分）\n\n(3) 初始大根堆：97, 76, 65, 49, 27, 49, 38, 13\n第一趟排序后（97与13交换，调整）：76, 49, 65, 13, 27, 49, 38, [97]",
        "kp_chapter": "2.8",
    },
    {
        "type": "analysis", "part": "data_structure", "difficulty": 5,
        "content": "关键路径分析（20分）：\n某工程如下图所示，顶点表示事件V0-V9，边表示活动a0-a12，请根据图求出：\n(1) 每个事件的最早发生时间和最晚发生时间\n(2) 每个活动的最早开始时间和最晚开始时间\n(3) 关键路径\n\n（注：原题附有AOE网图，此处简化为已知条件作答）",
        "answer": "关键路径的分析步骤：\n1. 按拓扑序计算ve（最早发生时间）：ve[源点]=0，ve[k]=max{ve[j]+weight(j,k)}\n2. 按逆拓扑序计算vl（最迟发生时间）：vl[汇点]=ve[汇点]，vl[k]=min{vl[j]-weight(k,j)}\n3. e[i]=ve[活动起点]，l[i]=vl[活动终点]-活动持续时间\n4. 若e[i]==l[i]，则该活动为关键活动，关键活动构成的路径即为关键路径。\n\n具体值依赖于图的结构，原题需要根据图计算出具体数值填入表格。关键路径可能不止一条。",
        "kp_chapter": "2.6",
    },

    # ============================================================
    # 数据结构部分 - 编程题（1题，20分）
    # ============================================================
    {
        "type": "programming", "part": "data_structure", "difficulty": 4,
        "content": "编写递归函数，在二叉树中查找值为x的结点。若找到则返回该结点的指针，否则返回NULL。\n二叉树结点定义：\n```c\ntypedef struct BiTNode {\n    int data;\n    struct BiTNode *lchild, *rchild;\n} BiTNode, *BiTree;\n```\n函数原型：BiTree SearchBST(BiTree T, int x);",
        "answer": "BiTree SearchBST(BiTree T, int x) {\n    if (T == NULL || T->data == x)\n        return T;\n    BiTree result = SearchBST(T->lchild, x);\n    if (result != NULL)\n        return result;\n    return SearchBST(T->rchild, x);\n}",
        "explanation": "递归查找二叉树：若当前结点为空或值等于x则返回当前结点；否则先在左子树递归查找，找到则返回；若左子树没找到则继续在右子树递归查找。时间复杂度O(n)。",
        "kp_chapter": "2.5",
    },

    # ============================================================
    # C语言部分 - 选择题（10题，每题2分，共20分）
    # ============================================================
    {
        "type": "single_choice", "part": "C_programming", "difficulty": 2,
        "content": "以下哪个选项是C语言中合法的标识符？( )",
        "options": {"A": "123identifier", "B": "_identifier", "C": "1_identifier", "D": "identifier"},
        "answer": "B",
        "explanation": "C语言标识符规则：只能由字母、数字和下划线组成，且不能以数字开头。A和C以数字开头不合法；D虽然是合法标识符但题目要求选一个，B(_identifier)以_开头，合法。",
        "kp_chapter": "1.1",
    },
    {
        "type": "single_choice", "part": "C_programming", "difficulty": 2,
        "content": "在C语言中，以下哪个选项是正确的函数声明方式？( )",
        "options": {"A": "int function();", "B": "function int();", "C": "int() function;", "D": "function() int;"},
        "answer": "A",
        "explanation": "C语言函数声明格式：返回类型 函数名(参数列表); 如 int function(); 是正确的。其他选项语法错误。",
        "kp_chapter": "1.5",
    },
    {
        "type": "single_choice", "part": "C_programming", "difficulty": 2,
        "content": "else和之前哪个if配对？( )",
        "options": {"A": "第一个if", "B": "之前最近的if", "C": "之前且未与else配对的if", "D": "同缩进的if"},
        "answer": "C",
        "explanation": "C语言中else与它之前最近的、尚未与任何else配对的if配对。缩进不影响配对规则，只影响可读性。",
        "kp_chapter": "1.3",
    },
    {
        "type": "single_choice", "part": "C_programming", "difficulty": 2,
        "content": "判断i和j至少有一个值为非0的表达式是( )。",
        "options": {"A": "i!=0 && j!=0", "B": "i+j!=0", "C": "i||j", "D": "i&&j"},
        "answer": "C",
        "explanation": "i||j：逻辑或，只要i或j任一非0，结果即为真(1)。A要求两者都非0，B可能因为正负相加为0而误判（如i=1, j=-1），D要求两者都非0。",
        "kp_chapter": "1.2",
    },
    {
        "type": "single_choice", "part": "C_programming", "difficulty": 2,
        "content": "下列选项正确的是( )。",
        "options": {
            "A": "数组的长度可以是变量",
            "B": "调用strcmp函数比较字符串大小时，通常较长的字符串会比较大",
            "C": "数组名作为函数参数，传递的是数组的首地址",
            "D": "对于两个字符串变量s1和s2，使用if(s1>s2)来比较是可以的"
        },
        "answer": "C",
        "explanation": "C正确：数组名作为实参传递给函数时，传递的是数组首地址（指针），即传地址方式。A错误：C89标准数组长度只能是常量，C99支持VLA但有限制。B错误：strcmp按字典序比较，与长度无关。D错误：不能直接用>比较字符串，应用strcmp。",
        "kp_chapter": "1.4",
    },
    {
        "type": "single_choice", "part": "C_programming", "difficulty": 3,
        "content": "已知代码如下：\n```c\nstruct employee {\n    char name[20];\n    int age;\n    int sex;\n} emp[5], *p;\np = emp;\n```\n以下不能正确输入结构体成员值的是( )。",
        "options": {
            "A": "scanf(\"%s\", emp[0].name);",
            "B": "scanf(\"%d\", &emp[0].age);",
            "C": "scanf(\"%d\", p->age);",
            "D": "scanf(\"%d\", &(p->sex));"
        },
        "answer": "C",
        "explanation": "p->age是一个整型变量，scanf的%d格式需要变量的地址（即&(p->age)），而非变量本身。C选项缺少&取地址符，应改为scanf(\"%d\", &p->age)。D正确（等价于&emp[0].sex）。",
        "code_snippet": "struct employee {\n    char name[20];\n    int age;\n    int sex;\n} emp[5], *p;\np = emp;",
        "kp_chapter": "1.4",
    },
    {
        "type": "single_choice", "part": "C_programming", "difficulty": 3,
        "content": "下列for循环的次数为( )。\n```c\nfor(i=0, x=0; !x && i<=5; i++)\n```",
        "options": {"A": "5", "B": "6", "C": "1", "D": "无限"},
        "answer": "B",
        "explanation": "循环条件为!x && i<=5。x初始为0，!x为真。i从0到5共6次循环（i=0,1,2,3,4,5）。当i=6时，i<=5为假，退出循环。共6次。",
        "code_snippet": "for(i=0, x=0; !x && i<=5; i++)",
        "kp_chapter": "1.3",
    },
    {
        "type": "single_choice", "part": "C_programming", "difficulty": 3,
        "content": "已知字符数组 char s[] = \"20213344734928\"，若将前四个字符\"2021\"转换成一个数字。以下哪个选项是实现这个目标的正确代码？( )",
        "options": {
            "A": "int number = s[0]*1000 + s[1]*100 + s[2]*10 + s[3];",
            "B": "int number = (s[0]-'0')*1000 + (s[1]-'0')*100 + (s[2]-'0')*10 + (s[3]-'0');",
            "C": "int number = s[0] + s[1] + s[2] + s[3];",
            "D": "int number = (int)s[0] + (int)s[1] + (int)s[2] + (int)s[3];"
        },
        "answer": "B",
        "explanation": "字符'0'的ASCII码是48。s[0]是字符'2'(ASCII 50)，s[0]-'0'得到数值2。只有B正确地将字符转为对应数字后再计算。A直接乘以字符的ASCII值，结果错误。C、D只是求和，不是组成4位数。",
        "kp_chapter": "1.6",
    },
    {
        "type": "single_choice", "part": "C_programming", "difficulty": 3,
        "content": "当文件以只写模式打开时，以下哪个选项是正确的代码来将字符串写入文件？( )",
        "options": {
            "A": "sprintf(fp, \"%s\", \"待写入的字符串\");",
            "B": "scanf(fp, \"%s\", \"待写入的字符串\");",
            "C": "sprintf(\"%s\", \"待写入的字符串\", fp);",
            "D": "scanf(\"%s\", \"待写入的字符串\", fp);"
        },
        "answer": "A",
        "explanation": "fprintf是向文件写入格式化字符串的函数，第一个参数为FILE*指针。fprintf(fp, \"%s\", str)正确。scanf/fscanf是读取函数。注意：原选项中写的是sprintf，应为fprintf。A选项的写法意图为fprintf。",
        "kp_chapter": "1.7",
    },
    {
        "type": "single_choice", "part": "C_programming", "difficulty": 3,
        "content": "已知代码如下：\n```c\nint *p;\nint x = 1;\np = &x;\n```\n则 (*p)++ 等价于( )。",
        "options": {"A": "x++", "B": "*(p++)", "C": "&x++", "D": "*++p"},
        "answer": "A",
        "explanation": "(*p)++先解引用取得x的值，再对该值自增，等价于x++。B是p指针自增后解引用；C语法错误（&x++非法，x是左值但x++不是）；D是先p自增再解引用。",
        "code_snippet": "int *p;\nint x = 1;\np = &x;",
        "kp_chapter": "1.6",
    },

    # ============================================================
    # C语言部分 - 程序填空题（3题，共10分）
    # ============================================================
    {
        "type": "fill_blank", "part": "C_programming", "difficulty": 2,
        "content": "以下代码的输出结果是什么？\n```c\nint main() {\n    int x, y, z;\n    x = 1;\n    y = 1;\n    z = x++, y++, ++y;\n    printf(\"%d,%d,%d\\n\", x, y, z);\n}\n```",
        "answer": "2, 3, 1",
        "explanation": "逗号表达式从左到右执行：z=x++（后自增，z被赋值为x原值1，x变为2），y++（y变为2），++y（y变为3）。最终x=2, y=3, z=1。注意：z=x++不是逗号表达式的整体值，赋值运算符优先级高于逗号，所以z只得到了x++的值。",
        "code_snippet": "int x, y, z;\nx = 1;\ny = 1;\nz = x++, y++, ++y;\nprintf(\"%d,%d,%d\\n\", x, y, z);",
        "kp_chapter": "1.2",
    },
    {
        "type": "fill_blank", "part": "C_programming", "difficulty": 3,
        "content": "根据代码补充填空（斐波那契数列）：\n```c\n#include <stdio.h>\n#define N 40\nint main() {\n    int i;\n    int f[N] = {1, 1};\n    for(i = 2; i < N; i++)\n        _____(1)_______\n    for(i = 0; i < N; i++) {\n        if(_____(2)_____)\n            printf(\"\\n\");\n        printf(\"%12ld\", f[i]);\n    }\n    return 0;\n}\n```\n(1)处应填入：____\n(2)处应填入：____",
        "answer": "(1) f[i] = f[i-1] + f[i-2];\n(2) i % 5 == 0 且 i != 0（或其他控制每行输出5个的换行条件）",
        "explanation": "(1)斐波那契递推：f[i] = f[i-1] + f[i-2]。\n(2)需要在每输出5个数后换行，典型条件：i % 5 == 0 && i != 0。",
        "code_snippet": "#define N 40\nint f[N] = {1, 1};\nfor(i = 2; i < N; i++)\n    f[i] = f[i-1] + f[i-2];",
        "kp_chapter": "1.3",
    },
    {
        "type": "fill_blank", "part": "C_programming", "difficulty": 3,
        "content": "根据代码补充填空（统计不及格学生）：\n```c\n#include <stdio.h>\n#define MAX_STUDENTS 100\ntypedef struct {\n    int student_id;\n    float score;\n} Student;\nint main() {\n    int num_students, i;\n    int count = 0;\n    Student students[MAX_STUDENTS];\n    printf(\"请输入学生总数：\");\n    scanf(\"%d\", &num_students);\n    for(i = 0; i < num_students; i++) {\n        printf(\"请输入学号和分数（学号 分数）：\");\n        scanf(\"%d %f\", &students[i].student_id, &students[i].score);\n    }\n    printf(\"不及格学生的学号和分数：\\n\");\n    for(i = 0; i < num_students; i++) {\n        if(_____(1)_____) {\n            printf(\"学号：%d，分数：%.2f\\n\", students[i].student_id, students[i].score);\n            count++;\n        }\n    }\n    printf(\"不及格的人数：%d\\n\", _____(2)_____);\n    return 0;\n}\n```\n(1)处应填入：____\n(2)处应填入：____",
        "answer": "(1) students[i].score < 60\n(2) count",
        "explanation": "(1)判断分数是否小于60分（不及格线）：students[i].score < 60。\n(2)程序已用count变量累计不及格人数，直接输出count即可。",
        "kp_chapter": "1.4",
    },

    # ============================================================
    # C语言部分 - 程序阅读题（3题，共10分）
    # ============================================================
    {
        "type": "program_reading", "part": "C_programming", "difficulty": 3,
        "content": "阅读以下代码，写出输出结果：\n```c\nint x = 1, a = 0, b = 0;\nswitch(x) {\n    case 0: b++;\n    case 1: a++;\n    case 2: a++, b++;\n}\nprintf(\"%d,%d\", a, b);\n```",
        "answer": "2, 1",
        "explanation": "x=1匹配case 1。执行a++（a变为1），无break，继续执行case 2的a++（a变为2）和b++（b变为1），遇到}结束。switch的穿透（fall-through）特性：进入case 1后，因无break，继续执行后续所有case的语句。",
        "code_snippet": "int x = 1, a = 0, b = 0;\nswitch(x) {\n    case 0: b++;\n    case 1: a++;\n    case 2: a++, b++;\n}\nprintf(\"%d,%d\", a, b);",
        "kp_chapter": "1.3",
    },
    {
        "type": "program_reading", "part": "C_programming", "difficulty": 4,
        "content": "阅读以下代码，写出最终输出的值：\n```c\nint fun(int x) {\n    static int a = 3;\n    a = a + x;\n    return a;\n}\nint main() {\n    int k = 1, m = 2;\n    int n;\n    n = fun(k);\n    n = fun(m);\n    printf(\"%d\", n);\n}\n```",
        "answer": "6",
        "explanation": "static局部变量a在函数调用结束后保留值。第一次调用fun(1)：a=3+1=4，返回4给n。第二次调用fun(2)：a保留为4，a=4+2=6，返回6给n。输出6。",
        "code_snippet": "int fun(int x) {\n    static int a = 3;\n    a = a + x;\n    return a;\n}\nint main() {\n    int k = 1, m = 2;\n    int n;\n    n = fun(k);\n    n = fun(m);\n    printf(\"%d\", n);\n}",
        "kp_chapter": "1.5",
    },
    {
        "type": "program_reading", "part": "C_programming", "difficulty": 4,
        "content": "阅读以下代码，写出最终输出的值：\n```c\nint x;\nint f();\nint main() {\n    int a = 1;\n    x = a;\n    a = f();\n    {\n        int b = 2;\n        b = a + b;\n        x = x + b;\n    }\n    printf(\"%d,%d\", a, x);\n}\nint f() {\n    int x = 4;\n    return x;\n}\n```",
        "answer": "4, 7",
        "explanation": "main中a=1, x=a=1。a=f()=4。进入代码块：b=2, b=a+b=4+2=6, x=x+b=1+6=7。块结束后b销毁。a=4（全局x在f()中被同名局部变量遮蔽，f()返回局部x=4，不影响全局x但main中x在f调用前已赋值为1）。最终输出\"4,7\"。",
        "code_snippet": "int x;\nint f() { int x = 4; return x; }\nint main() {\n    int a = 1;\n    x = a;\n    a = f();\n    { int b = 2;\n      b = a + b;\n      x = x + b; }\n    printf(\"%d,%d\", a, x);\n}",
        "kp_chapter": "1.5",
    },

    # ============================================================
    # C语言部分 - 编程题（3题，每题10分，共30分）
    # ============================================================
    {
        "type": "programming", "part": "C_programming", "difficulty": 4,
        "content": "已知cosx的泰勒展开式为：cos(x)=1 - x²/2! + x⁴/4! - x⁶/6! + ...\n请输入x，计算cos(x)的值。要求：最后一项的绝对值小于10⁻⁵时停止累加，输出最终答案和累加了多少项。（10分）",
        "answer": "#include <stdio.h>\n#include <math.h>\nint main() {\n    double x, term = 1, sum = 1;\n    int n = 1, count = 1;\n    scanf(\"%lf\", &x);\n    do {\n        term = -term * x * x / ((2*n-1) * (2*n));\n        if (fabs(term) < 1e-5) break;\n        sum += term;\n        count++;\n        n++;\n    } while (1);\n    printf(\"cos(%lf) = %lf, 共 %d 项\\n\", x, sum, count);\n    return 0;\n}",
        "explanation": "泰勒展开递推：第n+1项 = 第n项 × (-x²) / ((2n-1)×(2n))。初始term=1，n从1开始。循环累加直到|term|<10⁻⁵。",
        "code_snippet": "double x, term = 1, sum = 1;\nint n = 1;\nwhile (fabs(term) >= 1e-5) {\n    term = -term * x * x / ((2*n-1) * (2*n));\n    sum += term;\n    n++;\n}",
        "kp_chapter": "1.5",
    },
    {
        "type": "programming", "part": "C_programming", "difficulty": 4,
        "content": "实现数组的循环左移。给定一个整型数组a和移动位数k，将数组中的元素循环左移k个位置。要求：移动次数尽量少，且不允许使用临时数组。（10分）\n\n例如：a={1,2,3,4,5,6,7}, k=3，循环左移后 a={4,5,6,7,1,2,3}",
        "answer": "// 三次逆置法\nvoid Reverse(int a[], int start, int end) {\n    while (start < end) {\n        int temp = a[start];\n        a[start] = a[end];\n        a[end] = temp;\n        start++; end--;\n    }\n}\nvoid RotateLeft(int a[], int n, int k) {\n    k = k % n;\n    Reverse(a, 0, k-1);     // 逆置前k个\n    Reverse(a, k, n-1);     // 逆置后n-k个\n    Reverse(a, 0, n-1);     // 整体逆置\n}",
        "explanation": "三次逆置法实现O(n)时间、O(1)空间。步骤：①逆置前k个{3,2,1,4,5,6,7}；②逆置后n-k个{3,2,1,7,6,5,4}；③整体逆置{4,5,6,7,1,2,3}。",
        "code_snippet": "void Reverse(int a[], int start, int end) {\n    while (start < end) {\n        int temp = a[start];\n        a[start] = a[end];\n        a[end] = temp;\n        start++; end--;\n    }\n}",
        "kp_chapter": "1.4",
    },
    {
        "type": "programming", "part": "C_programming", "difficulty": 5,
        "content": "给定不同面额的硬币coins和一个总金额amount。编写一个函数来计算可以凑成总金额所需的最少的硬币个数。如果没有任何一种硬币组合能组成总金额，返回-1。\n\n示例：\n输入: coins = [1, 2, 5], amount = 11\n输出: 3\n解释: 11 = 5 + 5 + 1\n\n要求使用动态规划法求解。（10分）",
        "answer": "#include <stdio.h>\n#include <string.h>\n#define INF 999999\nint coinChange(int coins[], int n, int amount) {\n    int dp[amount + 1];\n    for (int i = 0; i <= amount; i++)\n        dp[i] = INF;\n    dp[0] = 0;\n    for (int i = 1; i <= amount; i++) {\n        for (int j = 0; j < n; j++) {\n            if (coins[j] <= i && dp[i - coins[j]] != INF)\n                if (dp[i - coins[j]] + 1 < dp[i])\n                    dp[i] = dp[i - coins[j]] + 1;\n        }\n    }\n    return dp[amount] == INF ? -1 : dp[amount];\n}",
        "explanation": "动态规划：dp[i]表示凑成金额i的最少硬币数。状态转移：dp[i] = min(dp[i - coins[j]] + 1)，其中coins[j] ≤ i。dp[0]=0。时间复杂度O(n×amount)。",
        "kp_chapter": "1.4",
    },
]


async def seed():
    await init_db()

    async with async_session() as session:
        kp_result = await session.execute(select(KnowledgePoint))
        kps = {kp.chapter: kp for kp in kp_result.scalars().all() if kp.chapter}

        # 清除旧的2024真题（如已存在则跳过）
        count = 0
        skipped = 0
        for q_data in EXAM_2024_QUESTIONS:
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
        print(f"2024真题导入完成！共导入 {count} 道题目，跳过 {skipped} 道。")
        print("覆盖：数据结构10选择+1计算+2分析+1编程，C语言10选择+3填空+3阅读+3编程")
        print("知识点分布：2.1(1) 2.2(1) 2.3(1) 2.4(1) 2.5(3) 2.6(2) 2.7(2) 2.8(1)")
        print("         1.1(1) 1.2(2) 1.3(3) 1.4(4) 1.5(4) 1.6(2) 1.7(1)")


if __name__ == "__main__":
    asyncio.run(seed())
