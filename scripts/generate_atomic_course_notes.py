from __future__ import annotations

import json
import textwrap
from collections import defaultdict
from pathlib import Path

import generate_specialty_notes as base


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_DIR = ROOT / "二工大804资料包"
NOTE_ROOT = PACKAGE_DIR / "考研专业课笔记"
NOTES_DIR = NOTE_ROOT / "知识点notes"
FRAMEWORK_PATH = ROOT / "docs" / "804专业课原子概念框架.json"
DS_MD_PATH = PACKAGE_DIR / "数据结构" / "数据结构Markdown版.md"
C_DOC_DIR = ROOT / "scripts" / "doc_converted"

TEXTBOOK_LINES = {
    "C_MOC": "教材：《C语言程序设计》（第4版）何钦铭、颜晖编，高等教育出版社，2023年。",
    "DS_MOC": "教材：《数据结构》（C语言版 第2版）严蔚敏、李冬梅、吴伟民编，人民邮电出版社，2022年。",
}

SOURCE_ENCODINGS = ("utf-8", "gb18030", "gbk")

ALIAS_CATEGORY = {
    "for循环": "statement",
    "while循环": "statement",
    "do-while循环": "statement",
    "scanf": "library_function",
    "strlen": "library_function",
    "strcmp": "library_function",
    "取地址运算": "operator",
    "解引用": "operator",
    "筛法": "algorithm",
    "冒泡排序思想": "algorithm",
    "选择排序思想": "algorithm",
    "图的深度优先遍历": "traversal",
    "图的广度优先遍历": "traversal",
}

ALIAS_DEFINITION_TARGET = {
    "for循环": "for语句",
    "while循环": "while语句",
    "do-while循环": "do-while语句",
    "scanf": "scanf函数",
    "strlen": "strlen函数",
    "strcmp": "strcmp函数",
    "取地址运算": "取地址运算符",
    "解引用": "解引用运算符",
}

