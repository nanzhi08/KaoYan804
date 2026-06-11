import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button, Card, Row, Col, Statistic, Spin, Empty, Progress, Tabs, Table, Tag, Collapse, Space } from "antd";
import {
  BookOutlined, TrophyOutlined, CodeOutlined, RadarChartOutlined,
  RiseOutlined, CheckCircleOutlined, FireOutlined, ScheduleOutlined,
} from "@ant-design/icons";
import { fetchProgressDetail, fetchProgressOverview } from "../../services/progressApi";
import type { ChapterProgress, ProgressOverview } from "../../types";
import {
  RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar,
  ResponsiveContainer, Tooltip,
} from "recharts";

const partColors: Record<string, string> = {
  C_programming: "#6366F1",
  data_structure: "#10B981",
};

const examWeightColors: Record<string, string> = {
  "高频": "#EF4444",
  "中频": "#F59E0B",
  "低频": "#6366F1",
};

type ChapterRadarDatum = {
  axis: string;
  chapter: string;
  part: string;
  mastery: number;
  totalAttempts: number;
  pointCount: number;
};

const getMasteryColor = (value: number) => (
  value >= 70 ? "#10B981" : value >= 40 ? "#F59E0B" : "#EF4444"
);

const getMasteryLabel = (value: number) => (
  value >= 70 ? "掌握较好" : value >= 40 ? "需要巩固" : "重点补强"
);

const getWeaknessScore = (item: ChapterProgress) => {
  const weightScore = item.exam_weight === "高频" ? 30 : item.exam_weight === "中频" ? 16 : 8;
  const attemptScore = item.total_attempts === 0 ? 10 : 0;
  return (100 - item.mastery_level) + weightScore + attemptScore;
};

const buildChapterRadarData = (items: ChapterProgress[]): ChapterRadarDatum[] => {
  const chapterMap = new Map<string, {
    chapter: string; part: string; masterySum: number; attemptsSum: number; pointCount: number;
  }>();

  items.forEach((item) => {
    const chapter = item.chapter || "未分类";
    const key = `${item.part}::${chapter}`;
    const current = chapterMap.get(key) ?? {
      chapter, part: item.part, masterySum: 0, attemptsSum: 0, pointCount: 0,
    };
    current.masterySum += item.mastery_level;
    current.attemptsSum += item.total_attempts;
    current.pointCount += 1;
    chapterMap.set(key, current);
  });

  return Array.from(chapterMap.values()).map((item) => ({
    axis: item.chapter,
    chapter: item.chapter,
    part: item.part,
    mastery: Math.round(item.masterySum / item.pointCount),
    totalAttempts: item.attemptsSum,
    pointCount: item.pointCount,
  }));
};

const SubjectRadarCard: React.FC<{
  title: string; color: string; icon: React.ReactNode; data: ChapterRadarDatum[];
}> = ({ title, color, icon, data }) => {
  const weakest = data.reduce<ChapterRadarDatum | null>(
    (worst, item) => (!worst || item.mastery < worst.mastery ? item : worst), null,
  );
  const averageMastery = data.length
    ? Math.round(data.reduce((sum, item) => sum + item.mastery, 0) / data.length)
    : 0;

  return (
    <Card title={<span>{icon} {title}</span>} size="small">
      {data.length === 0 ? (
        <Empty description="暂无章节掌握数据" image={Empty.PRESENTED_IMAGE_SIMPLE} />
      ) : (
        <>
          <Row gutter={12} style={{ marginBottom: 16 }}>
            <Col span={8}>
              <Card size="small">
                <Statistic title="章节数" value={data.length} />
              </Card>
            </Col>
            <Col span={8}>
              <Card size="small">
                <Statistic title="平均掌握度" value={averageMastery} suffix="%" styles={{ content: { color } }} />
              </Card>
            </Col>
            <Col span={8}>
              <Card size="small">
                <div style={{ color: "#64748B", fontSize: 12, marginBottom: 6 }}>当前最弱章节</div>
                <div style={{ fontWeight: 600, marginBottom: 4 }}>{weakest?.chapter || "-"}</div>
                <Tag color={getMasteryColor(weakest?.mastery ?? 0)}>
                  {weakest?.mastery ?? 0}% · {getMasteryLabel(weakest?.mastery ?? 0)}
                </Tag>
              </Card>
            </Col>
          </Row>
          <div style={{ height: 320, minWidth: 0, minHeight: 320 }}>
            <ResponsiveContainer width="100%" height="100%" minWidth={280} minHeight={320} initialDimension={{ width: 560, height: 320 }}>
              <RadarChart data={data} outerRadius="68%">
                <PolarGrid gridType="polygon" />
                <PolarAngleAxis dataKey="axis" fontSize={12} />
                <PolarRadiusAxis angle={30} domain={[0, 100]} />
                <Radar name="掌握度" dataKey="mastery" stroke={color} fill={color} fillOpacity={0.18} />
                <Tooltip />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </>
      )}
    </Card>
  );
};

