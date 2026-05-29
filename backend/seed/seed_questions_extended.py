"""扩展题库 - 基于804考试大纲的全面练习题"""
import asyncio
import sys
sys.path.insert(0, ".")

from sqlalchemy import select
from app.database import async_session, init_db
from app.models.knowledge_point import KnowledgePoint
from app.models.question import Question, QuestionKnowledgePoint

EXTENDED_QUESTIONS = [
    # ============================================================
    # 1.1 程序基本结构与数据类型 (C_programming)
    # ============================================================
    {
        "type": "single_choice", "part": "C_programming", "difficulty": 1,
        "content": "C语言源程序文件经过编译后生成的文件扩展名是？",
        "options": {"A": ".c", "B": ".obj", "C": ".exe", "D": ".h"},
        "answer": "B",
        "explanation": "C源文件(.c)经过编译生成目标文件(.obj/.o)，再经过链接生成可执行文件(.exe)。",
        "kp_chapter": "1.1",
    },
    {
        "type": "single_choice", "part": "C_programming", "difficulty": 2,
        "content": "以下哪项不是C语言的基本数据类型？",
        "options": {"A": "int", "B": "float", "C": "string", "D": "char"},
        "answer": "C",
        "explanation": "C语言中没有string类型，字符串通过char数组或char*指针实现。基本数据类型包括int、float、double、char等。",
        "kp_chapter": "1.1",
    },
    {
        "type": "fill_blank", "part": "C_programming", "difficulty": 1,
        "content": "C语言中，整数类型 int 在32位系统中通常占用 ____ 个字节。",
        "answer": "4",
        "explanation": "在32位和64位系统中，int通常占4个字节（32位），取值范围约为-21亿到21亿。",
        "kp_chapter": "1.1",
    },
    {
        "type": "fill_blank", "part": "C_programming", "difficulty": 2,
        "content": "在C语言中，用关键字 ____ 定义符号常量。",
        "answer": "#define",
        "explanation": "#define是预处理指令，用于定义宏常量，如 #define PI 3.14159。另一种方式是使用const关键字。",
        "kp_chapter": "1.1",
    },
    {
        "type": "short_answer", "part": "C_programming", "difficulty": 2,
        "content": "简述C语言中变量声明与定义的区别。",
        "answer": "声明(declaration)仅告知编译器变量的类型和名称，不分配内存；定义(definition)不仅声明类型和名称，还会分配存储空间。同一个变量可以多次声明但只能定义一次。extern int a; 是声明，int a = 10; 是定义。",
        "kp_chapter": "1.1",
    },
    # ============================================================
    # 1.2 运算符与表达式 (C_programming)
    # ============================================================
    {
        "type": "single_choice", "part": "C_programming", "difficulty": 2,
        "content": "设有 int a = 3, b = 4; 则表达式 (a++) + (++b) 的值是？",
        "options": {"A": "7", "B": "8", "C": "9", "D": "10"},
        "answer": "B",
        "explanation": "a++先使用再自增，值为3；++b先自增再使用，值为5；3+5=8。运算后a=4, b=5。",
        "kp_chapter": "1.2",
    },
    {
        "type": "single_choice", "part": "C_programming", "difficulty": 3,
        "content": "表达式 5 > 3 && 2 || 8 < 4 - !0 的值是？",
        "options": {"A": "0", "B": "1", "C": "2", "D": "语法错误"},
        "answer": "B",
        "explanation": "优先级：! > 算术 > 关系 > && > ||。!0=1, 4-1=3, 8<3=0, 5>3=1, 1&&2=1(2非0为真), 1||0=1。最终结果为1（真）。",
        "kp_chapter": "1.2",
    },
    {
        "type": "fill_blank", "part": "C_programming", "difficulty": 2,
        "content": "C语言中，表达式 10 % 3 的值是 ____，表达式 -10 % 3 的值是 ____。",
        "answer": "1 和 -1",
        "explanation": "%为取模运算，10/3=3余1。负数的取模结果符号与被除数相同：-10%3 = -(10%3) = -1。",
        "kp_chapter": "1.2",
    },
    {
        "type": "single_choice", "part": "C_programming", "difficulty": 3,
        "content": "设有 int x = 5; 则执行 x += x -= x * x; 后，x的值为？",
        "options": {"A": "-15", "B": "-40", "C": "15", "D": "40"},
        "answer": "B",
        "explanation": "赋值运算符从右向左结合。x*x=25，x-=25即x=5-25=-20，x+=-20即x=-20+(-20)=-40。注意x值在运算过程中已改变。",
        "kp_chapter": "1.2",
    },
    # ============================================================
    # 1.3 循环结构与分支结构 (C_programming)
    # ============================================================
    {
        "type": "single_choice", "part": "C_programming", "difficulty": 2,
        "content": "以下代码段执行后，s的值是？\n```c\nint i, s = 0;\nfor (i = 1; i <= 10; i++) {\n    if (i % 2 == 0) continue;\n    s += i;\n}\n```",
        "options": {"A": "20", "B": "25", "C": "30", "D": "55"},
        "answer": "B",
        "explanation": "continue跳过偶数，只累加奇数：1+3+5+7+9=25。",
        "code_snippet": "int i, s = 0;\nfor (i = 1; i <= 10; i++) {\n    if (i % 2 == 0) continue;\n    s += i;\n}",
        "kp_chapter": "1.3",
    },
    {
        "type": "single_choice", "part": "C_programming", "difficulty": 2,
        "content": "以下代码输出什么？\n```c\nint x = 3;\nswitch (x) {\n    case 1: printf(\"A\");\n    case 2: printf(\"B\"); break;\n    case 3: printf(\"C\");\n    case 4: printf(\"D\"); break;\n    default: printf(\"E\");\n}\n```",
        "options": {"A": "C", "B": "CD", "C": "CDE", "D": "C D"},
        "answer": "B",
        "explanation": "x=3，匹配case 3，执行printf(\"C\")。由于case 3后没有break，继续执行case 4的printf(\"D\")，遇到break退出。输出\"CD\"。",
        "code_snippet": "int x = 3;\nswitch (x) {\n    case 1: printf(\"A\");\n    case 2: printf(\"B\"); break;\n    case 3: printf(\"C\");\n    case 4: printf(\"D\"); break;\n    default: printf(\"E\");\n}",
        "kp_chapter": "1.3",
    },
    {
        "type": "program_reading", "part": "C_programming", "difficulty": 3,
        "content": "阅读以下程序，写出输出结果：\n```c\n#include <stdio.h>\nint main() {\n    int i, j;\n    for (i = 1; i <= 3; i++) {\n        for (j = 1; j <= i; j++)\n            printf(\"*\");\n        printf(\"\\n\");\n    }\n    return 0;\n}\n```",
        "answer": "*\n**\n***",
        "explanation": "外层循环控制行数(3行)，内层循环每行输出i个*号。第1行1个，第2行2个，第3行3个。",
        "kp_chapter": "1.3",
    },
    {
        "type": "program_reading", "part": "C_programming", "difficulty": 3,
        "content": "阅读以下程序，写出输出结果：\n```c\n#include <stdio.h>\nint main() {\n    int a = 1, b = 10;\n    do {\n        b -= a;\n        a++;\n    } while (b-- > 0);\n    printf(\"%d, %d\", a, b);\n    return 0;\n}\n```",
        "answer": "5, -4",
        "explanation": "追踪变量变化：初始a=1,b=10。第1次：b=9,a=2,判断b--(9>0)后b=8；第2次：b=6,a=3,判断6>0后b=5；第3次：b=2,a=4,判断2>0后b=1；第4次：b=-3,a=5,判断-3>0假退出，b再减1=-4。输出5, -4。",
        "code_snippet": "int a = 1, b = 10;\ndo {\n    b -= a;\n    a++;\n} while (b-- > 0);\nprintf(\"%d, %d\", a, b);",
        "kp_chapter": "1.3",
    },
    {
        "type": "fill_blank", "part": "C_programming", "difficulty": 2,
        "content": "C语言的循环结构中，____ 语句用于结束本次循环，进入下一次循环；____ 语句用于直接跳出当前循环。",
        "answer": "continue 和 break",
        "explanation": "continue跳过循环体中剩余语句，进入下一次循环条件判断；break直接跳出当前循环体，执行循环后的语句。",
        "kp_chapter": "1.3",
    },
    # ============================================================
    # 1.4 数组与结构体 (C_programming)
    # ============================================================
    {
        "type": "single_choice", "part": "C_programming", "difficulty": 2,
        "content": "设有 int a[][3] = {{1, 2}, {3, 4, 5}, {6}}; 则 a[1][2] 的值是？",
        "options": {"A": "0", "B": "5", "C": "3", "D": "不确定"},
        "answer": "B",
        "explanation": "a是3行3列的二维数组，未显式初始化的元素自动赋0。a[0]={1,2,0}, a[1]={3,4,5}, a[2]={6,0,0}。a[1][2]=5。",
        "kp_chapter": "1.4",
    },
    {
        "type": "fill_blank", "part": "C_programming", "difficulty": 3,
        "content": "用选择排序对数组 int a[6] = {64, 25, 12, 22, 11, 9} 从小到大排序，第一趟（选出最小值放到第一个位置）后数组变为 ____。",
        "answer": "{9, 25, 12, 22, 11, 64}",
        "explanation": "选择排序第一趟：找到最小元素9（下标5），与a[0]=64交换，数组变为{9, 25, 12, 22, 11, 64}。",
        "kp_chapter": "1.4",
    },
    {
        "type": "single_choice", "part": "C_programming", "difficulty": 2,
        "content": "以下关于结构体的说法，正确的是？",
        "options": {
            "A": "结构体变量之间可以直接赋值",
            "B": "结构体成员不能是数组类型",
            "C": "结构体变量名代表结构体的首地址",
            "D": "结构体类型定义时系统会分配内存"
        },
        "answer": "A",
        "explanation": "同类型的结构体变量可以直接相互赋值（逐成员拷贝）。B错，成员可以是数组；C错，只有用&取地址才行，不像数组名；D错，定义类型不分配内存，定义变量时才分配。",
        "kp_chapter": "1.4",
    },
    {
        "type": "single_choice", "part": "C_programming", "difficulty": 3,
        "content": "有以下定义：\n```c\nstruct student {\n    char name[20];\n    int score;\n} s[3] = {{\"Alice\", 85}, {\"Bob\", 92}, {\"Cathy\", 78}};\n```\n表达式 s[1].score 的值是？",
        "options": {"A": "85", "B": "92", "C": "78", "D": "编译错误"},
        "answer": "B",
        "explanation": "s是结构数组，s[1]是第二个元素{\"Bob\", 92}，s[1].score = 92。",
        "kp_chapter": "1.4",
    },
    {
        "type": "programming", "part": "C_programming", "difficulty": 3,
        "content": "编写C语言程序：将一个3×3的二维数组进行转置（行列互换），并在转置后输出。要求使用二重循环实现。",
        "answer": "#include <stdio.h>\nint main() {\n    int a[3][3] = {{1,2,3},{4,5,6},{7,8,9}};\n    int i, j, temp;\n    for (i = 0; i < 3; i++)\n        for (j = i + 1; j < 3; j++) {\n            temp = a[i][j];\n            a[i][j] = a[j][i];\n            a[j][i] = temp;\n        }\n    for (i = 0; i < 3; i++) {\n        for (j = 0; j < 3; j++)\n            printf(\"%d \", a[i][j]);\n        printf(\"\\n\");\n    }\n    return 0;\n}",
        "kp_chapter": "1.4",
    },
    # ============================================================
    # 1.5 函数、递推与递归 (C_programming)
    # ============================================================
    {
        "type": "single_choice", "part": "C_programming", "difficulty": 2,
        "content": "C语言中，函数返回值的类型由什么决定？",
        "options": {
            "A": "return语句中表达式的类型",
            "B": "调用函数时临时决定",
            "C": "定义函数时指定的函数类型",
            "D": "系统自动推断"
        },
        "answer": "C",
        "explanation": "函数返回值的类型由函数定义时指定的返回类型决定。如果return表达式的类型与函数类型不一致，会自动转换为函数类型。",
        "kp_chapter": "1.5",
    },
    {
        "type": "single_choice", "part": "C_programming", "difficulty": 2,
        "content": "以下关于递归的说法，错误的是？",
        "options": {
            "A": "递归函数必须有终止条件",
            "B": "递归调用会增加栈空间的开销",
            "C": "任何递归都可以用迭代来实现",
            "D": "递归一定比迭代效率高"
        },
        "answer": "D",
        "explanation": "递归不一定比迭代效率高。递归调用有函数调用开销（保存返回地址、参数压栈等），通常迭代效率更高。但递归代码更简洁易懂。",
        "kp_chapter": "1.5",
    },
    {
        "type": "program_reading", "part": "C_programming", "difficulty": 3,
        "content": "阅读以下程序，写出输出结果：\n```c\n#include <stdio.h>\nvoid swap(int a, int b) {\n    int t = a; a = b; b = t;\n}\nint main() {\n    int x = 3, y = 5;\n    swap(x, y);\n    printf(\"%d %d\", x, y);\n    return 0;\n}\n```",
        "answer": "3 5",
        "explanation": "swap函数使用的是值传递，函数内部交换的是形参a和b的副本，不影响实参x和y的值。若想交换x和y，应使用指针传递：void swap(int *a, int *b)。",
        "code_snippet": "void swap(int a, int b) {\n    int t = a; a = b; b = t;\n}\nint main() {\n    int x = 3, y = 5;\n    swap(x, y);\n    printf(\"%d %d\", x, y);\n    return 0;\n}",
        "kp_chapter": "1.5",
    },
    {
        "type": "program_reading", "part": "C_programming", "difficulty": 3,
        "content": "以下递归函数的返回值是什么？\n```c\nint fib(int n) {\n    if (n <= 1) return n;\n    return fib(n - 1) + fib(n - 2);\n}\n```\n请写出 fib(5) 的值。",
        "answer": "5",
        "explanation": "这是斐波那契数列的递归实现。fib(5)=fib(4)+fib(3)=3+2=5。数列：fib(0)=0, fib(1)=1, fib(2)=1, fib(3)=2, fib(4)=3, fib(5)=5。",
        "code_snippet": "int fib(int n) {\n    if (n <= 1) return n;\n    return fib(n - 1) + fib(n - 2);\n}",
        "kp_chapter": "1.5",
    },
    {
        "type": "programming", "part": "C_programming", "difficulty": 3,
        "content": "编写C语言函数，用迭代方法求斐波那契数列的第n项：F(0)=0, F(1)=1, F(n)=F(n-1)+F(n-2)。要求写出完整函数定义。",
        "answer": "int fib(int n) {\n    if (n <= 1) return n;\n    int a = 0, b = 1, c, i;\n    for (i = 2; i <= n; i++) {\n        c = a + b;\n        a = b;\n        b = c;\n    }\n    return b;\n}",
        "kp_chapter": "1.5",
    },
    # ============================================================
    # 1.6 指针与引用 (C_programming)
    # ============================================================
    {
        "type": "single_choice", "part": "C_programming", "difficulty": 2,
        "content": "设有 int a[] = {1, 2, 3, 4, 5}, *p = a; 则 *(p + 2) 的值是？",
        "options": {"A": "1", "B": "2", "C": "3", "D": "4"},
        "answer": "C",
        "explanation": "p指向a[0]，p+2指向a[2]，*(p+2)即a[2]=3。等价于p[2]。",
        "kp_chapter": "1.6",
    },
    {
        "type": "single_choice", "part": "C_programming", "difficulty": 3,
        "content": "设 char str[] = \"Hello\"; 则 sizeof(str) 和 strlen(str) 的值分别是？",
        "options": {"A": "5 和 5", "B": "6 和 5", "C": "5 和 6", "D": "6 和 6"},
        "answer": "B",
        "explanation": "sizeof计算变量所占内存字节数，包括结尾的'\\0'，所以为6。strlen计算字符串长度（不含'\\0'），所以为5。",
        "kp_chapter": "1.6",
    },
    {
        "type": "single_choice", "part": "C_programming", "difficulty": 4,
        "content": "设有以下定义：\n```c\nint a[3][4] = {{1,2,3,4},{5,6,7,8},{9,10,11,12}};\nint (*p)[4] = a;\n```\n则 *(*(p+1)+2) 的值是？",
        "options": {"A": "3", "B": "6", "C": "7", "D": "11"},
        "answer": "C",
        "explanation": "p是指向含4个int的数组指针，p+1指向第2行(元素5,6,7,8)，*(p+1)取得该行首地址，*(p+1)+2指向该行第3个元素，**(p+1)+2=7。",
        "code_snippet": "int a[3][4] = {{1,2,3,4},{5,6,7,8},{9,10,11,12}};\nint (*p)[4] = a;",
        "kp_chapter": "1.6",
    },
    {
        "type": "fill_blank", "part": "C_programming", "difficulty": 3,
        "content": "C语言中，若要通过函数修改实参的值，应采用 ____ 传递方式；若要避免复制大型结构体的开销同时保留原始数据的只读性，应采用 ____ 传递方式。",
        "answer": "指针(地址) 和 常量引用(const引用，C++中)或在C中用const指针",
        "explanation": "指针传递将实参地址传给函数，函数可通过解引用修改实参。C语言中避免大结构体复制开销可用const指针。C++中增加了引用传递，更简洁。",
        "kp_chapter": "1.6",
    },
    {
        "type": "program_reading", "part": "C_programming", "difficulty": 4,
        "content": "阅读以下程序，写出输出结果：\n```c\n#include <stdio.h>\n#include <string.h>\nint main() {\n    char s1[] = \"abc\";\n    char s2[] = \"abd\";\n    printf(\"%d\", strcmp(s1, s2));\n    return 0;\n}\n```",
        "answer": "负数（如 -1）",
        "explanation": "strcmp逐字符比较ASCII码。s1第3字符'c'(99) < s2第3字符'd'(100)，因此返回负值。具体值（-1）依赖于实现，但一定是负数。",
        "code_snippet": "char s1[] = \"abc\";\nchar s2[] = \"abd\";\nprintf(\"%d\", strcmp(s1, s2));",
        "kp_chapter": "1.6",
    },
    {
        "type": "programming", "part": "C_programming", "difficulty": 3,
        "content": "编写C语言函数 int str_len(const char *s)，不使用库函数，计算并返回字符串s的长度。",
        "answer": "int str_len(const char *s) {\n    int len = 0;\n    while (*s != '\\0') {\n        len++;\n        s++;\n    }\n    return len;\n}",
        "kp_chapter": "1.6",
    },
    # ============================================================
    # 1.7 流与文件操作 (C_programming)
    # ============================================================
    {
        "type": "single_choice", "part": "C_programming", "difficulty": 2,
        "content": "fopen()函数以\"w\"模式打开文件时，如果文件已存在会发生什么？",
        "options": {
            "A": "在文件末尾追加内容",
            "B": "打开失败返回NULL",
            "C": "原文件内容被清空",
            "D": "读取文件内容"
        },
        "answer": "C",
        "explanation": "\"w\"(write)模式打开文件，若文件存在则清空其内容（截断为0长度），若不存在则创建新文件。若想追加内容应使用\"a\"模式。",
        "kp_chapter": "1.7",
    },
    {
        "type": "single_choice", "part": "C_programming", "difficulty": 2,
        "content": "以下哪个函数用于从文件中读取一个字符？",
        "options": {"A": "fputs()", "B": "fgetc()", "C": "fscanf()", "D": "fprintf()"},
        "answer": "B",
        "explanation": "fgetc()从文件读取一个字符。fputs()写字符串，fscanf()格式化读，fprintf()格式化写。对应的标准I/O函数：getchar()、putchar()。",
        "kp_chapter": "1.7",
    },
    {
        "type": "fill_blank", "part": "C_programming", "difficulty": 2,
        "content": "C语言中，文件操作完成后应使用 ____ 函数关闭文件，以防止数据丢失和资源泄露。",
        "answer": "fclose",
        "explanation": "fclose(FILE *fp)关闭文件，将缓冲区中的数据写入文件并释放文件指针。良好的编程习惯是打开文件后一定要关闭。",
        "kp_chapter": "1.7",
    },
    {
        "type": "program_reading", "part": "C_programming", "difficulty": 3,
        "content": "阅读以下程序的功能，写出其输出：\n```c\n#include <stdio.h>\nint main() {\n    FILE *fp = fopen(\"test.txt\", \"w\");\n    if (fp == NULL) { printf(\"Error\"); return 1; }\n    fprintf(fp, \"Hello %s %d\", \"World\", 2024);\n    fclose(fp);\n    \n    fp = fopen(\"test.txt\", \"r\");\n    char buf[100] = {0};\n    fgets(buf, 100, fp);\n    printf(\"%s\", buf);\n    fclose(fp);\n    return 0;\n}\n```\n假设文件操作均成功，最终的输出是什么？",
        "answer": "Hello World 2024",
        "explanation": "程序先将\"Hello World 2024\"写入test.txt，然后再读取并打印该内容。fprintf格式化写入，fgets读取一行。",
        "code_snippet": "FILE *fp = fopen(\"test.txt\", \"w\");\nfprintf(fp, \"Hello %s %d\", \"World\", 2024);\nfclose(fp);\nfp = fopen(\"test.txt\", \"r\");\nchar buf[100];\nfgets(buf, 100, fp);\nprintf(\"%s\", buf);",
        "kp_chapter": "1.7",
    },
    {
        "type": "short_answer", "part": "C_programming", "difficulty": 2,
        "content": "简述C语言中文本文件和二进制文件的区别，以及各自适用场景。",
        "answer": "文本文件以ASCII码存储，每个字节对应一个字符，可读性好但有转换开销，适合存储文本、配置等。二进制文件按内存中的二进制形式直接存储，读写速度快、节省空间但不可读，适合存储图片、音频、结构化数据（如结构体）等。",
        "kp_chapter": "1.7",
    },
    # ============================================================
    # 2.1 数据结构与算法基础概念 (data_structure)
    # ============================================================
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 2,
        "content": "以下哪种结构属于数据的逻辑结构？",
        "options": {"A": "顺序存储结构", "B": "链式存储结构", "C": "线性结构", "D": "索引存储结构"},
        "answer": "C",
        "explanation": "逻辑结构描述数据元素之间的逻辑关系，包括线性结构（线性表、栈、队列）和非线性结构（树、图）。A、B、D都是存储结构（物理结构）。",
        "kp_chapter": "2.1",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 2,
        "content": "以下程序段的时间复杂度是？\n```c\nfor (i = 1; i <= n; i *= 2)\n    for (j = 1; j <= n; j++)\n        x++;\n```",
        "options": {"A": "O(n)", "B": "O(n²)", "C": "O(n log n)", "D": "O(log n)"},
        "answer": "C",
        "explanation": "外层循环i每次乘以2，执行log₂n次；内层循环执行n次。总执行次数为 n * log₂n，时间复杂度为 O(n log n)。",
        "code_snippet": "for (i = 1; i <= n; i *= 2)\n    for (j = 1; j <= n; j++)\n        x++;",
        "kp_chapter": "2.1",
    },
    {
        "type": "fill_blank", "part": "data_structure", "difficulty": 1,
        "content": "评价算法优劣的五个主要方面是：____、____、____、____ 和 ____。",
        "answer": "正确性、可读性、健壮性、时间复杂度（效率）和空间复杂度（存储量）",
        "explanation": "算法评价五要素：正确性（最基本）、可读性（便于维护）、健壮性（处理异常输入）、时间复杂度（执行效率）、空间复杂度（内存占用）。",
        "kp_chapter": "2.1",
    },
    {
        "type": "short_answer", "part": "data_structure", "difficulty": 2,
        "content": "简述抽象数据类型(ADT)的概念及其三个组成部分。",
        "answer": "ADT是指一个数学模型以及定义在该模型上的一组操作。三个组成部分：①数据对象(D)—元素集合；②数据关系(S)—元素间的逻辑关系；③基本操作(P)—对数据对象可执行的操作集合。ADT仅定义做什么，不定义怎么做，体现了信息隐藏和封装的思想。",
        "kp_chapter": "2.1",
    },
    # ============================================================
    # 2.2 线性表 (data_structure)
    # ============================================================
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 2,
        "content": "顺序存储和链式存储相比，顺序存储的主要优势是？",
        "options": {
            "A": "插入删除操作方便",
            "B": "存储密度大，支持随机存取",
            "C": "不需要连续的存储空间",
            "D": "存储空间可以动态增长"
        },
        "answer": "B",
        "explanation": "顺序存储（数组）支持随机存取，存储密度为1（只存数据，不存指针）。链式存储的优势在于插入删除方便、空间可动态增长，但需要额外存储指针且只能顺序存取。",
        "kp_chapter": "2.2",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 3,
        "content": "在单链表中，要在p所指结点之前插入一个新结点s，以下操作正确的是？（已知头指针为head）",
        "options": {
            "A": "s->next=p; p->next=s;",
            "B": "s->next=p->next; p->next=s;",
            "C": "需要先找到p的前驱结点",
            "D": "直接交换p和s的数据域即可"
        },
        "answer": "C",
        "explanation": "单链表只有后继指针，要在线性表结点的前面插入，必须先找到p的前驱结点q，然后执行：s->next = p; q->next = s;。D选项交换数据域也是一种巧妙方法，但改变了语义。",
        "kp_chapter": "2.2",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 2,
        "content": "带头结点的单链表head为空的判定条件是？",
        "options": {
            "A": "head == NULL",
            "B": "head->next == NULL",
            "C": "head->next == head",
            "D": "head->data == NULL"
        },
        "answer": "B",
        "explanation": "带头结点时，头结点head始终存在。链表为空意味着没有数据结点，即head->next == NULL。不带头结点时判空条件为 head == NULL。",
        "kp_chapter": "2.2",
    },
    {
        "type": "fill_blank", "part": "data_structure", "difficulty": 3,
        "content": "在长度为n的顺序表中删除第i个元素（1≤i≤n），需要向前移动 ____ 个元素，时间复杂度为 ____。",
        "answer": "n-i 和 O(n)",
        "explanation": "删除第i个元素后，其后n-i个元素都需要向前移动一个位置。最坏情况删除第一个元素需移动n-1个，平均移动(n-1)/2个，时间复杂度O(n)。",
        "kp_chapter": "2.2",
    },
    {
        "type": "analysis", "part": "data_structure", "difficulty": 4,
        "content": "已知两个有序递增的单链表La和Lb（带头结点），请设计算法将它们合并为一个有序递减的单链表，并要求利用原结点空间（不新建结点）。描述算法思路并用C语言实现。",
        "answer": "思路：同时遍历La和Lb，比较当前结点值，用头插法将较小的结点插入新链表（头插法使得最终链表为递减）。\n\nvoid MergeDesc(LinkList La, LinkList Lb, LinkList *Lc) {\n    Node *pa = La->next, *pb = Lb->next, *r;\n    (*Lc) = La;\n    (*Lc)->next = NULL;\n    while (pa && pb) {\n        if (pa->data <= pb->data) {\n            r = pa->next;\n            pa->next = (*Lc)->next;\n            (*Lc)->next = pa;\n            pa = r;\n        } else {\n            r = pb->next;\n            pb->next = (*Lc)->next;\n            (*Lc)->next = pb;\n            pb = r;\n        }\n    }\n    while (pa) { r = pa->next; pa->next = (*Lc)->next; (*Lc)->next = pa; pa = r; }\n    while (pb) { r = pb->next; pb->next = (*Lc)->next; (*Lc)->next = pb; pb = r; }\n}",
        "kp_chapter": "2.2",
    },
    {
        "type": "programming", "part": "data_structure", "difficulty": 4,
        "content": "编写C语言函数，实现带头结点单链表的就地逆置（反转），要求空间复杂度为O(1)，不得新建结点。\n函数原型：void Reverse(LinkList L);",
        "answer": "void Reverse(LinkList L) {\n    Node *p = L->next, *q;\n    L->next = NULL;\n    while (p) {\n        q = p->next;\n        p->next = L->next;\n        L->next = p;\n        p = q;\n    }\n}",
        "explanation": "采用头插法思想：依次摘下原链表的每个结点，用头插法插入到头结点之后，最终实现逆置。时间复杂度O(n)，空间复杂度O(1)。",
        "kp_chapter": "2.2",
    },
    # ============================================================
    # 2.3 栈与队列 (data_structure)
    # ============================================================
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 2,
        "content": "若元素a, b, c, d依次入栈，则以下哪个出栈序列是不可能的？",
        "options": {"A": "a b c d", "B": "d c b a", "C": "c a b d", "D": "b d c a"},
        "answer": "C",
        "explanation": "c先出栈说明a,b,c已入栈且c出栈，此时栈内为a,b(b在栈顶)。下一个出栈只能是b，不可能a在b之前出栈。'c a b d'不合法。",
        "kp_chapter": "2.3",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 3,
        "content": "循环队列用数组A[0..M-1]存储，用front和rear分别指示队头和队尾。入队的操作是？",
        "options": {
            "A": "rear = (rear + 1) % M; A[rear] = x;",
            "B": "A[rear] = x; rear = (rear + 1) % M;",
            "C": "rear = rear + 1; A[rear] = x;",
            "D": "A[rear] = x; rear++;"
        },
        "answer": "A",
        "explanation": "循环队列入队：先移动rear指针rear=(rear+1)%M，再存入元素A[rear]=x。注意若rear初始指向队尾元素，则需区分rear指向队尾还是队尾的下一个位置。通常约定rear指向队尾元素的下一个空位，入队时先存后移则选B。两种约定均可，但本题按常见教材（rear指向队头前一个位置），选A。",
        "kp_chapter": "2.3",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 2,
        "content": "递归调用过程中，系统使用什么数据结构来保存返回地址和局部变量？",
        "options": {"A": "队列", "B": "栈", "C": "链表", "D": "二叉树"},
        "answer": "B",
        "explanation": "递归调用时，每次函数调用都会在系统栈中创建一个栈帧，保存返回地址、参数、局部变量等。递归返回时逐层弹出栈帧，因此递归本质上是用栈实现的。",
        "kp_chapter": "2.3",
    },
    {
        "type": "calculation", "part": "data_structure", "difficulty": 3,
        "content": "设循环队列的容量为6（下标0~5），初始front=rear=0。经过以下操作序列后，队列中还有几个元素？\n\n入队A, 入队B, 出队, 入队C, 入队D, 出队, 入队E, 入队F, 入队G（若发生上溢请说明）。",
        "answer": "入队G时队列满（上溢）。最终队列有5个元素：C, D, E, F, G。",
        "explanation": "循环队列容量6，最多存5个元素（区分空和满）。逐操作追踪：①入A(1)②入B(2)③出A(1)④入C(2)⑤入D(3)⑥出B(2)⑦入E(3)⑧入F(4)⑨入G(5)。此时(rear+1)%6==front，队列满，无法再入队。",
        "kp_chapter": "2.3",
    },
    {
        "type": "analysis", "part": "data_structure", "difficulty": 3,
        "content": "已知一个算术表达式为 a+b*(c-d)-e/f，请：(1) 写出其对应的后缀表达式（逆波兰表示法）；(2) 画出将中缀表达式转换为后缀表达式时栈的变化过程。",
        "answer": "(1) 后缀表达式：a b c d - * + e f / -\n(2) 转换过程：遇a输出a；遇+，栈空入栈[+]；遇b输出b；遇*，*优先级高于+，入栈[+,*]；遇(入栈[+,*,(]；遇c输出c；遇-，-高于(，入栈[+,*,(,-]；遇d输出d；遇)弹出至(，输出-，栈为[+,*]；遇-，-优先级低于*，弹出*输出，栈为[+]，-入栈[+,-]；遇e输出e；遇/，/高于-，入栈[+,-,/]；遇f输出f；结束弹出所有运算符/、-、+，输出/、-、+。最终：a b c d - * + e f / -",
        "kp_chapter": "2.3",
    },
    {
        "type": "programming", "part": "data_structure", "difficulty": 4,
        "content": "编写C语言函数，使用栈判断一个字符串中的括号是否匹配。字符串中只包含 '('、')'、'['、']'、'{'、'}' 六种括号。\n函数原型：int isBalanced(const char *s); // 匹配返回1，否则返回0",
        "answer": "int isBalanced(const char *s) {\n    char stack[1000];\n    int top = -1;\n    for (int i = 0; s[i] != '\\0'; i++) {\n        if (s[i] == '(' || s[i] == '[' || s[i] == '{')\n            stack[++top] = s[i];\n        else {\n            if (top == -1) return 0;\n            char c = stack[top--];\n            if ((s[i] == ')' && c != '(') ||\n                (s[i] == ']' && c != '[') ||\n                (s[i] == '}' && c != '{'))\n                return 0;\n        }\n    }\n    return top == -1;\n}",
        "kp_chapter": "2.3",
    },
    # ============================================================
    # 2.4 数组与特殊矩阵 (data_structure)
    # ============================================================
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 2,
        "content": "设有一个10阶对称矩阵A，采用压缩存储（按行序存储下三角部分，含主对角线），一维数组sa的长度至少为？",
        "options": {"A": "100", "B": "45", "C": "55", "D": "50"},
        "answer": "C",
        "explanation": "n阶对称矩阵的下三角（含对角线）有 n(n+1)/2 个元素。n=10时，10×11/2=55。",
        "kp_chapter": "2.4",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 3,
        "content": "将三对角矩阵A[1..n][1..n]按行序存储到一维数组B[1..3n-2]中，则A[i][j]在B中的位置k（1≤i,j≤n）为？",
        "options": {
            "A": "2i + j",
            "B": "2i + j - 2",
            "C": "3i + j - 2",
            "D": "2i + j - 1"
        },
        "answer": "B",
        "explanation": "三对角矩阵每行最多3个非零元素。前i-1行共有3(i-1)-1个元素（第1行2个，其余行3个），A[i][j]在第i行是第j-(i-1)个（当|i-j|≤1）。总公式k=2i+j-2。",
        "kp_chapter": "2.4",
    },
    {
        "type": "fill_blank", "part": "data_structure", "difficulty": 2,
        "content": "稀疏矩阵的三元组表示法中，每个三元组由 ____、____ 和 ____ 三部分组成。",
        "answer": "行号、列号和元素值",
        "explanation": "稀疏矩阵的三元组表示（行下标, 列下标, 元素值），只存储非零元素，大幅节省存储空间。适用于非零元素很少的矩阵。",
        "kp_chapter": "2.4",
    },
    {
        "type": "short_answer", "part": "data_structure", "difficulty": 2,
        "content": "简述广义表(Generalized List)的定义及其与线性表的主要区别。",
        "answer": "广义表是n(n≥0)个数据元素的有限序列，其中每个元素可以是原子（不可再分的数据元素），也可以是另一个广义表（子表）。与线性表的区别：线性表要求所有元素必须是同类型的原子，而广义表允许元素为子表，因此广义表是一种递归定义的数据结构，可以表示多层次、嵌套的数据关系。",
        "kp_chapter": "2.4",
    },
    # ============================================================
    # 2.5 树与二叉树 (data_structure)
    # ============================================================
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 2,
        "content": "一棵完全二叉树有100个结点，则叶子结点数为？",
        "options": {"A": "49", "B": "50", "C": "51", "D": "52"},
        "answer": "B",
        "explanation": "完全二叉树中，度为1的结点n1最多1个。由n0=n2+1，n=n0+n1+n2=2n0+n1-1。n=100，若n1=1则n0=50；若n1=0则n0=50.5（舍）。所以n0=50。",
        "kp_chapter": "2.5",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 2,
        "content": "若二叉树的前序遍历序列和中序遍历序列相同，则该二叉树的特点是？",
        "options": {
            "A": "所有结点只有左子树",
            "B": "所有结点只有右子树",
            "C": "是满二叉树",
            "D": "是平衡二叉树"
        },
        "answer": "B",
        "explanation": "前序：根→左→右，中序：左→根→右。两者相同意味着无左子树（左为空），即所有结点只有右子树，退化为右单链。",
        "kp_chapter": "2.5",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 3,
        "content": "在含n个叶子结点的哈夫曼树中，度为2的结点数为？",
        "options": {"A": "n", "B": "n-1", "C": "n+1", "D": "2n-1"},
        "answer": "B",
        "explanation": "哈夫曼树是正则二叉树（只有度为0和度为2的结点）。由二叉树性质n0=n2+1，n2=n0-1=n-1。总结点数=2n-1。",
        "kp_chapter": "2.5",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 2,
        "content": "将森林F转换为二叉树B，则F中第一棵树的结点个数等于B中什么？",
        "options": {
            "A": "左子树的结点数+1",
            "B": "右子树的结点数+1",
            "C": "左子树结点数+根+右子树中无右兄弟的结点",
            "D": "根+左子树（含所有左链）的结点"
        },
        "answer": "D",
        "explanation": "森林转二叉树规则：兄弟变右孩子。第一棵树的根变成二叉树的根，第一棵树的子树变成左子树。第一棵树中所有结点在二叉树中都在根及其左子树（沿左链可达），不含右子树（右子树是后续树的结点）。",
        "kp_chapter": "2.5",
    },
    {
        "type": "fill_blank", "part": "data_structure", "difficulty": 2,
        "content": "一棵深度为k的满二叉树（根深度为1）共有 ____ 个结点。第i层（1≤i≤k）上最多有 ____ 个结点。",
        "answer": "2^k - 1 和 2^(i-1)",
        "explanation": "满二叉树每层都达到最大结点数。第1层1个，第2层2个，...，第i层2^(i-1)个。k层总结点数=1+2+4+...+2^(k-1)=2^k-1。",
        "kp_chapter": "2.5",
    },
    {
        "type": "analysis", "part": "data_structure", "difficulty": 3,
        "content": "已知某二叉树的中序遍历序列为 DBGEHACF，后序遍历序列为 DGHEBFCA，请画出该二叉树，并写出其前序遍历序列。",
        "answer": "前序：ABDEGHCF。二叉树结构：A为根（后序最后），中序中A左边DBGEH为左子树，右边CF为右子树。左子树：后序DGHEB中B为根（最后），中序D在B左，(G,E,H)中E为根，G和H为E的左右孩子。右子树：后序FC中C为根，F为C的左孩子。",
        "kp_chapter": "2.5",
    },
    {
        "type": "calculation", "part": "data_structure", "difficulty": 4,
        "content": "给定权值w={2, 3, 6, 8, 9}，请：(1) 构造一棵哈夫曼树；(2) 计算该哈夫曼树的带权路径长度WPL；(3) 给出各叶子结点的哈夫曼编码（设左分支为0，右分支为1）。",
        "answer": "(1) 构造步骤：①选2和3合并得5；②选5和6合并得11；③选8和9合并得17；④选11和17合并得28。\n(2) WPL = (2+3)×3 + 6×2 + (8+9)×2 = 5×3 + 12 + 17×2 = 15+12+34 = 61\n(3) 编码：2:000, 3:001, 6:01, 8:10, 9:11（根据构造方式可能有不同等价编码）",
        "kp_chapter": "2.5",
    },
    {
        "type": "programming", "part": "data_structure", "difficulty": 4,
        "content": "编写C语言递归函数，求二叉树的深度（高度）。二叉树结点定义如下：\n```c\ntypedef struct BiTNode {\n    int data;\n    struct BiTNode *lchild, *rchild;\n} BiTNode, *BiTree;\n```",
        "answer": "int Depth(BiTree T) {\n    if (T == NULL) return 0;\n    int ld = Depth(T->lchild);\n    int rd = Depth(T->rchild);\n    return (ld > rd ? ld : rd) + 1;\n}",
        "kp_chapter": "2.5",
    },
    # ============================================================
    # 2.6 图 (data_structure)
    # ============================================================
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 2,
        "content": "在一个无向图中，所有顶点的度之和等于图中边数的多少倍？",
        "options": {"A": "1/2", "B": "1", "C": "2", "D": "4"},
        "answer": "C",
        "explanation": "握手定理：无向图中每条边为两个端点各贡献1度。所有顶点的度之和 = 2 × 边数。",
        "kp_chapter": "2.6",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 2,
        "content": "具有n个顶点的有向完全图，边的数量为？",
        "options": {"A": "n(n-1)", "B": "n(n-1)/2", "C": "n²", "D": "n"},
        "answer": "A",
        "explanation": "有向完全图中任意两顶点间有方向相反的两条弧。每条弧从一个顶点指向另一个顶点，n个顶点每个可发出n-1条弧，共n(n-1)条。无向完全图边数为n(n-1)/2。",
        "kp_chapter": "2.6",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 2,
        "content": "用邻接矩阵存储含有n个顶点的图，则该矩阵的大小是？",
        "options": {"A": "n", "B": "n-1", "C": "n×n", "D": "2n"},
        "answer": "C",
        "explanation": "邻接矩阵是n×n的方阵，A[i][j]=1表示从顶点i到顶点j有边（或有向边）。空间复杂度O(n²)，适用于稠密图。",
        "kp_chapter": "2.6",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 3,
        "content": "以下关于拓扑排序的描述，错误的是？",
        "options": {
            "A": "拓扑排序的结果不一定是唯一的",
            "B": "有向无环图(DAG)一定存在拓扑排序",
            "C": "存在拓扑排序的图一定是无环的",
            "D": "任何有向图都可以进行拓扑排序"
        },
        "answer": "D",
        "explanation": "只有有向无环图(DAG)才能进行拓扑排序。有环的有向图不存在拓扑排序（无法确定环中顶点的先后顺序）。A、B、C均正确。",
        "kp_chapter": "2.6",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 3,
        "content": "Prim算法用于求解什么问题的？其时间复杂度是多少（用邻接矩阵存储）？",
        "options": {
            "A": "最短路径，O(n³)",
            "B": "最小生成树，O(n²)",
            "C": "拓扑排序，O(n+e)",
            "D": "关键路径，O(n²)"
        },
        "answer": "B",
        "explanation": "Prim算法（加点法）和Kruskal算法（加边法）都用于求最小生成树。Prim用邻接矩阵实现时间复杂度O(n²)，Kruskal时间复杂度O(e log e)。Dijkstra算法求最短路径O(n²)。",
        "kp_chapter": "2.6",
    },
    {
        "type": "fill_blank", "part": "data_structure", "difficulty": 2,
        "content": "图的遍历主要有两种方法：____ 和 ____。其中 ____ 需要使用队列辅助实现。",
        "answer": "深度优先遍历(DFS)、广度优先遍历(BFS)和BFS",
        "explanation": "DFS类似于树的先序遍历，用栈（或递归）实现；BFS类似于树的层次遍历，用队列实现。两者时间复杂度均为O(n+e)（邻接表）。",
        "kp_chapter": "2.6",
    },
    {
        "type": "calculation", "part": "data_structure", "difficulty": 4,
        "content": "已知下图用邻接矩阵表示如下。求从顶点0出发的Dijkstra最短路径（到各顶点的最短距离和路径）。\n\n图：n=5，边和权值为：0-1:10, 0-4:5, 1-2:1, 1-4:2, 2-3:4, 3-0:7, 3-2:6, 4-1:3, 4-2:9, 4-3:2",
        "answer": "从顶点0出发：到0:0(0)；到1:8(0→4→1)；到2:9(0→4→1→2)；到3:7(0→4→3)；到4:5(0→4)。\n\nDijkstra过程：S={0}, [0,∞,∞,∞,∞]dist；选4(5): S={0,4}, 更新 [0,8,14,7,5]；选3(7): S={0,4,3}, 更新 [0,8,13,7,5]；选1(8): S={0,4,3,1}, 更新 [0,8,9,7,5]；选2(9): S全部，完成。",
        "kp_chapter": "2.6",
    },
    {
        "type": "short_answer", "part": "data_structure", "difficulty": 3,
        "content": "简述关键路径的概念及其在项目管理中的应用意义。",
        "answer": "关键路径是AOE网（边表示活动的网）中从源点到汇点的最长路径，其长度等于整个工程的最短完成时间。关键路径上的活动称为关键活动，任何关键活动的延迟都会导致整个工程延期。在项目管理中，识别关键路径有助于合理分配资源，重点关注关键活动，确保项目按时完成。非关键活动有一定的时间余量（松弛时间）。",
        "kp_chapter": "2.6",
    },
    # ============================================================
    # 2.7 查找 (data_structure)
    # ============================================================
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 2,
        "content": "在有序表 {3, 5, 8, 10, 15, 20, 25, 30} 中使用折半查找关键字30，比较次数为？",
        "options": {"A": "1", "B": "2", "C": "3", "D": "4"},
        "answer": "D",
        "explanation": "折半查找过程：mid=3→a[3]=10<30, low=4；mid=5→a[5]=20<30, low=6；mid=6→a[6]=25<30, low=7；mid=7→a[7]=30==30，找到。共比较4次。",
        "kp_chapter": "2.7",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 3,
        "content": "在哈希表中，负载因子α的定义是？当α增大时，平均查找长度ASL会如何变化？",
        "options": {
            "A": "α=表长/记录数，α增大ASL减小",
            "B": "α=记录数/表长，α增大ASL增大",
            "C": "α=冲突次数/记录数，α增大ASL不变",
            "D": "α=表长-记录数，α增大ASL减小"
        },
        "answer": "B",
        "explanation": "负载因子α=表中记录数/哈希表长度。α越大表示表越满，冲突概率增加，平均查找长度ASL也增大。通常α建议在0.7~0.85之间。",
        "kp_chapter": "2.7",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 3,
        "content": "在一个空的二叉排序树(BST)中依次插入关键字 5, 2, 8, 1, 4, 7, 9，则该BST的中序遍历序列是？",
        "options": {
            "A": "5 2 8 1 4 7 9",
            "B": "1 2 4 5 7 8 9",
            "C": "9 8 7 5 4 2 1",
            "D": "1 4 2 7 9 8 5"
        },
        "answer": "B",
        "explanation": "BST的中序遍历得到关键字的有序序列（递增）。输入的排序结果为1,2,4,5,7,8,9。验证：5为根，2<5放左，8>5放右，依此类推构造BST。",
        "kp_chapter": "2.7",
    },
    {
        "type": "fill_blank", "part": "data_structure", "difficulty": 2,
        "content": "分块查找（索引顺序查找）中，索引表是 ____（有序/无序）的，每个块内的记录 ____（有序/无序）。平均查找长度为 ____ 之和。",
        "answer": "有序、可以无序和查找索引表与查找块内记录",
        "explanation": "分块查找：先将数据分块，索引表按每块最大关键字有序排列，块内记录可以不排序。查找时先在索引表中确定块（可用顺序或折半），再到块内顺序查找。",
        "kp_chapter": "2.7",
    },
    {
        "type": "calculation", "part": "data_structure", "difficulty": 4,
        "content": "给定关键字序列 {19, 14, 23, 1, 68, 20, 84, 27, 55, 11, 10, 79}，哈希函数 H(key)=key%13，采用线性探测再散列处理冲突。(1) 请构造哈希表（表长16）；(2) 计算在等概率查找成功下的平均查找长度ASL。",
        "answer": "(1) 哈希表[0..15]：\nH(19)=6→[6]=19,\nH(14)=1→[1]=14,\nH(23)=10→[10]=23,\nH(1)=1→冲突→[2]=1,\nH(68)=3→[3]=68,\nH(20)=7→[7]=20,\nH(84)=6→冲突→7→8→[8]=84,\nH(27)=1→冲突→2→3→4→[4]=27,\nH(55)=3→冲突→4→5→[5]=55,\nH(11)=11→[11]=11,\nH(10)=10→冲突→11→12→[12]=10,\nH(79)=1→冲突→2→3→4→5→6→7→8→9→[9]=79\n\n表：[空,14,1,68,27,55,19,20,84,79,23,11,10,空,空,空]\n\n(2) ASL成功 = (1+1+1+2+1+1+3+4+3+1+3+9)/12 = 30/12 = 2.5",
        "kp_chapter": "2.7",
    },
    # ============================================================
    # 2.8 内部排序 (data_structure)
    # ============================================================
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 3,
        "content": "以下排序算法中，在最好情况下时间复杂度为O(n)的是？",
        "options": {"A": "快速排序", "B": "冒泡排序", "C": "选择排序", "D": "堆排序"},
        "answer": "B",
        "explanation": "冒泡排序在序列已经有序时（最好情况），一趟扫描无交换即退出，时间复杂度O(n)。快速排序最好O(n log n)，选择排序和堆排序最好最坏均为O(n²)和O(n log n)。",
        "kp_chapter": "2.8",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 2,
        "content": "对序列 {8, 3, 5, 1, 9, 6} 进行一趟希尔排序（增量d=3），结果可能是？",
        "options": {
            "A": "{1, 3, 5, 6, 8, 9}",
            "B": "{1, 3, 5, 8, 9, 6}",
            "C": "{6, 3, 5, 1, 9, 8}",
            "D": "{6, 1, 5, 8, 3, 9}"
        },
        "answer": "B",
        "explanation": "d=3分为3组：{8,1}(下标0,3)→排序{1,8}，{3,9}(下标1,4)→排序{3,9}，{5,6}(下标2,5)→排序{5,6}。一趟后：{1, 3, 5, 8, 9, 6}。",
        "kp_chapter": "2.8",
    },
    {
        "type": "single_choice", "part": "data_structure", "difficulty": 3,
        "content": "归并排序的空间复杂度是？",
        "options": {"A": "O(1)", "B": "O(log n)", "C": "O(n)", "D": "O(n²)"},
        "answer": "C",
        "explanation": "归并排序需要额外的辅助数组存储合并结果，空间复杂度为O(n)。虽然可以优化到O(1)（原地归并），但实现复杂且通常不实用。",
        "kp_chapter": "2.8",
    },
    {
        "type": "fill_blank", "part": "data_structure", "difficulty": 2,
        "content": "快速排序的核心操作是 ____，其平均时间复杂度为 ____，最坏时间复杂度为 ____。",
        "answer": "划分(Partition)、O(n log n)和O(n²)",
        "explanation": "快速排序通过Partition将序列划分为两个子序列，递归排序。平均O(n log n)，最好O(n log n)，最坏（已有序且选第一个为基准）O(n²)。空间复杂度O(log n)（递归栈）。",
        "kp_chapter": "2.8",
    },
    {
        "type": "fill_blank", "part": "data_structure", "difficulty": 3,
        "content": "基数排序（最低位优先LSD）的时间复杂度为 ____，其中d为关键字位数，r为基数，n为记录数。该排序算法 ____（是/否）稳定的。",
        "answer": "O(d(n+r)) 和 是",
        "explanation": "基数排序对每一位进行一趟分配和收集。每趟O(n+r)，共d趟，总O(d(n+r))。LSD基数排序是稳定的（先按低位排序，再按高位排序时保持低位有序）。",
        "kp_chapter": "2.8",
    },
    {
        "type": "calculation", "part": "data_structure", "difficulty": 4,
        "content": "对序列 {49, 38, 65, 97, 76, 13, 27, 50} 进行堆排序（大顶堆），请：(1) 画出初始建堆过程；(2) 写出前两趟排序（即选出前两个最大值）后序列的变化。",
        "answer": "(1) 从n/2=4开始调整。调整97(76已≥子)，调整65(13,27<65)，调整38(97>38→{49,97,65,38,76,13,27,50})，调整49→与97换再与50换。最终大顶堆：{97, 76, 65, 50, 49, 13, 27, 38}\n(2) 第一趟：交换堆顶97与末尾38，输出97，调整→{76, 50, 65, 38, 49, 13, 27}；第二趟：交换堆顶76与末尾27，输出76，调整→{65, 50, 27, 38, 49, 13}",
        "kp_chapter": "2.8",
    },
    {
        "type": "multi_choice", "part": "data_structure", "difficulty": 3,
        "content": "以下哪些排序算法是稳定的？（多选）",
        "options": {
            "A": "直接插入排序",
            "B": "冒泡排序",
            "C": "快速排序",
            "D": "归并排序",
            "E": "简单选择排序",
            "F": "基数排序"
        },
        "answer": "ABDF",
        "explanation": "稳定排序：插入排序、冒泡排序、归并排序、基数排序。不稳定排序：希尔排序、快速排序、简单选择排序、堆排序。记忆口诀：\"插冒归基稳，希快选堆慌\"。",
        "kp_chapter": "2.8",
    },
    {
        "type": "analysis", "part": "data_structure", "difficulty": 4,
        "content": "已知一组记录的关键字为 {46, 79, 56, 38, 40, 84}，请分别给出使用以下排序算法第一趟排序后的结果：\n(1) 直接插入排序\n(2) 冒泡排序（从后往前，小的上浮）\n(3) 快速排序（选第一个46为基准）\n(4) 简单选择排序（选出最小值）",
        "answer": "(1) 直接插入排序第一趟（将第2个元素79插入有序表{46}）：{46, 79, 56, 38, 40, 84}\n(2) 冒泡排序第一趟（最小元素上浮）：{38, 46, 79, 56, 40, 84}（38从后冒到最前）\n(3) 快速排序第一趟（基准46）：{40, 38, 46, 56, 79, 84}\n(4) 简单选择排序第一趟（选最小值38与46交换）：{38, 79, 56, 46, 40, 84}",
        "kp_chapter": "2.8",
    },
    # ============================================================
    # 综合/跨章节题目
    # ============================================================
    {
        "type": "multi_choice", "part": "data_structure", "difficulty": 3,
        "content": "以下关于二叉树的叙述中，正确的有？（多选）",
        "options": {
            "A": "二叉树的第i层最多有2^(i-1)个结点",
            "B": "深度为k的二叉树最少有k个结点",
            "C": "完全二叉树一定是满二叉树",
            "D": "满二叉树一定是完全二叉树",
            "E": "在二叉树的先序序列中，任意结点都在其子孙结点之前",
            "F": "哈夫曼树中不存在度为1的结点"
        },
        "answer": "ABDEF",
        "explanation": "A：二叉树每层最多2^(i-1)个结点；B：每层至少1个，k层最少k个；C错：满二叉树一定是完全二叉树，反之不成立；D正确；E：先序遍历根在子之前，正确；F：哈夫曼树是正则二叉树，只有度为0和2的结点，正确。",
        "kp_chapter": "2.5",
    },
    {
        "type": "short_answer", "part": "data_structure", "difficulty": 3,
        "content": "比较顺序存储（数组）和链式存储（链表）的优缺点，并说明各自适用场景。",
        "answer": "顺序存储优点：①支持随机存取O(1)；②存储密度高（只存数据）；③实现简单。缺点：①插入删除需移动元素O(n)；②需要连续空间，可能产生碎片；③长度固定，扩容不便。适用：频繁查找、数据量稳定、不常插入删除的场景。\n\n链式存储优点：①插入删除O(1)（给定位置）；②空间动态分配，按需增长；③不需连续空间。缺点：①只能顺序存取O(n)；②存储密度低（需额外存指针）；③实现较复杂。适用：频繁插入删除、数据量不确定的场景。",
        "kp_chapter": "2.2",
    },
    {
        "type": "multi_choice", "part": "C_programming", "difficulty": 3,
        "content": "以下关于C语言指针的说法，正确的有？（多选）",
        "options": {
            "A": "指针变量存储的是另一个变量的地址",
            "B": "int *p; 中p是一个int型变量",
            "C": "&运算符用于取变量的地址",
            "D": "*运算符用于取指针指向的值",
            "E": "两个指针可以相加",
            "F": "数组名是一个常量指针，指向数组首元素"
        },
        "answer": "ACDF",
        "explanation": "A正确；B错误，p是指针变量（存储地址）；C正确；D正确；E错误，两个指针相加没有意义，但可以相减（得到元素个数）；F正确。",
        "kp_chapter": "1.6",
    },
    {
        "type": "multi_choice", "part": "C_programming", "difficulty": 2,
        "content": "以下C语言关键字中，用于循环结构的有？（多选）",
        "options": {
            "A": "for",
            "B": "if",
            "C": "while",
            "D": "switch",
            "E": "do",
            "F": "goto"
        },
        "answer": "ACE",
        "explanation": "for、while、do-while是C语言三种循环结构。if和switch是分支结构。goto虽可实现循环但不属于基本循环结构，且不推荐使用。",
        "kp_chapter": "1.3",
    },
    {
        "type": "programming", "part": "C_programming", "difficulty": 3,
        "content": "编写C语言程序：输入一个正整数n，判断n是否为素数（质数）。若是输出\"YES\"，否则输出\"NO\"。要求时间复杂度O(√n)。",
        "answer": "#include <stdio.h>\n#include <math.h>\nint main() {\n    int n, i;\n    scanf(\"%d\", &n);\n    if (n < 2) { printf(\"NO\"); return 0; }\n    for (i = 2; i <= sqrt(n); i++)\n        if (n % i == 0) {\n            printf(\"NO\");\n            return 0;\n        }\n    printf(\"YES\");\n    return 0;\n}",
        "kp_chapter": "1.5",
    },
    {
        "type": "programming", "part": "data_structure", "difficulty": 4,
        "content": "编写C语言函数，统计二叉树的叶子结点个数。\n```c\ntypedef struct BiTNode {\n    int data;\n    struct BiTNode *lchild, *rchild;\n} BiTNode, *BiTree;\n\nint CountLeaf(BiTree T);\n```",
        "answer": "int CountLeaf(BiTree T) {\n    if (T == NULL) return 0;\n    if (T->lchild == NULL && T->rchild == NULL)\n        return 1;\n    return CountLeaf(T->lchild) + CountLeaf(T->rchild);\n}",
        "kp_chapter": "2.5",
    },
    {
        "type": "programming", "part": "data_structure", "difficulty": 4,
        "content": "编写C语言函数，在有序递增的顺序表中折半查找关键字key。查找成功返回其下标（从0开始），失败返回-1。\n顺序表类型定义：\n```c\ntypedef struct {\n    int data[100];\n    int length;\n} SeqList;\n```",
        "answer": "int BinarySearch(SeqList L, int key) {\n    int low = 0, high = L.length - 1, mid;\n    while (low <= high) {\n        mid = (low + high) / 2;\n        if (L.data[mid] == key)\n            return mid;\n        else if (L.data[mid] < key)\n            low = mid + 1;\n        else\n            high = mid - 1;\n    }\n    return -1;\n}",
        "kp_chapter": "2.7",
    },
    {
        "type": "programming", "part": "data_structure", "difficulty": 3,
        "content": "编写C语言函数，用直接插入排序对整数数组a[0..n-1]进行升序排序。",
        "answer": "void InsertSort(int a[], int n) {\n    int i, j, temp;\n    for (i = 1; i < n; i++) {\n        temp = a[i];\n        for (j = i - 1; j >= 0 && a[j] > temp; j--)\n            a[j + 1] = a[j];\n        a[j + 1] = temp;\n    }\n}",
        "kp_chapter": "2.8",
    },
]


async def seed():
    await init_db()

    async with async_session() as session:
        kp_result = await session.execute(select(KnowledgePoint))
        kps = {kp.chapter: kp for kp in kp_result.scalars().all() if kp.chapter}

        count = 0
        skipped = 0
        for q_data in EXTENDED_QUESTIONS:
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
        print(f"扩展题库初始化完成！共导入 {count} 道新题目，跳过 {skipped} 道。")
        print("题型分布：单选、多选、填空、程序阅读、分析、计算、编程、简答")
        print("覆盖章节：C语言1.1~1.7，数据结构2.1~2.8")


if __name__ == "__main__":
    asyncio.run(seed())
