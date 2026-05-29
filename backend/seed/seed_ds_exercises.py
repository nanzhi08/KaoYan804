"""数据结构章节习题 - 从Markdown笔记提取的章末练习题"""
import asyncio
import sys
sys.path.insert(0, ".")

from sqlalchemy import select
from app.database import async_session, init_db
from app.models.knowledge_point import KnowledgePoint
from app.models.question import Question, QuestionKnowledgePoint

DS_EXERCISES = [
    # ============================================================
    # 第一章 绪论 - 6道选择
    # ============================================================
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 1,
        "content": "在数据结构中，从逻辑上可以把数据结构分成（ ）。",
        "options": {"A": "动态结构和静态结构", "B": "紧凑结构和非紧凑结构", "C": "线性结构和非线性结构", "D": "内部结构和外部结构"},
        "answer": "C",
        "explanation": "数据结构按逻辑结构分为线性结构（线性表、栈、队列、串）和非线性结构（树、图、集合）。存储结构分为顺序存储和链式存储。",
        "kp_chapter": "2.1",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 1,
        "content": "与数据元素本身的形式、内容、相对位置、个数无关的是数据的（ ）。",
        "options": {"A": "存储结构", "B": "存储实现", "C": "逻辑结构", "D": "运算实现"},
        "answer": "C",
        "explanation": "逻辑结构描述数据元素之间的逻辑关系，与数据的具体内容、存储方式无关，是独立于计算机的。存储结构则依赖于计算机。",
        "kp_chapter": "2.1",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 1,
        "content": "通常要求同一逻辑结构中的所有数据元素具有相同的特性，这意味着（ ）。",
        "options": {
            "A": "数据具有同一特点",
            "B": "不仅数据元素所包含的数据项的个数要相同，而且对应数据项的类型要一致",
            "C": "每个数据元素都一样",
            "D": "数据元素所包含的数据项的个数要相等"
        },
        "answer": "B",
        "explanation": "同一逻辑结构要求数据元素具有相同的数据项个数和类型，这是数据结构中\"相同特性\"的含义。",
        "kp_chapter": "2.1",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 1,
        "content": "以下说法正确的是（ ）。",
        "options": {
            "A": "数据元素是数据的最小单位",
            "B": "数据项是数据的基本单位",
            "C": "数据结构是带有结构的各数据项的集合",
            "D": "一些表面上很不相同的数据可以有相同的逻辑结构"
        },
        "answer": "D",
        "explanation": "数据元素是数据的基本单位，数据项是数据的最小单位，数据结构是带有结构的数据元素的集合。不同类型的数据（如学生表和课程表）可以有相同的逻辑结构（如线性结构）。",
        "kp_chapter": "2.1",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 2,
        "content": "算法的时间复杂度取决于（ ）。",
        "options": {
            "A": "问题的规模",
            "B": "待处理数据的初态",
            "C": "计算机的配置",
            "D": "A和B"
        },
        "answer": "D",
        "explanation": "算法的时间复杂度不仅与问题规模有关，还与待处理数据的初始状态有关。如排序算法在数据有序和无序时表现不同，因此有最好、最坏和平均时间复杂度之分。",
        "kp_chapter": "2.1",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 1,
        "content": "以下数据结构中，（ ）是非线性数据结构。",
        "options": {"A": "树", "B": "字符串", "C": "队列", "D": "栈"},
        "answer": "A",
        "explanation": "树是一对多的层次结构，属于非线性结构。字符串、队列、栈都是一对一的线性结构。",
        "kp_chapter": "2.1",
    },

    # ============================================================
    # 第二章 线性表 - 15道选择（选最有代表性的）
    # ============================================================
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 2,
        "content": "顺序表中第一个元素的存储地址是100，每个元素的长度为2，则第5个元素的地址是（ ）。",
        "options": {"A": "110", "B": "108", "C": "100", "D": "120"},
        "answer": "B",
        "explanation": "顺序表连续存储，LOC(ai)=LOC(a1)+(i-1)×L。第5个元素地址=100+4×2=108。",
        "kp_chapter": "2.2",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 2,
        "content": "在n个结点的顺序表中，算法的时间复杂度是O(1)的操作是（ ）。",
        "options": {
            "A": "访问第i个结点（1≤i≤n）和求第i个结点的直接前驱（2≤i≤n）",
            "B": "在第i个结点后插入一个新结点（1≤i≤n）",
            "C": "删除第i个结点（1≤i≤n）",
            "D": "将n个结点从小到大排序"
        },
        "answer": "A",
        "explanation": "顺序表支持随机存取，访问第i个结点直接通过下标O(1)。插入和删除需移动元素O(n)，排序至少O(n²)或O(n log n)。",
        "kp_chapter": "2.2",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 2,
        "content": "向一个有127个元素的顺序表中插入一个新元素并保持原来顺序不变，平均要移动的元素个数为（ ）。",
        "options": {"A": "8", "B": "63.5", "C": "63", "D": "7"},
        "answer": "B",
        "explanation": "顺序表插入有n+1个可能位置，平均移动元素数为n/2。127/2=63.5。",
        "kp_chapter": "2.2",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 2,
        "content": "线性表若采用链式存储结构时，要求内存中可用存储单元的地址（ ）。",
        "options": {"A": "必须是连续的", "B": "部分地址必须是连续的", "C": "一定是不连续的", "D": "连续或不连续都可以"},
        "answer": "D",
        "explanation": "链式存储通过指针链接各结点，存储单元可以是任意位置，连续或不连续都不影响逻辑关系。",
        "kp_chapter": "2.2",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 2,
        "content": "线性表L在（ ）情况下适用于使用链式结构实现。",
        "options": {"A": "需经常修改L中的结点值", "B": "需不断对L进行删除插入", "C": "L中含有大量的结点", "D": "L中结点结构复杂"},
        "answer": "B",
        "explanation": "链表最大的优势在于插入和删除时不需要移动数据，只需修改指针即可，适合频繁增删的场景。",
        "kp_chapter": "2.2",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 2,
        "content": "单链表的存储密度（ ）。",
        "options": {"A": "大于1", "B": "等于1", "C": "小于1", "D": "不能确定"},
        "answer": "C",
        "explanation": "存储密度=数据本身所占空间/结点总空间=D/(D+N)（N为指针域大小）。因为N>0，所以存储密度<1。顺序表的存储密度为1。",
        "kp_chapter": "2.2",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 2,
        "content": "在单链表中，要将s所指结点插入到p所指结点之后，其语句应为（ ）。",
        "options": {
            "A": "s->next=p+1; p->next=s;",
            "B": "(*p).next=s; (*s).next=(*p).next;",
            "C": "s->next=p->next; p->next=s->next;",
            "D": "s->next=p->next; p->next=s;"
        },
        "answer": "D",
        "explanation": "在p之后插入s：先让s指向p的后继(s->next=p->next)，再让p指向s(p->next=s)。注意顺序不能颠倒，否则会丢失原p的后继结点。",
        "kp_chapter": "2.2",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 3,
        "content": "在双向循环链表中，在p指针所指的结点后插入q所指向的新结点，其修改指针的操作是（ ）。",
        "options": {
            "A": "p->next=q; q->prior=p; p->next->prior=q; q->next=q;",
            "B": "p->next=q; p->next->prior=q; q->prior=p; q->next=p->next;",
            "C": "q->prior=p; q->next=p->next; p->next->prior=q; p->next=q;",
            "D": "q->prior=p; q->next=p->next; p->next=q; p->next->prior=q;"
        },
        "answer": "C",
        "explanation": "双向链表插入需修改4个指针。正确顺序：①q->prior=p ②q->next=p->next ③p->next->prior=q ④p->next=q。选项C的顺序保证了不丢失原后继结点的引用。",
        "kp_chapter": "2.2",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 2,
        "content": "创建一个包括n个结点的有序单链表的时间复杂度是（ ）。",
        "options": {"A": "O(1)", "B": "O(n)", "C": "O(n²)", "D": "O(n log n)"},
        "answer": "C",
        "explanation": "创建有序单链表时，每插入一个新结点需要找到合适的插入位置（与已有有序结点比较），类似于插入排序，时间复杂度为O(n²)。",
        "kp_chapter": "2.2",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 2,
        "content": "在双向链表存储结构中，删除p所指的结点时须修改指针（ ）。",
        "options": {
            "A": "p->next->prior=p->prior; p->prior->next=p->next;",
            "B": "p->next=p->next->next; p->next->prior=p;",
            "C": "p->prior->next=p; p->prior=p->prior->prior;",
            "D": "p->prior=p->next->next; p->next=p->prior->prior;"
        },
        "answer": "A",
        "explanation": "删除p结点需要：①让p的后继的前驱指向p的前驱（p->next->prior=p->prior）；②让p的前驱的后继指向p的后继（p->prior->next=p->next）。",
        "kp_chapter": "2.2",
    },

    # ============================================================
    # 第三章 栈和队列 - 15道选择（选最有代表性的）
    # ============================================================
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 2,
        "content": "若让元素1，2，3，4，5依次进栈，则出栈次序不可能出现在（ ）种情况。",
        "options": {"A": "5，4，3，2，1", "B": "2，1，5，4，3", "C": "4，3，1，2，5", "D": "2，3，5，4，1"},
        "answer": "C",
        "explanation": "栈是后进先出。C选项4,3先出（说明1,2仍在栈中），然后1先于2出栈，违背了栈的后进先出原则（2在1之后入栈，应在1之前出栈）。因此'4,3,1,2,5'不可能。",
        "kp_chapter": "2.3",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 3,
        "content": "若已知一个栈的入栈序列是1，2，3，…，n，其输出序列为p1，p2，p3，…，pn，若p1=n，则pi为（ ）。",
        "options": {"A": "i", "B": "n-i", "C": "n-i+1", "D": "不确定"},
        "answer": "C",
        "explanation": "p1=n说明所有元素一次性全部入栈后再依次出栈。出栈顺序为n, n-1, ..., 1。所以pi=n-i+1。",
        "kp_chapter": "2.3",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 3,
        "content": "数组Q[n]用来表示一个循环队列，f为当前队列头元素的前一位置，r为队尾元素的位置，假定队列中元素的个数小于n，计算队列中元素个数的公式为（ ）。",
        "options": {"A": "r-f", "B": "(n+f-r)%n", "C": "n+r-f", "D": "(n+r-f)%n"},
        "answer": "D",
        "explanation": "循环队列元素个数=(rear-front+MAXSIZE)%MAXSIZE。本题MAXSIZE=n，f为front，r为rear，故(n+r-f)%n。",
        "kp_chapter": "2.3",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 2,
        "content": "链式栈结点为：(data,link)，top指向栈顶。若想摘除栈顶结点，并将删除结点的值保存到x中，则应执行操作（ ）。",
        "options": {
            "A": "x=top->data; top=top->link;",
            "B": "top=top->link; x=top->link;",
            "C": "x=top; top=top->link;",
            "D": "x=top->link;"
        },
        "answer": "A",
        "explanation": "出栈操作：先取出栈顶数据x=top->data，然后将栈顶指针下移top=top->link（指向下一个结点）。",
        "kp_chapter": "2.3",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 2,
        "content": "栈在（ ）中有所应用。",
        "options": {"A": "递归调用", "B": "函数调用", "C": "表达式求值", "D": "前三个选项都有"},
        "answer": "D",
        "explanation": "递归调用使用系统栈保存调用信息；函数调用通过栈传递参数和返回地址；表达式求值（如中缀转后缀）用栈保存运算符。三者都用到了栈的后进先出性质。",
        "kp_chapter": "2.3",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 2,
        "content": "为解决计算机主机与打印机间速度不匹配问题，通常设一个打印数据缓冲区。主机将要输出的数据依次写入该缓冲区，而打印机则依次从该缓冲区中取出数据。该缓冲区的逻辑结构应该是（ ）。",
        "options": {"A": "队列", "B": "栈", "C": "线性表", "D": "有序表"},
        "answer": "A",
        "explanation": "打印机按先来先服务的顺序处理数据（FIFO），缓冲区应使用队列结构。队列是一种先进先出的线性表。",
        "kp_chapter": "2.3",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 4,
        "content": "设栈S和队列Q的初始状态为空，元素e1、e2、e3、e4、e5和e6依次进入栈S，一个元素出栈后即进入Q，若6个元素出队的序列是e2、e4、e3、e6、e5和e1，则栈S的容量至少应该是（ ）。",
        "options": {"A": "2", "B": "3", "C": "4", "D": "6"},
        "answer": "B",
        "explanation": "出队序列即出栈序列（因为出栈后立即入队）。出栈序列为e2,e4,e3,e6,e5,e1。分析：e1入,e2入,e2出(1个在栈)；e3入,e4入,e4出,e3出(最多2个在栈)；e5入,e6入,e6出,e5出,e1出。栈中同时最多3个元素(e1,e3,e4或e1,e5,e6)，容量至少为3。",
        "kp_chapter": "2.3",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 3,
        "content": "若一个栈以向量V[1..n]存储，初始栈顶指针top设为n+1，则元素x进栈的正确操作是（ ）。",
        "options": {
            "A": "top++; V[top]=x;",
            "B": "V[top]=x; top++;",
            "C": "top--; V[top]=x;",
            "D": "V[top]=x; top--;"
        },
        "answer": "C",
        "explanation": "初始top=n+1说明栈从高端向低端增长。进栈时指针先减1移至空位top--，再存储元素V[top]=x。这是向下增长的顺序栈。",
        "kp_chapter": "2.3",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 2,
        "content": "设计一个判别表达式中左、右括号是否配对出现的算法，采用（ ）数据结构最佳。",
        "options": {"A": "线性表的顺序存储结构", "B": "队列", "C": "线性表的链式存储结构", "D": "栈"},
        "answer": "D",
        "explanation": "括号匹配利用栈的后进先出特性：遇到左括号入栈，遇到右括号与栈顶匹配则出栈。最终栈空则匹配成功。",
        "kp_chapter": "2.3",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 3,
        "content": "循环队列存储在数组A[0..m]中，则入队时的操作为（ ）。",
        "options": {"A": "rear=rear+1", "B": "rear=(rear+1)%(m-1)", "C": "rear=(rear+1)%m", "D": "rear=(rear+1)%(m+1)"},
        "answer": "D",
        "explanation": "数组A[0..m]共有m+1个元素，取模时应除以m+1。入队操作：rear=(rear+1)%(m+1)。",
        "kp_chapter": "2.3",
    },

    # ============================================================
    # 第四章 串、数组和广义表 - 15道选代表性题目
    # ============================================================
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 1,
        "content": "串是一种特殊的线性表，其特殊性体现在（ ）。",
        "options": {"A": "可以顺序存储", "B": "数据元素是一个字符", "C": "可以链式存储", "D": "数据元素可以是多个字符"},
        "answer": "B",
        "explanation": "串是内容受限的线性表，限定了表中的每个元素只能是单个字符。这是串区别于其他线性表的核心特征。",
        "kp_chapter": "2.4",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 1,
        "content": "下面关于串的叙述中，（ ）是不正确的？",
        "options": {
            "A": "串是字符的有限序列",
            "B": "空串是由空格构成的串",
            "C": "模式匹配是串的一种重要运算",
            "D": "串既可以采用顺序存储，也可以采用链式存储"
        },
        "answer": "B",
        "explanation": "空串是长度为0的串（零个字符），空格串是由空格字符组成的串（长度>0）。两者不同！B选项将空串与空格串混淆，是不正确的。",
        "kp_chapter": "2.4",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 1,
        "content": "串的长度是指（ ）。",
        "options": {
            "A": "串中所含不同字母的个数",
            "B": "串中所含字符的个数",
            "C": "串中所含不同字符的个数",
            "D": "串中所含非空格字符的个数"
        },
        "answer": "B",
        "explanation": "串的长度是指串中字符的数目（包括空格字符）。空串长度为0，空格串长度为其空格个数。",
        "kp_chapter": "2.4",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 3,
        "content": "假设以行序为主序存储二维数组A=array[1..100,1..100]，设每个数据元素占2个存储单元，基地址为10，则LOC[5,5]=（ ）。",
        "options": {"A": "808", "B": "818", "C": "1010", "D": "1020"},
        "answer": "B",
        "explanation": "行序为主：LOC[i,j]=基地址+[(i-1)×列数+(j-1)]×L。LOC[5,5]=10+[(5-1)×100+(5-1)]×2=10+[400+4]×2=818。",
        "kp_chapter": "2.4",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 3,
        "content": "设有一个10阶的对称矩阵A，采用压缩存储方式，以行序为主存储，a11为第一元素，其存储地址为1，每个元素占一个地址空间，则a85的地址为（ ）。",
        "options": {"A": "13", "B": "32", "C": "33", "D": "40"},
        "answer": "C",
        "explanation": "对称矩阵压缩存储下三角（含对角线）。a85中8≥5，存于下三角。地址=1+[i(i-1)/2+j-1]=1+[8×7/2+5-1]=1+[28+4]=33。",
        "kp_chapter": "2.4",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 3,
        "content": "设二维数组A[1..m, 1..n]按行存储在数组B[1..m*n]中，则二维数组元素A[i,j]在一维数组B中的下标为（ ）。",
        "options": {"A": "(i-1)*n+j", "B": "(i-1)*n+j-1", "C": "i*(j-1)", "D": "j*m+i-1"},
        "answer": "A",
        "explanation": "A[1,1]对应B[1]。按行存储：位置=(i-1)×列数+j=(i-1)×n+j。取i=1,j=1代入得1，仅A正确。",
        "kp_chapter": "2.4",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 2,
        "content": "广义表A=(a,b,(c,d),(e,(f,g)))，则Head(Tail(Head(Tail(Tail(A)))))的值为（ ）。",
        "options": {"A": "(g)", "B": "(d)", "C": "c", "D": "d"},
        "answer": "D",
        "explanation": "Tail(A)=(b,(c,d),(e,(f,g)))；Tail(Tail(A))=((c,d),(e,(f,g)))；Head(Tail(Tail(A)))=(c,d)；Tail(Head(Tail(Tail(A))))=(d)；Head(Tail(Head(Tail(Tail(A)))))=d。",
        "kp_chapter": "2.4",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 2,
        "content": "广义表((a,b,c,d))的表头是（ ），表尾是（ ）。",
        "options": {"A": "a", "B": "( )", "C": "(a,b,c,d)", "D": "(b,c,d)"},
        "answer": "C、B",
        "explanation": "表头：非空广义表的第一个元素（去掉该元素最外层括号）。((a,b,c,d))中只有一个子表(a,b,c,d)，表头=(a,b,c,d)。表尾：除去表头后由其余元素构成的表（保留最外层括号）。这里只有表头，剩余元素为空，表尾=( )。",
        "kp_chapter": "2.4",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 2,
        "content": "设广义表L=((a,b,c))，则L的长度和深度分别为（ ）。",
        "options": {"A": "1和1", "B": "1和3", "C": "1和2", "D": "2和3"},
        "answer": "C",
        "explanation": "长度=最大括号中逗号数+1。((a,b,c))中只有1个元素，长度=1。深度=括号嵌套的最大层数。((a,b,c))有2层括号，深度=2。",
        "kp_chapter": "2.4",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 3,
        "content": "若对n阶对称矩阵A以行序为主序方式将其下三角形的元素(包括主对角线上所有元素)依次存放于一维数组B[1..n(n+1)/2]中，则在B中确定aij（i<j）的位置k的关系为（ ）。",
        "options": {"A": "i(i-1)/2+j", "B": "j(j-1)/2+i", "C": "i(i+1)/2+j", "D": "j(j+1)/2+i"},
        "answer": "B",
        "explanation": "当i<j时，aij在上三角。由于是对称矩阵，aij=aji，而aji在下三角，按行序存储时位置为j(j-1)/2+i。",
        "kp_chapter": "2.4",
    },

    # ============================================================
    # 第五章 树和二叉树 - 15道代表性题目
    # ============================================================
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 2,
        "content": "由3个结点可以构造出多少种不同的二叉树？（ ）",
        "options": {"A": "2", "B": "3", "C": "4", "D": "5"},
        "answer": "D",
        "explanation": "3个结点的二叉树有5种形态：全左斜、全右斜、根-左(根-左)、根-左(根-右)、根-左右。Catalan数：n个结点不同二叉树个数=C(2n,n)/(n+1)，n=3时=5。",
        "kp_chapter": "2.5",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 3,
        "content": "一棵完全二叉树上有1001个结点，其中叶子结点的个数是（ ）。",
        "options": {"A": "250", "B": "500", "C": "254", "D": "501"},
        "answer": "D",
        "explanation": "n0=n2+1, n=n0+n1+n2, n=2n0+n1-1=1001, 2n0+n1=1002。完全二叉树中n1=0或1。若n1=1, n0=500.5(舍)；若n1=0, n0=501（让2n0=1001不行）。正确：n1=1, n0=(1002-1)/2=500.5舍；n1=0, n0=501。\n\n验算：n0=n2+1, n=1001=n0+n2+0=2n0-1, n0=501。",
        "kp_chapter": "2.5",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 2,
        "content": "一个具有1025个结点的二叉树的高h为（ ）。",
        "options": {"A": "11", "B": "10", "C": "11至1025之间", "D": "10至1024之间"},
        "answer": "C",
        "explanation": "二叉树最小高度：完全二叉树⌊log₂1025⌋+1=10+1=11。最大高度：每层1个结点，共1025层。所以h在11至1025之间。",
        "kp_chapter": "2.5",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 3,
        "content": "一棵非空的二叉树的先序遍历序列与后序遍历序列正好相反，则该二叉树一定满足（ ）。",
        "options": {
            "A": "所有的结点均无左孩子",
            "B": "所有的结点均无右孩子",
            "C": "只有一个叶子结点",
            "D": "是任意一棵二叉树"
        },
        "answer": "C",
        "explanation": "先序=中左右，后序=左右中。两者正相反时：无左子树的先序=中右，后序=右中（相反）；无右子树的先序=中左，后序=左中（相反）。两者情况都是只有一个叶子结点（退化为单支树）。",
        "kp_chapter": "2.5",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 2,
        "content": "设哈夫曼树中有199个结点，则该哈夫曼树中有（ ）个叶子结点。",
        "options": {"A": "99", "B": "100", "C": "101", "D": "102"},
        "answer": "B",
        "explanation": "哈夫曼树只有度为0和度为2的结点。n=n0+n2=n0+(n0-1)=2n0-1。199=2n0-1，n0=100。",
        "kp_chapter": "2.5",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 3,
        "content": "若X是二叉中序线索树中一个有左孩子的结点，且X不为根，则X的前驱为（ ）。",
        "options": {
            "A": "X的双亲",
            "B": "X的右子树中最左的结点",
            "C": "X的左子树中最右结点",
            "D": "X的左子树中最右叶结点"
        },
        "answer": "C",
        "explanation": "中序线索树中，结点X的前驱是其左子树中最右下的结点（即左子树中序遍历的最后一个结点）。这与中序遍历规则一致。",
        "kp_chapter": "2.5",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 2,
        "content": "引入二叉线索树的目的是（ ）。",
        "options": {
            "A": "加快查找结点的前驱或后继的速度",
            "B": "为了能在二叉树中方便的进行插入与删除",
            "C": "为了能方便的找到双亲",
            "D": "使二叉树的遍历结果唯一"
        },
        "answer": "A",
        "explanation": "线索二叉树利用n+1个空链域存储前驱/后继指针，目的是加速查找某遍历序列中结点的前驱和后继。",
        "kp_chapter": "2.5",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 3,
        "content": "设F是一个森林，B是由F变换得的二叉树。若F中有n个非终端结点，则B中右指针域为空的结点有（ ）个。",
        "options": {"A": "n-1", "B": "n", "C": "n+1", "D": "n+2"},
        "answer": "C",
        "explanation": "森林转二叉树后，右指针代表兄弟关系。每棵树最后（最右）的结点右指针为空。n个非终端结点意味着有n+1棵树（或可推导），故有n+1个右指针为空的结点。\n\n推导：F有m棵树的森林，B中右指针为空的结点=森林中每棵树的根（无右兄弟）+某些其他结点=n+1。",
        "kp_chapter": "2.5",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 2,
        "content": "n（n≥2）个权值均不相同的字符构成哈夫曼树，关于该树的叙述中，错误的是（ ）。",
        "options": {
            "A": "该树一定是一棵完全二叉树",
            "B": "树中一定没有度为1的结点",
            "C": "树中两个权值最小的结点一定是兄弟结点",
            "D": "树中任一非叶结点的权值一定不小于下一层任一结点的权值"
        },
        "answer": "A",
        "explanation": "哈夫曼树不一定是完全二叉树，它只是带权路径长度最短的二叉树。B、C、D都是哈夫曼树的正确性质：正则二叉树、权值最小结点必定是兄弟、结点权值从上到下非递减。",
        "kp_chapter": "2.5",
    },

    # ============================================================
    # 第六章 图 - 15道代表性题目
    # ============================================================
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 1,
        "content": "在一个图中，所有顶点的度数之和等于图的边数的（ ）倍。",
        "options": {"A": "1/2", "B": "1", "C": "2", "D": "4"},
        "answer": "C",
        "explanation": "握手定理：每条边连接两个顶点，为两个端点各贡献1度。所有顶点的度之和=2×边数。",
        "kp_chapter": "2.6",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 1,
        "content": "在一个有向图中，所有顶点的入度之和等于所有顶点的出度之和的（ ）倍。",
        "options": {"A": "1/2", "B": "1", "C": "2", "D": "4"},
        "answer": "B",
        "explanation": "有向图中，每条弧为一个顶点贡献1出度、为另一个顶点贡献1入度。所有顶点的入度之和=所有顶点的出度之和=弧的总数。",
        "kp_chapter": "2.6",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 2,
        "content": "具有n个顶点的有向图最多有（ ）条边。",
        "options": {"A": "n", "B": "n(n-1)", "C": "n(n+1)", "D": "n²"},
        "answer": "B",
        "explanation": "有向完全图：任意两个顶点间有方向相反的两条弧，n个顶点每个可指向其余n-1个顶点，共n(n-1)条。无向完全图有n(n-1)/2条边。",
        "kp_chapter": "2.6",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 3,
        "content": "n个顶点的连通图用邻接矩阵表示时，该矩阵至少有（ ）个非零元素。",
        "options": {"A": "n", "B": "2(n-1)", "C": "n/2", "D": "n²"},
        "answer": "B",
        "explanation": "连通n个顶点至少需要n-1条边。无向图的每条边在邻接矩阵中被存储两次（对称矩阵），所以非零元素至少为2(n-1)个。",
        "kp_chapter": "2.6",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 3,
        "content": "G是一个非连通无向图，共有28条边，则该图至少有（ ）个顶点。",
        "options": {"A": "7", "B": "8", "C": "9", "D": "10"},
        "answer": "C",
        "explanation": "8个顶点的无向完全图有8×7/2=28条边（连通图边数最大值）。再添加1个孤立顶点（第9个），总边数不变但图变为非连通。因此至少9个顶点。",
        "kp_chapter": "2.6",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 2,
        "content": "下面（ ）算法适合构造一个稠密图G的最小生成树。",
        "options": {"A": "Prim算法", "B": "Kruskal算法", "C": "Floyd算法", "D": "Dijkstra算法"},
        "answer": "A",
        "explanation": "Prim算法O(n²)与边数无关，适合稠密图。Kruskal算法O(e log e)与边数相关，适合稀疏图。Floyd和Dijkstra是求最短路径的算法。",
        "kp_chapter": "2.6",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 2,
        "content": "用邻接表表示图进行广度优先遍历时，通常借助（ ）来实现算法。",
        "options": {"A": "栈", "B": "队列", "C": "树", "D": "图"},
        "answer": "B",
        "explanation": "BFS按层依次访问，先访问的顶点的邻接点应优先被访问，使用队列(FIFO)实现。DFS使用栈（或递归）实现。",
        "kp_chapter": "2.6",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 2,
        "content": "深度优先遍历类似于二叉树的（ ）。",
        "options": {"A": "先序遍历", "B": "中序遍历", "C": "后序遍历", "D": "层次遍历"},
        "answer": "A",
        "explanation": "DFS先访问根（起始顶点），再深入各子树（邻接点），类似于二叉树的先序遍历（根→左→右）。BFS类似于层次遍历。",
        "kp_chapter": "2.6",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 2,
        "content": "下面（ ）方法可以判断出一个有向图是否有环。",
        "options": {"A": "深度优先遍历", "B": "拓扑排序", "C": "求最短路径", "D": "求关键路径"},
        "answer": "B",
        "explanation": "拓扑排序只能对有向无环图(DAG)进行。若进行拓扑排序后仍有顶点未被输出，则说明图中有环。DFS也可以检测环（通过判断回边），但拓扑排序是最直接的判断方法。",
        "kp_chapter": "2.6",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 2,
        "content": "图的BFS生成树的树高比DFS生成树的树高（ ）。",
        "options": {"A": "小", "B": "相等", "C": "小或相等", "D": "大或相等"},
        "answer": "C",
        "explanation": "BFS按层次扩展，生成树高度最小（最短路径树）。DFS可能沿一条路径深入很深。因此BFS树高≤DFS树高。",
        "kp_chapter": "2.6",
    },

    # ============================================================
    # 第七章 查找 - 15道代表性题目
    # ============================================================
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 1,
        "content": "对n个元素的表做顺序查找时，若查找每个元素的概率相同，则平均查找长度为（ ）。",
        "options": {"A": "(n-1)/2", "B": "n/2", "C": "(n+1)/2", "D": "n"},
        "answer": "C",
        "explanation": "ASL成功=(1+2+...+n)/n=n(n+1)/(2n)=(n+1)/2。",
        "kp_chapter": "2.7",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 1,
        "content": "适用于折半查找的表的存储方式及元素排列要求为（ ）。",
        "options": {
            "A": "链接方式存储，元素无序",
            "B": "链接方式存储，元素有序",
            "C": "顺序方式存储，元素无序",
            "D": "顺序方式存储，元素有序"
        },
        "answer": "D",
        "explanation": "折半查找要求：①顺序存储结构（支持随机存取），②表中元素按关键字有序排列。两个条件缺一不可。",
        "kp_chapter": "2.7",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 2,
        "content": "如果要求一个线性表既能较快的查找，又能适应动态变化的要求，最好采用( )查找法。",
        "options": {"A": "顺序查找", "B": "折半查找", "C": "分块查找", "D": "哈希查找"},
        "answer": "C",
        "explanation": "分块查找结合了顺序查找（块内无序，方便插入删除）和折半查找（索引有序，快速定位块）的优点，兼顾查找效率和动态变化。",
        "kp_chapter": "2.7",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 2,
        "content": "折半查找有序表（4，6，10，12，20，30，50，70，88，100）。若查找表中元素58，则它将依次与表中（ ）比较大小，查找结果是失败。",
        "options": {"A": "20，70，30，50", "B": "30，88，70，50", "C": "20，50", "D": "30，88，50"},
        "answer": "A",
        "explanation": "10个元素，mid依次为：(1+10)/2=5→20<58→low=6；(6+10)/2=8→70>58→high=7；(6+7)/2=6→30<58→low=7；(7+7)/2=7→50<58→low=8>high，失败。比较：20,70,30,50。",
        "kp_chapter": "2.7",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 2,
        "content": "对22个记录的有序表作折半查找，当查找失败时，至少需要比较（ ）次关键字。",
        "options": {"A": "3", "B": "4", "C": "5", "D": "6"},
        "answer": "B",
        "explanation": "22个记录，判定树深度⌊log₂22⌋+1=4+1=5。二叉树非满，失败时至少比较4次（到达第4层即判定失败），至多比较5次。",
        "kp_chapter": "2.7",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 2,
        "content": "设哈希表长为14，哈希函数是H(key)=key%11，表中已有数据的关键字为15，38，61，84共四个，现要将关键字为49的元素加到表中，用二次探测法解决冲突，则放入的位置是（ ）。",
        "options": {"A": "8", "B": "3", "C": "5", "D": "9"},
        "answer": "D",
        "explanation": "15→4, 38→5, 61→6, 84→7。49%11=5冲突。二次探测：d1=1²→(5+1)%14=6冲突；d2=-1²→(5-1+14)%14=4冲突；d3=2²→(5+4)%14=9不冲突。放位置9。",
        "kp_chapter": "2.7",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 2,
        "content": "下列关于m阶B-树的说法错误的是（ ）。",
        "options": {
            "A": "根结点至多有m棵子树",
            "B": "所有叶子都在同一层次上",
            "C": "非叶结点至少有⌈m/2⌉棵子树",
            "D": "根结点中的数据是有序的"
        },
        "answer": "C",
        "explanation": "B-树中，非叶结点（除根外）至少有⌈m/2⌉棵子树，而非至少m/2或m/2+1。根结点可以只有2棵子树。D选项中，B-树结点内关键字是有序的。",
        "kp_chapter": "2.7",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 2,
        "content": "下面关于哈希查找的说法，正确的是（ ）。",
        "options": {
            "A": "哈希函数构造的越复杂越好，因为这样随机性好，冲突小",
            "B": "除留余数法是所有哈希函数中最好的",
            "C": "不存在特别好与坏的哈希函数，要视情况而定",
            "D": "哈希表的平均查找长度有时也和记录总数有关"
        },
        "answer": "C",
        "explanation": "哈希函数的选择要根据实际情况（关键字分布、表长等），没有绝对的优劣。A错（复杂不一定好，计算开销大）；B错（没有绝对最好）；D错（ASL与负载因子α有关）。",
        "kp_chapter": "2.7",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 2,
        "content": "采用线性探测法处理冲突，可能要探测多个位置，在查找成功的情况下，所探测的这些位置上的关键字 ( )。",
        "options": {"A": "不一定都是同义词", "B": "一定都是同义词", "C": "一定都不是同义词", "D": "都相同"},
        "answer": "A",
        "explanation": "线性探测过程中，探测到的位置可能是在处理其他关键字冲突时被占用的，这些关键字不一定是同义词。例如key1先占了位置，key2(同义词)被挤到下一个位置。查找key2时会探测到key1的位置但key1不是同义词。",
        "kp_chapter": "2.7",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 2,
        "content": "折半搜索与二叉排序树的时间性能（ ）。",
        "options": {"A": "相同", "B": "完全不同", "C": "有时不相同", "D": "数量级都是O(log₂n)"},
        "answer": "C",
        "explanation": "折半查找始终O(log n)。二叉排序树的查找时间与树的形态有关，平衡时为O(log n)，退化为单支树时O(n)。所以二叉排序树的时间性能有时与折半查找不同（如最坏情况）。",
        "kp_chapter": "2.7",
    },

    # ============================================================
    # 第八章 内部排序 - 5道精选
    # ============================================================
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 2,
        "content": "下列排序算法中，（ ）排序在一趟结束后不一定能选出一个元素放在其最终位置上。",
        "options": {"A": "简单选择排序", "B": "冒泡排序", "C": "归并排序", "D": "堆排序"},
        "answer": "C",
        "explanation": "选择排序每趟确定最小元素放最前；冒泡排序每趟确定最大元素放最后；堆排序每趟确定堆顶元素位置。归并排序每趟只将相邻子序列合并，不保证任何元素到达最终位置。",
        "kp_chapter": "2.8",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 3,
        "content": "数据序列 {8, 9, 10, 4, 5, 6, 20, 1, 2} 只能是（ ）的两趟排序后的结果。",
        "options": {"A": "选择排序", "B": "冒泡排序", "C": "插入排序", "D": "堆排序"},
        "answer": "C",
        "explanation": "观察序列前三个(8,9,10)已有序，中间(4,5,6,20)部分有序，最后(1,2)未排序。这种特征符合插入排序两趟后的状态：已排序部分逐步扩大，但可能不是最小/最大元素在两端。",
        "kp_chapter": "2.8",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 3,
        "content": "设有5000个无序的元素，希望用最快的速度挑选出其中前10个最大的元素，最好选用（ ）排序方法。",
        "options": {"A": "冒泡排序", "B": "快速排序", "C": "堆排序", "D": "基数排序"},
        "answer": "C",
        "explanation": "堆排序适合求Top-K问题：建堆O(n)，然后做10次堆调整O(10 log n)，总O(n+10 log n)。冒泡需O(kn)；快速排序需全排序O(n log n)。所以堆排序最优。",
        "kp_chapter": "2.8",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 3,
        "content": "在文件局部有序或文件长度较小的情况下，最佳的排序方法是（ ）。",
        "options": {"A": "直接插入排序", "B": "冒泡排序", "C": "简单选择排序", "D": "快速排序"},
        "answer": "A",
        "explanation": "直接插入排序在初始基本有序时比较次数和移动次数都很少，最好情况为O(n)。且算法简单，对较小规模数据效率高。冒泡也能O(n)但比较次数仍多。",
        "kp_chapter": "2.8",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 2,
        "content": "从未排序序列中依次取出元素与已排序序列中的元素进行比较，然后将其放在已排序序列的合适位置，该排序方法称为（ ）排序法。",
        "options": {"A": "插入", "B": "选择", "C": "希尔", "D": "归并"},
        "answer": "A",
        "explanation": "插入排序的基本思想：将待排序元素逐个插入到已有序序列的合适位置。选择排序是每次选出最小元素放最前，归并是合并有序子序列。",
        "kp_chapter": "2.8",
    },
]