CUSTOM_DEFINITIONS = {
    "C程序基本结构": "C程序基本结构是由预处理指令、全局声明、函数定义以及作为入口的 main 函数组成的整体程序框架。",
    "标识符与关键字": "标识符与关键字用于区分“程序员自定义名字”和“语言保留字”，前者要满足命名规则，后者不能被重新定义。",
    "常量与变量": "常量与变量描述程序中的两类数据对象：前者在语义上不应被修改，后者在程序执行过程中可以保存并更新数据。",
    "变量初始化": "变量初始化是变量定义时就为其赋予初始值的过程，用于避免未定义初值带来的不确定结果。",
    "作用域": "作用域说明一个名字在程序文本中从哪里开始可见、在哪些位置可以被合法引用。",
    "局部变量与全局变量": "局部变量与全局变量的区别在于定义位置、可见范围和共享方式，前者面向局部代码块，后者可跨函数共享。",
    "静态局部变量": "静态局部变量是在局部作用域内定义、但生存期贯穿整个程序运行过程的一类变量。",
    "自增自减": "自增自减描述 ++ 和 -- 对变量值进行原位加一或减一时的前置、后置执行差异。",
    "运算符优先级": "运算符优先级规定复杂表达式中不同运算先后结合的规则，只有在优先级相同时才进一步看结合性。",
    "条件表达式": "条件表达式是 C 语言中的三目运算形式，会根据条件真假在两个表达式之间二选一。",
    "类型转换": "类型转换是把一个表达式或对象从当前数据类型变换为另一种数据类型的过程，可能是隐式的，也可能是显式强制转换。",
    "逗号表达式": "逗号表达式会按从左到右的顺序依次计算多个子表达式，并以最后一个子表达式的值作为整体结果。",
    "if-else配对规则": "if-else配对规则指 else 总是与它之前最近且尚未配对的 if 结合，而不是按缩进决定。",
    "枚举法": "枚举法是把所有可能情况按某种顺序逐一列出并检查条件是否成立的求解方法。",
    "一维数组定义": "一维数组定义是为一组同类型元素分配连续存储空间，并通过单一下标访问各元素。",
    "数组下标": "数组下标是访问数组元素时使用的位置标识，在 C 语言中本质上从 0 开始计数。",
    "数组初始化": "数组初始化是在数组定义时给定部分或全部初始元素值的过程。",
    "二维数组定义": "二维数组定义是把同类型元素按照行列结构组织成表格状存储，并通过两个下标定位元素。",
    "二维数组存储与访问": "二维数组存储与访问关注二维数组在内存中的排布方式，以及按行列坐标定位元素的方法。",
    "筛法": "筛法是一类通过逐步标记、排除不满足条件元素来缩小候选范围的算法思想，典型代表是埃拉托斯特尼筛。",
    "冒泡排序思想": "冒泡排序思想是通过相邻元素比较与交换，把较大或较小元素逐趟“冒”到目标位置。",
    "选择排序思想": "选择排序思想是每一趟从未排序部分选出当前最值，再放到已排序区边界位置。",
    "函数声明": "函数声明用于提前说明函数名、返回类型和参数列表，使编译器在调用前知道该函数接口。",
    "函数定义": "函数定义给出了函数的完整接口和函数体，实现该函数的具体计算过程。",
    "形参与实参": "形参与实参分别对应“函数定义中的接收参数”和“函数调用时传入的具体值或表达式”。",
    "值传递": "值传递是调用函数时把实参当前的值复制给形参，因此形参修改通常不会直接改变实参本体。",
    "递推": "递推是利用前面已经求出的结果逐步推出后续结果的求解方式。",
    "递归定义": "递归定义是用问题自身规模更小的同类子问题来描述原问题的定义方式。",
    "递归出口": "递归出口是递归过程中保证调用最终停止并开始回退的终止条件。",
    "指针定义": "指针定义是声明一个用于保存地址值的变量，并明确它所指向对象的类型。",
    "取地址运算": "取地址运算通过 `&` 获取变量在内存中的地址，从而为指针赋值或传址调用提供依据。",
    "解引用": "解引用通过 `*` 按照指针中保存的地址访问目标对象本身。",
    "指针与一维数组": "指针与一维数组描述数组名、首元素地址和指针运算之间的对应关系。",
    "数组名含义": "数组名在大多数表达式环境下会退化为首元素地址，但在 `sizeof` 等少数场景中仍表示整个数组对象。",
    "字符串常量": "字符串常量是在程序中以双引号括起、默认以 `\\0` 结尾保存的只读字符序列。",
    "字符数组与字符串结束符": "字符数组与字符串结束符的核心是区分“字符序列的存放空间”和表示字符串结束的 `\\0`。",
    "结构体定义": "结构体定义是把多个可能类型不同的数据成员组织成一个记录型数据结构的声明方式。",
    "结构体变量": "结构体变量是按结构体类型分配出的具体对象，内部包含该类型定义的全部成员。",
    "结构体数组": "结构体数组是若干个同一结构体类型对象按顺序连续存放形成的数组。",
    "结构体成员访问": "结构体成员访问是通过点运算符或箭头运算符读取、修改结构体内部成员的方式。",
    "结构体指针": "结构体指针是保存结构体对象地址的指针变量，常用于函数传参和动态数据结构。",
    "printf格式控制": "printf格式控制是通过格式说明符、字段宽度和精度等规则决定输出内容表现形式的机制。",
    "字符输入输出": "字符输入输出关注以字符为单位进行输入输出时所使用的函数、数据类型和常见陷阱。",
    "文件指针": "文件指针是指向 `FILE` 结构对象的指针，用来标识和操作一个打开的文件流。",
    "文件打开关闭": "文件打开关闭是文件处理的起点和终点，分别负责建立文件流连接与释放相关资源。",
    "文件读写基础": "文件读写基础关注文本或二进制文件在打开后如何按字符、格式或数据块进行输入输出。",
    "算法五特性": "算法五特性通常指有穷性、确定性、可行性、输入和输出，是判断一个过程能否称为算法的基本标准。",
    "线性表定义": "线性表定义描述一组数据元素之间一对一的线性关系，以及首尾元素和前驱后继约束。",
    "顺序表与链表比较": "顺序表与链表比较关注两者在随机访问、插删代价、存储利用率和实现复杂度上的差异。",
    "出栈序列判定": "出栈序列判定是根据给定入栈顺序分析某个出栈顺序是否可能出现的问题。",
    "递归与栈关系": "递归与栈关系说明递归调用在运行时依赖系统调用栈保存返回地址、局部变量和参数状态。",
    "循环队列判空": "循环队列判空是依据头尾指针当前位置判断当前队列是否不含有效元素的规则。",
    "循环队列判满": "循环队列判满是依据头尾指针关系判断循环队列是否已经没有可用插入位置的规则。",
    "数组地址计算": "数组地址计算是利用基地址、下标和元素长度推导数组元素存储地址的过程。",
    "二维数组按行存储": "二维数组按行存储指同一行元素在内存中连续存放，各行依次排列。",
    "二维数组按列存储": "二维数组按列存储指同一列元素在内存中连续存放，各列依次排列。",
    "特殊矩阵压缩存储": "特殊矩阵压缩存储是利用矩阵元素分布规律，只保存有效元素以节省空间的表示方法。",
    "稀疏矩阵三元组表示": "稀疏矩阵三元组表示是用“行号、列号、值”三元组只存储非零元素的表示方式。",
    "广义表定义": "广义表定义说明广义表元素既可以是原子，也可以是子表，因此能表示层次化递归结构。",
    "树的基本术语": "树的基本术语用于描述树中结点之间的层次角色关系，如双亲、孩子、兄弟、叶子和深度等。",
    "完全二叉树性质": "完全二叉树性质是针对完全二叉树结点编号、层次分布和叶子位置等特点给出的规律总结。",
    "由遍历序列还原二叉树": "由遍历序列还原二叉树是根据前序、中序、后序等遍历结果恢复原树结构的过程。",
    "树森林二叉树转换": "树森林二叉树转换是用左孩子右兄弟等规则在树、森林和二叉树表示之间进行互换。",
    "图的基本术语": "图的基本术语包括顶点、边、弧、度、路径、回路、连通和子图等用于描述图结构的概念。",
    "图的深度优先遍历": "图的深度优先遍历是从某个顶点出发尽量沿一条路径向深处访问，走不通再回溯的访问方法。",
    "图的广度优先遍历": "图的广度优先遍历是从起始顶点开始按层次向外扩展访问相邻顶点的方法。",
    "最短路径": "最短路径问题研究图中两个顶点之间路径长度最小或权值和最小的路径。",
    "哈希函数构造": "哈希函数构造是设计关键字到散列地址映射规则的过程，目标是在分布均匀和计算简单之间取得平衡。",
    "冲突处理": "冲突处理是多个关键字被映射到同一散列地址时，为保证存取仍然可完成而采取的解决策略。",
    "排序稳定性": "排序稳定性是指排序前关键字相等的记录，在排序后相对次序是否保持不变。",
    "排序趟数分析": "排序趟数分析关注某种排序算法在给定输入规模下需要进行多少轮主要处理过程。",
    "排序算法比较": "排序算法比较是从时间复杂度、空间复杂度、稳定性、输入条件和实现难度等角度比较多种排序方法。",
}