const chapterColumns = [
  { title: "知识点", dataIndex: "name", key: "name", ellipsis: true },
  { title: "章节", dataIndex: "chapter", key: "chapter", render: (v: string) => <Tag>{v}</Tag> },
  { title: "考频", dataIndex: "exam_weight", key: "exam_weight", align: "center" as const, render: (v: string) => v ? <Tag color={examWeightColors[v]}>{v}</Tag> : "-" },
  {
    title: "掌握度", dataIndex: "mastery_level", key: "mastery", sorter: (a: ChapterProgress, b: ChapterProgress) => a.mastery_level - b.mastery_level,
    render: (v: number) => <Progress percent={Math.round(v)} size="small" strokeColor={getMasteryColor(v)} />,
  },
  { title: "练习次数", dataIndex: "total_attempts", key: "attempts", align: "center" as const },
  { title: "状态", dataIndex: "mastery_level", key: "status", render: (v: number) => <Tag color={v >= 70 ? "success" : v >= 40 ? "warning" : "error"}>{getMasteryLabel(v)}</Tag> },
];

const ProgressPage: React.FC = () => {
  const navigate = useNavigate();
  const [overview, setOverview] = useState<ProgressOverview | null>(null);
  const [chapters, setChapters] = useState<ChapterProgress[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([fetchProgressOverview(), fetchProgressDetail()])
      .then(([ov, ch]) => { setOverview(ov); setChapters(ch); })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <Spin size="large" style={{ display: "block", margin: "100px auto" }} />;
  if (!overview) return <Empty description="无法加载学习统计" />;

  const cChapters = chapters.filter((ch) => ch.part === "C_programming");
  const dsChapters = chapters.filter((ch) => ch.part === "data_structure");
  const cAvgMastery = cChapters.length ? Math.round(cChapters.reduce((s, c) => s + c.mastery_level, 0) / cChapters.length) : 0;
  const dsAvgMastery = dsChapters.length ? Math.round(dsChapters.reduce((s, c) => s + c.mastery_level, 0) / dsChapters.length) : 0;
  const cRadarData = buildChapterRadarData(cChapters);
  const dsRadarData = buildChapterRadarData(dsChapters);

  const weakChapters = chapters
    .filter((ch) => ch.mastery_level < 70)
    .sort((a, b) => getWeaknessScore(b) - getWeaknessScore(a))
    .slice(0, 6);

  return (
    <div>
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col xs={12} sm={6}>
          <Card><Statistic title="总练习次数" value={overview.total_attempts} prefix={<BookOutlined />} /></Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card><Statistic title="正确次数" value={overview.total_correct} prefix={<CheckCircleOutlined />} styles={{ content: { color: "#10B981" } }} /></Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card><Statistic title="正确率" value={overview.accuracy} suffix="%" prefix={<TrophyOutlined />} /></Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card><Statistic title="今日练习" value={overview.today_attempts} prefix={<FireOutlined />} styles={{ content: { color: overview.today_attempts > 0 ? "#F59E0B" : "#94A3B8" } }} /></Card>
        </Col>
      </Row>

      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col xs={24} lg={14}>
          <Card title="补弱优先队列" extra={<Button type="link" size="small" onClick={() => navigate("/study", { state: { tab: "practice" } })}>去刷题</Button>}>
            {weakChapters.length === 0 ? (
              <Empty description="所有章节掌握良好！" image={Empty.PRESENTED_IMAGE_SIMPLE} />
            ) : (
              weakChapters.map((ch, idx) => (
                <div key={ch.id} style={{ marginBottom: 16 }}>
                  <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 6 }}>
                    <span>
                      <Tag color={idx === 0 ? "red" : "orange"}>#{idx + 1}</Tag>
                      <Tag color={partColors[ch.part]}>{ch.part === "C_programming" ? "C" : "DS"}</Tag>
                      [{ch.chapter}] {ch.name}
                    </span>
                    <Tag color={examWeightColors[ch.exam_weight] || "default"}>{ch.exam_weight}</Tag>
                  </div>
                  <Progress percent={Math.round(ch.mastery_level)} size="small" strokeColor={getMasteryColor(ch.mastery_level)} />
                </div>
              ))
            )}
          </Card>
        </Col>
        <Col xs={24} lg={10}>
          <Card>
            <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 16 }}>
              <FireOutlined style={{ color: "#F59E0B" }} />
              <span style={{ fontWeight: 600 }}>今日行动建议</span>
            </div>
            <Space direction="vertical" size={12} style={{ width: "100%" }}>
              <div style={{ padding: 12, border: "1px solid #E2E8F0", borderRadius: 10, background: "#F8FAFC", fontSize: 13, lineHeight: 1.7 }}>
                <ScheduleOutlined style={{ marginRight: 8, color: "#6366F1" }} />
                完成到期复习知识点，清空今日记忆队列，再开始新题练习。
              </div>
              <div style={{ padding: 12, border: "1px solid #E2E8F0", borderRadius: 10, background: "#F8FAFC", fontSize: 13, lineHeight: 1.7 }}>
                今日目标 {overview.daily_target} 题 · 已完成 {overview.today_attempts} 题
              </div>
            </Space>
            <div style={{ marginTop: 12 }}>
              <Button type="primary" block icon={<FireOutlined />} onClick={() => navigate("/study", { state: { tab: "practice" } })}>
                开始刷题
              </Button>
            </div>
          </Card>
        </Col>
      </Row>

      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col xs={24} md={12}>
          <Card title={<span><CodeOutlined /> C语言程序设计</span>}>
            <Row gutter={16}>
              <Col span={12}><Statistic title="刷题数" value={overview.c_attempts} prefix={<BookOutlined />} /></Col>
              <Col span={12}><Statistic title="正确率" value={overview.c_accuracy} precision={1} suffix="%" prefix={<CheckCircleOutlined />} /></Col>
            </Row>
            <div style={{ marginTop: 16 }}>
              <div style={{ marginBottom: 4, color: "#64748B" }}>平均掌握度</div>
              <Progress percent={cAvgMastery} strokeColor="#6366F1" format={() => `${cAvgMastery}%`} />
            </div>
          </Card>
        </Col>
        <Col xs={24} md={12}>
          <Card title={<span><RadarChartOutlined /> 数据结构</span>}>
            <Row gutter={16}>
              <Col span={12}><Statistic title="刷题数" value={overview.ds_attempts} prefix={<BookOutlined />} /></Col>
              <Col span={12}><Statistic title="正确率" value={overview.ds_accuracy} precision={1} suffix="%" prefix={<CheckCircleOutlined />} /></Col>
            </Row>
            <div style={{ marginTop: 16 }}>
              <div style={{ marginBottom: 4, color: "#64748B" }}>平均掌握度</div>
              <Progress percent={dsAvgMastery} strokeColor="#10B981" format={() => `${dsAvgMastery}%`} />
            </div>
          </Card>
        </Col>
      </Row>

      <Card>
        <Tabs
          defaultActiveKey="radar"
          items={[
            {
              key: "radar",
              label: <span><RadarChartOutlined /> 章节掌握雷达图</span>,
              children: cRadarData.length > 0 || dsRadarData.length > 0 ? (
                <Row gutter={[16, 16]}>
                  <Col xs={24} xl={12}>
                    <SubjectRadarCard title="C语言程序设计" color={partColors.C_programming} icon={<CodeOutlined />} data={cRadarData} />
                  </Col>
                  <Col xs={24} xl={12}>
                    <SubjectRadarCard title="数据结构" color={partColors.data_structure} icon={<RadarChartOutlined />} data={dsRadarData} />
                  </Col>
                </Row>
              ) : (
                <Empty description="暂无章节掌握数据" />
              ),
            },
            {
              key: "detail",
              label: <span><RiseOutlined /> 章节掌握度详情</span>,
              children: (
                <Collapse
                  size="small"
                  items={[
                    {
                      key: "C_programming",
                      label: <span><CodeOutlined /> C语言程序设计 ({cChapters.length} 个知识点)</span>,
                      children: <Table dataSource={cChapters} columns={chapterColumns} rowKey="id" pagination={false} size="small" />,
                    },
                    {
                      key: "data_structure",
                      label: <span><RadarChartOutlined /> 数据结构 ({dsChapters.length} 个知识点)</span>,
                      children: <Table dataSource={dsChapters} columns={chapterColumns} rowKey="id" pagination={false} size="small" />,
                    },
                  ]}
                  defaultActiveKey={["C_programming", "data_structure"]}
                />
              ),
            },
          ]}
        />
      </Card>
    </div>
  );
};

export default ProgressPage;
