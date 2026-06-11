import sys
sys.stdout.reconfigure(encoding='utf-8')

# Fix Progress
c = open('frontend/src/pages/Progress/index.tsx', 'r', encoding='utf-8').read()

# Remove unused Space import
c = c.replace(
    "import { Button, Card, Row, Col, Spin, Empty, Progress, Tabs, Table, Tag, Space } from 'antd';",
    "import { Button, Card, Row, Col, Spin, Empty, Progress, Tabs, Table, Tag } from 'antd';"
)

# Fix imports - remove BookOutlined, TrophyOutlined, CheckCircleOutlined
old_imports = """import {
  BookOutlined,
  TrophyOutlined,
  CodeOutlined,"""
new_imports = """import {
  CodeOutlined,"""
c = c.replace(old_imports, new_imports)

c = c.replace(
    """  CheckCircleOutlined,
  FireOutlined,""",
    """  FireOutlined,"""
)

# Fix Tooltip formatter
c = c.replace(
    "formatter={(value: number) => [`${value}%`, '掌握度']}",
    "formatter={(value) => [`${value}%`, '掌握度']}"
)

open('frontend/src/pages/Progress/index.tsx', 'w', encoding='utf-8').write(c)
print('Progress fixed')

# Fix ReviewPlan
c2 = open('frontend/src/pages/ReviewPlan/index.tsx', 'r', encoding='utf-8').read()
c2 = c2.replace(
    "import { Card, Button, Tag, Space, Spin, Result, Progress, Rate, message, Statistic, Row, Col } from 'antd';",
    "import { Card, Button, Tag, Space, Spin, Result, Progress, Rate, message, Row, Col } from 'antd';"
)
c2 = c2.replace(
    """  FlagOutlined,
  BulbOutlined,
  TrophyOutlined,
  ThunderboltOutlined,""",
    """  BulbOutlined,
  TrophyOutlined,"""
)
open('frontend/src/pages/ReviewPlan/index.tsx', 'w', encoding='utf-8').write(c2)
print('ReviewPlan fixed')