CUSTOM_MATCH_ALIASES = {
    "scanf": ["scanf", "标准输入输出函数"],
    "strlen": ["strlen", "字符串长度"],
    "strcmp": ["strcmp", "字符串比较"],
    "printf格式控制": ["printf", "格式说明符", "字段宽度", "输出精度"],
    "字符输入输出": ["getchar", "putchar", "字符输入输出"],
    "文件指针": ["FILE", "文件指针"],
    "文件打开关闭": ["fopen", "fclose", "文件操作"],
    "文件读写基础": ["fprintf", "fscanf", "fread", "fwrite", "文件读写"],
    "形参与实参": ["形式参数", "实际参数"],
    "值传递": ["值传递", "参数传递"],
    "递归出口": ["递归出口", "终止条件"],
    "数组名含义": ["数组名", "首地址"],
    "算法五特性": ["有穷性", "确定性", "可行性", "输入", "输出"],
    "循环队列判空": ["判空", "循环队列"],
    "循环队列判满": ["判满", "循环队列"],
    "最短路径": ["最短路径", "单源最短路径", "全源最短路径"],
    "哈希函数构造": ["哈希函数", "散列函数"],
    "冲突处理": ["冲突处理", "开放定址法", "链地址法"],
    "排序稳定性": ["稳定性", "排序稳定性"],
    "完全二叉树性质": ["完全二叉树"],
}

CUSTOM_SUMMARY_LINES = {
    "if-else配对规则": [
        "if-else配对规则的核心不是缩进，而是 `else` 必须和最近且尚未配对的 `if` 结合。",
        "看到嵌套选择结构时，先画出真实配对关系，再判断输出和执行路径。",
    ],
    "完全二叉树性质": [
        "完全二叉树性质的复习重点是结点编号、父子关系、深度公式和叶子结点个数推导。",
        "考试里这类题常从定义稍作变形，要求你直接计算而不是复述概念。",
    ],
    "形参与实参": [
        "形参与实参必须放在函数调用链里理解，重点是“谁提供值、谁接收值、何时发生绑定”。",
        "程序阅读题经常借它考参数传递和局部变量变化，而不是单独考术语定义。",
    ],
    "值传递": [
        "值传递的关键是“传过去的是副本，不是原变量本体”。",
        "看到函数调用题时，要先判断修改发生在形参副本上，还是通过地址间接作用到实参。",
    ],
    "逗号表达式": [
        "逗号表达式要同时看执行顺序和最终取值，不能只盯最后一个子表达式。",
        "考试常把它和赋值、自增自减放在一起卡优先级和副作用。",
    ],
    "静态局部变量": [
        "静态局部变量兼具“局部可见”和“整个程序运行期保留值”两层特性。",
        "程序阅读题里最容易忽略的是它第二次调用时不会重新初始化。",
    ],
    "数组名含义": [
        "数组名含义的关键不是一句“等于首地址”，而是要分清它在哪些场景会退化、哪些场景不会。",
        "和函数参数、`sizeof`、字符串处理题结合时，是 C 语言高频陷阱点。",
    ],
    "循环队列判空": [
        "循环队列判空必须和具体的头尾指针约定一起记，脱离实现细节就容易背错。",
        "做题时先写清 front、rear 的含义，再判断当前状态。",
    ],
    "循环队列判满": [
        "循环队列判满通常依赖预留一个空位置或额外标志位，不能凭直觉判断。",
        "考试会专门把判空和判满条件对调，考你是否真正理解实现约定。",
    ],
    "排序稳定性": [
        "排序稳定性不是背定义，而是判断相等关键字记录的相对次序是否被改变。",
        "它常与算法比较题一起出现，是选择题、简答题和分析题都爱考的评价维度。",
    ],
    "哈希函数构造": [
        "哈希函数构造的目标是“计算简单、分布均匀、冲突尽量少”。",
        "做题时要把函数形式和关键字集合特征一起考虑，而不是死背某一种公式。",
    ],
    "由遍历序列还原二叉树": [
        "由遍历序列还原二叉树的关键在于先定位根，再递归切分左右子树。",
        "题目一旦缺少中序序列，通常就不能唯一确定原树，这正是高频判断点。",
    ],
}