DS_CHAPTER_1_ANALYSIS = [
    {
        "type": "analysis", "part": "data_structure", "difficulty": 2,
        "content": "简述下列概念：数据、数据元素、数据项、数据对象、数据结构、逻辑结构、存储结构、抽象数据类型。",
        "answer": "数据：客观事物的符号表示，能输入到计算机中的符号的总称。\n数据元素：数据的基本单位，在计算机中通常作为一个整体处理。\n数据项：组成数据元素的、有独立含义的、不可分割的最小单位。\n数据对象：性质相同的数据元素的集合，是数据的一个子集。\n数据结构：相互之间存在一种或多种特定关系的数据元素的集合。\n逻辑结构：从逻辑关系上描述数据，与存储无关，独立于计算机。\n存储结构（物理结构）：数据在计算机中的存储表示。\n抽象数据类型(ADT)：由用户定义、表示应用问题的数学模型及定义在该模型上的一组操作。",
        "kp_chapter": "2.1",
    },
    {
        "type": "analysis", "part": "data_structure", "difficulty": 2,
        "content": "试举一个数据结构的例子，叙述其逻辑结构和存储结构两方面的含义和相互关系。",
        "answer": "例如学生基本信息表：每个学生记录是一个数据元素，含学号、姓名、性别等数据项。记录按顺序排列形成线性序列→逻辑结构为线性结构。\n存储实现：①用数组连续存放→顺序存储结构；②用链表随机存放并通过指针连接→链式存储结构。\n结论：同一逻辑结构可以对应多种不同的存储结构。",
        "kp_chapter": "2.1",
    },
    {
        "type": "analysis", "part": "data_structure", "difficulty": 2,
        "content": "试分析以下各程序段的时间复杂度。\n（1）循环 while(y>0){if(x>100){x=x-10;y--;}else x++;}\n（2）二重循环 for(i=0;i<n;i++) for(j=0;j<m;j++) a[i][j]=0;\n（3）i=1; while(i<=n) i=i*3;\n（4）for(i=1;i<n;i++) for(j=1;j<=n-i;j++) x++;",
        "answer": "（1）O(1)：循环至多执行有限次（常数阶），与n无关。\n（2）O(m×n)：执行m×n次。\n（3）O(log₃n)：i=1,3,9,27,...,3^k≤n，k=log₃n次。\n（4）O(n²)：x++执行总次数=(n-1)+(n-2)+...+1=n(n-1)/2，为n²级别。",
        "kp_chapter": "2.1",
    },
    {
        "type": "short_answer", "part": "data_structure", "difficulty": 2,
        "content": "简述逻辑结构的四种基本关系，并各举一例。",
        "answer": "（1）集合结构：元素仅属于同一集合。例：判断学生是否为某班成员。\n（2）线性结构：元素一对一关系。例：按学号顺序排列的学生名单。\n（3）树形结构：元素一对多关系。例：班级管理体系中班长管组长、组长管组员。\n（4）图结构（网状结构）：元素多对多关系。例：多位同学间任意交朋友的关系网。\n其中树结构和图结构属于非线性结构。",
        "kp_chapter": "2.1",
    },
]