CUSTOM_CORE_POINTS = {
    "if-else配对规则": [
        "判断配对时只看语法结合规则，不看缩进和排版习惯。",
        "`else` 总是归属于它前面最近的、尚未配对的 `if`。",
        "一旦使用花括号显式成块，真实配对关系会立刻清晰很多。",
    ],
    "完全二叉树性质": [
        "完全二叉树适合顺序存储，结点编号和父子位置之间存在直接公式关系。",
        "深度、叶子结点数、度为1结点数经常放在同一道计算题里联动考查。",
        "复习时要把“定义特征”和“可计算性质”分开记。前者用于判断，后者用于计算。",
    ],
    "形参与实参": [
        "形参出现在函数定义中，实参出现在函数调用中，两者在调用发生时才建立对应关系。",
        "同一个实参表达式传入后，函数内部操作的是形参名字，不是原文本。",
        "做程序阅读题时，要追踪的是实参求值结果如何绑定到形参，而不是只看名称是否相同。",
    ],
    "值传递": [
        "值传递会把实参当前值复制给形参，因此普通形参改动不会回写到原实参变量。",
        "数组名传参是特例高频陷阱，因为传过去的是地址值而不是整数组副本。",
        "要把“值传递”和“通过地址间接修改原对象”明确区分开。",
    ],
    "逗号表达式": [
        "多个子表达式从左到右依次执行，每一步的副作用都要保留。",
        "整个逗号表达式的值取最后一个子表达式的结果。",
        "如果与赋值运算组合，必须额外检查赋值运算和逗号运算之间的优先级关系。",
    ],
    "静态局部变量": [
        "它定义在函数或代码块内部，但只初始化一次，后续调用继续沿用上次结果。",
        "作用域仍然是局部的，不能因为“静态”就误判为全局可见。",
        "程序阅读题常借它考累计效果、函数多次调用和初始化时机。",
    ],
    "数组名含义": [
        "数组名在大多数表达式中会退化为首元素地址，因此可以参与指针运算和函数传参。",
        "在 `sizeof(数组名)`、`&数组名` 等场景中，它仍代表整个数组对象而不是单纯首地址。",
        "字符串处理、函数参数和指针题最喜欢在这里设陷阱。",
    ],
    "循环队列判空": [
        "若采用“空出一个位置”的实现，常见判空条件是 `front == rear`。",
        "判空前先确认 front、rear 分别指向队头元素还是下一插入位置。",
        "不要把顺序队列的直觉直接套到循环队列上。",
    ],
    "循环队列判满": [
        "若采用“空出一个位置”的实现，常见判满条件是 `(rear + 1) % MaxSize == front`。",
        "判满公式永远要和判空公式成对记忆，否则最容易在选择题里对调。",
        "真正做题时建议先画环形下标，再代入公式判断。",
    ],
    "排序稳定性": [
        "稳定性的判断对象是“关键字相等的不同记录”，不是普通数字序列本身。",
        "插入、冒泡、归并、基数通常稳定；选择、希尔、快速、堆通常不稳定。",
        "算法比较题里稳定性常和时间复杂度、空间复杂度一起同时考。 ",
    ],
    "哈希函数构造": [
        "哈希函数既要容易计算，又要让关键字尽量均匀分散到地址空间中。",
        "除留余数法、平方取中法、折叠法等构造方式要会辨认其适用场景。",
        "不能脱离关键字分布和表长去孤立评价一个哈希函数。",
    ],
    "由遍历序列还原二叉树": [
        "先序/后序负责提供根的顺序信息，中序负责切分左右子树范围。",
        "一旦确定根结点，就要按中序位置把问题递归拆成左右子树两部分。",
        "缺少中序信息时，很多题目无法唯一还原原树，这一点必须会判断。",
    ],
}

CUSTOM_EXAM_POINTS = {
    "if-else配对规则": [
        "常见选择题：判断 `else` 最终和哪个 `if` 配对。",
        "常见程序阅读题：不加花括号的嵌套 `if` 结构输出结果判断。",
        "常见改错点：缩进和实际语义不一致，导致逻辑分支理解错误。",
    ],
    "完全二叉树性质": [
        "常见计算题：已知结点总数求深度、叶子结点数、度为2结点数。",
        "常见选择题：利用层序编号判断某结点的双亲、孩子或所在层。",
        "常见判断点：完全二叉树与满二叉树、普通二叉树的区别。",
    ],
    "形参与实参": [
        "常见程序阅读题：指出某个名字是形参还是实参，并跟踪函数调用时值如何传入。",
        "常见填空题：补函数首部或调用语句，考参数个数、顺序和类型。",
        "常见改错点：把定义中的形参和调用中的实参位置写反。",
    ],
    "值传递": [
        "常见程序阅读题：判断函数内部修改后，实参变量最终是否改变。",
        "常见简答点：说明为什么普通变量传参不影响调用者中的原变量。",
        "常见陷阱：数组名、指针和结构体指针传参看似“值传递”，但可经地址间接改原对象。",
    ],
    "逗号表达式": [
        "常见程序阅读题：给出含逗号表达式的赋值语句，要求写出最终结果。",
        "常见陷阱：把整个表达式值误认为第一个子表达式的结果。",
        "常见组合：与自增自减、优先级、条件表达式一起出现。",
    ],
    "静态局部变量": [
        "常见程序阅读题：函数被连续调用多次，要求写出每次返回值或最终输出。",
        "常见选择题：比较静态局部变量与普通局部变量、全局变量的差异。",
        "常见简答点：说明它为什么既是局部变量又能保留值。",
    ],
    "数组名含义": [
        "常见选择题：判断数组名作为函数实参时传递的到底是什么。",
        "常见程序阅读题：数组名与指针表达式混用，要求判断访问对象。",
        "常见陷阱：把 `sizeof(数组名)` 误当作首地址大小。",
    ],
    "循环队列判空": [
        "常见选择题：给定 front、rear 数值，判断队列是否为空。",
        "常见填空题：补循环队列判空条件。",
        "常见分析点：解释为什么该条件不会和判满条件冲突。",
    ],
    "循环队列判满": [
        "常见选择题：给定 front、rear 数值，判断循环队列是否已满。",
        "常见填空题：补循环队列判满公式。",
        "常见分析点：说明为什么通常要牺牲一个存储单元来区分空和满。",
    ],
    "排序稳定性": [
        "常见选择题：判断给定排序算法是否稳定。",
        "常见简答题：解释稳定性定义，并说明它为什么在多关键字排序中重要。",
        "常见分析题：把稳定性与时间复杂度、空间复杂度一起比较。",
    ],
    "哈希函数构造": [
        "常见选择题：给定关键字集合和表长，判断哪种函数更合理。",
        "常见计算题：按指定哈希函数计算地址，并继续结合冲突处理法求最终位置。",
        "常见简答点：说明哈希函数设计原则和装填因子的影响。",
    ],
    "由遍历序列还原二叉树": [
        "常见计算题：给定前序+中序或后序+中序，直接画出二叉树。",
        "常见选择题：判断某组遍历序列能否唯一确定一棵二叉树。",
        "常见分析点：说明为什么没有中序序列时往往无法唯一还原。",
    ],
}

CUSTOM_PITFALLS = {
    "if-else配对规则": [
        "最常见错误是按缩进肉眼判断配对，而不是按语法规则判断。",
        "嵌套 `if` 若不加花括号，极容易把 `else` 归错对象。",
    ],
    "完全二叉树性质": [
        "不要把完全二叉树和满二叉树混为一谈，后者要求每层都满。",
        "做结点数推导时，别漏掉“度为1的结点最多只有1个”这一前提。",
    ],
    "值传递": [
        "不要把“形参变了”误判为“实参一定也变了”。",
        "数组和指针题里最容易把“地址值按值传递”误说成“整个数组按值传递”。",
    ],
    "逗号表达式": [
        "不要忽略前面子表达式的副作用，它们虽然不决定最终值，但会改变变量状态。",
        "和赋值、自增自减连写时，优先级一旦判断错，结果通常全错。",
    ],
    "静态局部变量": [
        "不要把它当作每次调用都会重新初始化的普通局部变量。",
        "也不要因为它能保留值，就误判为其他函数都能直接访问它。",
    ],
    "数组名含义": [
        "“数组名等于指针”是近似说法，不是所有场景都成立。",
        "对 `&数组名`、`数组名`、`&数组[0]` 三者关系若不区分清楚，指针题很容易失分。",
    ],
    "循环队列判空": [
        "不同教材实现约定可能不同，公式一定要和题目给定定义保持一致。",
        "front、rear 所指位置含义没看清，就会把空和满全部判错。",
    ],
    "循环队列判满": [
        "不要把顺序队列“尾到末端即满”的直觉套过来。",
        "若题目采用计数器或标志位法，判满条件就不再是标准的 `(rear + 1) % MaxSize == front`。",
    ],
    "排序稳定性": [
        "判断稳定性时不能只看平均情况，要看算法机制是否可能改变相等关键字的相对次序。",
        "算法名相似时最容易记混，例如“直接插入排序稳定、简单选择排序不稳定”。",
    ],
    "哈希函数构造": [
        "表长选取不合理会显著放大冲突，即使函数形式本身看起来没问题。",
        "不要把哈希函数构造和冲突处理法混为一个概念，它们是两个不同层面。",
    ],
    "由遍历序列还原二叉树": [
        "切分左右子树时一旦中序边界划错，后续整棵树都会错。",
        "没有中序序列时不要轻易说“能唯一还原”，这正是高频陷阱。",
    ],
}