DS_CHAPTER_3_EX = [
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 2,
        "content": "设有一个递归算法如下：\n```c\nint fact(int n) { // n≥0\n    if (n <= 0) return 1;\n    else return n * fact(n - 1);\n}\n```\n则计算fact(n)需要调用该函数的次数为（ ）。",
        "options": {"A": "n+1", "B": "n-1", "C": "n", "D": "n+2"},
        "answer": "A",
        "explanation": "fact(n)递归调用链：fact(n)→fact(n-1)→...→fact(0)，共n+1次调用。fact(0)直接返回不递归。特殊值法验证：n=0时调用1次，只有A选项n+1=1正确。",
        "code_snippet": "int fact(int n) {\n    if (n <= 0) return 1;\n    else return n * fact(n - 1);\n}",
        "kp_chapter": "2.3",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 3,
        "content": "最大容量为n的循环队列，队尾指针是rear，队头是front，则队空的条件是（ ）。",
        "options": {"A": "(rear+1)%n == front", "B": "rear == front", "C": "rear+1 == front", "D": "(rear-1)%n == front"},
        "answer": "B",
        "explanation": "最大容量n的循环队列，队空条件：rear==front。队满条件：(rear+1)%n==front（少用一个空间区分空和满）。",
        "kp_chapter": "2.3",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 1,
        "content": "栈和队列的共同点是（ ）。",
        "options": {"A": "都是先进先出", "B": "都是先进后出", "C": "只允许在端点处插入和删除元素", "D": "没有共同点"},
        "answer": "C",
        "explanation": "栈在栈顶一端操作，队列在队尾插入、队头删除，两者都只在端点处操作。两者的区别是操作规则：栈是LIFO，队列是FIFO。",
        "kp_chapter": "2.3",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 1,
        "content": "一个递归算法必须包括（ ）。",
        "options": {"A": "递归部分", "B": "终止条件和递归部分", "C": "迭代部分", "D": "终止条件和迭代部分"},
        "answer": "B",
        "explanation": "递归算法必须包含：①终止条件（基线条件）——防止无限递归；②递归部分——将问题分解为更小规模的同类问题。两者缺一不可。",
        "kp_chapter": "2.3",
    },
]


async def seed():
    await init_db()

    async with async_session() as session:
        kp_result = await session.execute(select(KnowledgePoint))
        kps = {kp.chapter: kp for kp in kp_result.scalars().all() if kp.chapter}

        all_questions = DS_EXERCISES + DS_CHAPTER_1_ANALYSIS + DS_CHAPTER_3_EX

        count = 0
        skipped = 0
        for q_data in all_questions:
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
        print(f"DS章节习题导入完成！共导入 {count} 道题目，跳过 {skipped} 道。")
        print("来源：数据结构Markdown笔记各章课后习题（含详细答案解析）")
        print("覆盖：第1章绪论(10) 第2章线性表(10) 第3章栈队列(13) 第4章串数组(10)")
        print("      第5章树(9) 第6章图(10) 第7章查找(10) 第8章排序(5)")


if __name__ == "__main__":
    asyncio.run(seed())