_original_classify = base.classify
_original_build_definition = base.build_definition
_original_find_source_hint = base.find_source_hint
_original_build_one_line_summary = base.build_one_line_summary
_original_build_core_points = base.build_core_points
_original_build_exam_points = base.build_exam_points
_original_build_pitfalls = base.build_pitfalls


def load_framework() -> dict:
    return json.loads(FRAMEWORK_PATH.read_text(encoding="utf-8"))


def read_text_guess(path: Path) -> str:
    for encoding in SOURCE_ENCODINGS:
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    raise UnicodeDecodeError("unknown", b"", 0, 1, f"Unable to decode {path}")


def patch_base_module(framework: dict) -> None:
    for area in framework["subjects"]["C_MOC"]["knowledge_areas"]:
        codes = area["chapter_refs"]["syllabus"]
        for title in area["chapter_refs"].get("textbook_hint", []):
            base.C_EXAM_CHAPTER_MAP[title] = codes

    for concept, aliases in CUSTOM_MATCH_ALIASES.items():
        existing = list(base.MATCH_ALIASES.get(concept, []))
        for alias in aliases:
            if alias not in existing:
                existing.append(alias)
        base.MATCH_ALIASES[concept] = existing

    base.STATEMENT_META["for循环"] = base.STATEMENT_META["for语句"]
    base.STATEMENT_META["while循环"] = base.STATEMENT_META["while语句"]
    base.STATEMENT_META["do-while循环"] = base.STATEMENT_META["do-while语句"]

    base.LIBRARY_FUNCTION_META["scanf"] = base.LIBRARY_FUNCTION_META["scanf函数"]
    base.LIBRARY_FUNCTION_META["strlen"] = base.LIBRARY_FUNCTION_META["strlen函数"]
    base.LIBRARY_FUNCTION_META["strcmp"] = base.LIBRARY_FUNCTION_META["strcmp函数"]

    base.OPERATOR_META["取地址运算"] = base.OPERATOR_META["取地址运算符"]
    base.OPERATOR_META["解引用"] = base.OPERATOR_META["解引用运算符"]

    base.ALGORITHM_META["筛法"] = ("通过标记和剔除不满足条件的元素逐步缩小候选集合", "通常 O(n log log n) 或依具体筛法而定", "O(n)", "适合批量筛选满足某种性质的元素")
    base.ALGORITHM_META["冒泡排序思想"] = base.ALGORITHM_META["冒泡排序"]
    base.ALGORITHM_META["选择排序思想"] = base.ALGORITHM_META["简单选择排序"]

    base.TRAVERSAL_META["图的深度优先遍历"] = ("从起始顶点出发尽量沿一条路径向深处访问，走不通再回溯", "通常借助递归或栈遍历图")
    base.TRAVERSAL_META["图的广度优先遍历"] = ("从起始顶点开始按层向外扩展访问相邻顶点", "通常借助队列遍历图")

    def custom_classify(concept: str) -> str:
        if concept in ALIAS_CATEGORY:
            return ALIAS_CATEGORY[concept]
        return _original_classify(concept)

    def custom_build_definition(concept: str, note_info: dict) -> str:
        if concept in CUSTOM_DEFINITIONS:
            return CUSTOM_DEFINITIONS[concept]
        alias = ALIAS_DEFINITION_TARGET.get(concept)
        if alias:
            return _original_build_definition(alias, note_info)

        if concept.endswith("定义") and len(concept) > 2:
            base_name = concept[:-2]
            return f"{concept}是对{base_name}的概念、组成形式和基本约束所作的明确说明。"
        if concept.endswith("初始化") and len(concept) > 3:
            base_name = concept[:-3]
            return f"{concept}是为{base_name}设置合法起始状态或起始值的过程。"
        if concept.endswith("比较") and len(concept) > 2:
            base_name = concept[:-2]
            return f"{concept}是围绕{base_name}的特点、代价和适用场景进行对照分析的知识点。"
        if concept.endswith("判空") and len(concept) > 2:
            base_name = concept[:-2]
            return f"{concept}是判断{base_name}当前是否没有有效元素或可处理对象的规则。"
        if concept.endswith("判满") and len(concept) > 2:
            base_name = concept[:-2]
            return f"{concept}是判断{base_name}当前是否已无法继续插入新元素的规则。"
        if concept.endswith("还原二叉树"):
            return f"{concept}是根据给定遍历序列一步步重建原二叉树结构的过程。"
        return _original_build_definition(concept, note_info)

    def custom_find_source_hint(concept: str, note_info: dict, source_texts: dict[str, str]) -> str:
        terms = [concept]
        for alias in base.MATCH_ALIASES.get(concept, []):
            if alias not in terms:
                terms.append(alias)

        subjects = sorted(note_info["subjects"])
        for subject in subjects:
            text = source_texts.get(subject, "")
            if not text:
                continue
            lines = text.splitlines()
            for idx, line in enumerate(lines):
                clean_line = line.strip()
                if not clean_line or clean_line.startswith("!") or "pic_center" in clean_line:
                    continue
                if not any(term in clean_line for term in terms):
                    continue
                chunk = " ".join(s.strip() for s in lines[idx : min(idx + 3, len(lines))] if s.strip())
                chunk = " ".join(chunk.split())
                if chunk:
                    return chunk[:220]
        return _original_find_source_hint(concept, note_info, source_texts)

    def custom_build_one_line_summary(concept: str, note_info: dict, practice_questions):
        if concept in CUSTOM_SUMMARY_LINES:
            return CUSTOM_SUMMARY_LINES[concept]
        return _original_build_one_line_summary(concept, note_info, practice_questions)

    def custom_build_core_points(concept: str, note_info: dict):
        if concept in CUSTOM_CORE_POINTS:
            return CUSTOM_CORE_POINTS[concept]
        return _original_build_core_points(concept, note_info)

    def custom_build_exam_points(concept: str, note_info: dict):
        if concept in CUSTOM_EXAM_POINTS:
            return CUSTOM_EXAM_POINTS[concept]
        return _original_build_exam_points(concept, note_info)

    def custom_build_pitfalls(concept: str, note_info: dict):
        if concept in CUSTOM_PITFALLS:
            return CUSTOM_PITFALLS[concept]
        return _original_build_pitfalls(concept, note_info)

    base.classify = custom_classify
    base.build_definition = custom_build_definition
    base.find_source_hint = custom_find_source_hint
    base.build_one_line_summary = custom_build_one_line_summary
    base.build_core_points = custom_build_core_points
    base.build_exam_points = custom_build_exam_points
    base.build_pitfalls = custom_build_pitfalls


def load_source_texts() -> dict[str, str]:
    c_parts: list[str] = []
    for path in sorted(C_DOC_DIR.glob("*.txt")):
        c_parts.append(read_text_guess(path))

    extracted_c = base.extract_c_sources()
    if extracted_c:
        c_parts.append(extracted_c)

    ds_parts: list[str] = []
    if DS_MD_PATH.exists():
        ds_parts.append(DS_MD_PATH.read_text(encoding="utf-8"))

    return {
        "C语言": "\n".join(c_parts),
        "数据结构": "\n".join(ds_parts),
    }


def build_notes_index(framework: dict) -> dict[str, dict]:
    notes: dict[str, dict] = defaultdict(
        lambda: {"contexts": [], "subjects": set(), "children": set(), "parents": set()}
    )

    for moc_name, subject_cfg in framework["subjects"].items():
        subject = subject_cfg["subject_name"]
        for area in subject_cfg["knowledge_areas"]:
            chapter_title = area["chapter_refs"].get("textbook_hint", [area["chapter_refs"]["system_chapter"]])[0]
            concepts = list(area["concepts"])
            for concept in concepts:
                notes[concept]["subjects"].add(subject)
                notes[concept]["contexts"].append(
                    {
                        "subject": subject,
                        "chapter": chapter_title,
                        "label": area["name"],
                        "peers": [item for item in concepts if item != concept],
                        "chapter_peers": [item for item in concepts if item != concept],
                    }
                )

    existing_concepts = set(notes)
    for parent, children in base.EXPANDED_CONCEPTS.items():
        if parent not in existing_concepts:
            continue
        for child in children:
            if child not in existing_concepts:
                continue
            notes[parent]["children"].add(child)
            notes[child]["parents"].add(parent)

    return notes


def build_moc_text(moc_name: str, subject_cfg: dict) -> str:
    lines = [f"# {moc_name}", "", TEXTBOOK_LINES[moc_name], ""]
    lines.append("按 804 出题方式优先组织，原子概念统一用 `[[概念名]]` 表示。先从考法入口定位，再回到知识域索引和具体知识点笔记。")
    lines.append("")
    lines.append("## 考法入口")
    lines.append("")

    area_index = {area["name"]: area for area in subject_cfg["knowledge_areas"]}
    for bucket in subject_cfg["exam_buckets"]:
        lines.append(f"### {bucket['name']}")
        lines.append("")
        for area_name in bucket["knowledge_area_refs"]:
            area = area_index[area_name]
            lines.append(
                f"- {area_name}：对应 804 章节 {'、'.join(area['chapter_refs']['syllabus'])}，"
                f"主入口见下方“{area_name}”知识域索引。"
            )
        lines.append("")

    lines.append("## 主干知识域索引")
    lines.append("")
    for area in subject_cfg["knowledge_areas"]:
        lines.append(f"### {area['name']}")
        lines.append("")
        lines.append(f"- 对应804章节：{'、'.join(area['chapter_refs']['syllabus'])}")
        lines.append(f"- 对应系统章节：{area['chapter_refs']['system_chapter']}")
        textbook_hint = area["chapter_refs"].get("textbook_hint", [])
        if textbook_hint:
            lines.append(f"- 对应教材章节：{'、'.join(textbook_hint)}")
        lines.append(f"- 原子概念：{'、'.join(base.link(concept) for concept in area['concepts'])}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def write_notes(notes: dict[str, dict], source_texts: dict[str, str], question_bank: dict) -> None:
    NOTES_DIR.mkdir(parents=True, exist_ok=True)

    for concept in sorted(notes):
        file_path = NOTES_DIR / f"{base.sanitize_filename(concept)}.md"
        note_text = base.build_note(concept, notes[concept], source_texts, question_bank)
        file_path.write_text(note_text, encoding="utf-8")

    readme = textwrap.dedent(
        f"""\
        # 知识点notes

        - 笔记目录：{NOTES_DIR.name}
        - 当前原子知识点数：{len(notes)}
        - 入口文件：[[C_MOC]]、[[DS_MOC]]
        - 生成脚本：`scripts/generate_atomic_course_notes.py`

        使用建议：
        - 先从 `C_MOC.md` / `DS_MOC.md` 选定题型入口。
        - 再进入具体 `[[原子概念]]`，先看“严格定义与边界”和“考研命题视角”。
        - 每个知识点笔记底部的“现场练手题”和“刷题回填区”用于和题库联动。
        """
    )
    (NOTES_DIR / "README.md").write_text(readme, encoding="utf-8")


def write_root_files(framework: dict) -> None:
    NOTE_ROOT.mkdir(parents=True, exist_ok=True)
    for moc_name in ("C_MOC", "DS_MOC"):
        text = build_moc_text(moc_name, framework["subjects"][moc_name])
        (NOTE_ROOT / f"{moc_name}.md").write_text(text, encoding="utf-8")

    root_readme = textwrap.dedent(
        """\
        # 考研专业课笔记

        - 入口文件：`C_MOC.md`、`DS_MOC.md`
        - 细粒度原子知识点目录：`知识点notes/`
        - 生成方式：`python scripts/generate_atomic_course_notes.py`
        """
    )
    (NOTE_ROOT / "README.md").write_text(root_readme, encoding="utf-8")


def verify_output(framework: dict, notes: dict[str, dict]) -> None:
    expected_count = len(notes)
    actual_files = [path for path in NOTES_DIR.glob("*.md") if path.name != "README.md"]
    if len(actual_files) != expected_count:
        raise RuntimeError(f"Expected {expected_count} note files, found {len(actual_files)}")

    for moc_name in ("C_MOC", "DS_MOC"):
        moc_path = NOTE_ROOT / f"{moc_name}.md"
        if not moc_path.exists():
            raise RuntimeError(f"Missing {moc_path}")
        if "## 考法入口" not in moc_path.read_text(encoding="utf-8"):
            raise RuntimeError(f"{moc_path} missing expected structure")

    for concept in notes:
        note_path = NOTES_DIR / f"{base.sanitize_filename(concept)}.md"
        if not note_path.exists():
            raise RuntimeError(f"Missing note for concept: {concept}")

    print(f"Generated MOC files under: {NOTE_ROOT}")
    print(f"Generated atomic notes: {expected_count}")


def main() -> None:
    framework = load_framework()
    patch_base_module(framework)
    write_root_files(framework)

    source_texts = load_source_texts()
    notes = build_notes_index(framework)
    question_bank = base.fetch_question_bank()
    write_notes(notes, source_texts, question_bank)
    verify_output(framework, notes)


if __name__ == "__main__":
    main()
