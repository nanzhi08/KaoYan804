import React, { useEffect, useState } from 'react';
import { Card, Row, Col, Statistic, Spin, Empty, Progress, Tabs, Table, Tag, Collapse, Space } from 'antd';
import {
  BookOutlined, TrophyOutlined, CodeOutlined, RadarChartOutlined,
  RiseOutlined, CheckCircleOutlined,
} from '@ant-design/icons';
import { fetchProgressDetail, fetchProgressOverview } from '../../services/progressApi';
import type { ChapterProgress, ProgressOverview } from '../../types';
import {
  RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar,
  ResponsiveContainer, Tooltip,
} from 'recharts';

const partColors: Record<string, string> = {
  C_programming: '#6366F1',
  data_structure: '#10B981',
};

const examWeightColors: Record<string, string> = {
  '高频': '#EF4444',
  '中频': '#F59E0B',
  '低频': '#6366F1',
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
  value >= 70 ? '#10B981' : value >= 40 ? '#F59E0B' : '#EF4444'
);

const getMasteryLabel = (value: number) => (
  value >= 70 ? '掌握较好' : value >= 40 ? '需要巩固' : '重点补强'
);

const buildChapterRadarData = (items: ChapterProgress[]): ChapterRadarDatum[] => {
  const chapterMap = new Map<string, {
    chapter: string;
    part: string;
    masterySum: number;
    attemptsSum: number;
    pointCount: number;
  }>();

  items.forEach((item) => {
    const chapter = item.chapter || '未分类';
    const key = `${item.part}::${chapter}`;
    const current = chapterMap.get(key) ?? {
      chapter,
      part: item.part,
      masterySum: 0,
      attemptsSum: 0,
      pointCount: 0,
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
  title: string;
  color: string;
  icon: React.ReactNode;
  data: ChapterRadarDatum[];
}> = ({ title, color, icon, data }) => {
  const strongest = data.reduce<ChapterRadarDatum | null>(
    (best, item) => (!best || item.mastery > best.mastery ? item : best),
    null,
  );
  const weakest = data.reduce<ChapterRadarDatum | null>(
    (worst, item) => (!worst || item.mastery < worst.mastery ? item : worst),
    null,
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
                <Statistic
                  title="平均掌握度"
                  value={averageMastery}
                  suffix="%"
                  styles={{ content: { color } }}
                />
              </Card>
            </Col>
            <Col span={8}>
              <Card size="small">
                <div style={{ color: '#64748B', fontSize: 12, marginBottom: 6 }}>当前最弱章节</div>
                <div style={{ fontWeight: 600, marginBottom: 4 }}>{weakest?.chapter || '-'}</div>
                <Tag color={getMasteryColor(weakest?.mastery ?? 0)}>
                  {weakest?.mastery ?? 0}% · {getMasteryLabel(weakest?.mastery ?? 0)}
                </Tag>
              </Card>
            </Col>
          </Row>

          <div style={{ height: 320 }}>
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart data={data} outerRadius="68%">
                <PolarGrid gridType="polygon" />
                <PolarAngleAxis dataKey="axis" fontSize={12} />
                <PolarRadiusAxis domain={[0, 100]} tickCount={6} tickFormatter={(value) => `${value}%`} />
                <Tooltip
                  formatter={(value) => [`${value ?? 0}%`, '章节掌握度']}
                  labelFormatter={(label, payload) => {
                    const item = payload?.[0]?.payload as ChapterRadarDatum | undefined;
                    if (!item) return label;
                    return `${item.chapter} · ${item.pointCount} 个知识点 · ${item.totalAttempts} 次练习`;
                  }}
                />
                <Radar
                  name="章节掌握度"
                  dataKey="mastery"
                  stroke={color}
                  fill={color}
                  fillOpacity={0.28}
                  dot={{ r: 4, fill: color }}
                />
              </RadarChart>
            </ResponsiveContainer>
          </div>

          <div style={{ marginTop: 8 }}>
            <div style={{ fontWeight: 600, marginBottom: 12 }}>章节进度一览</div>
            <Space orientation="vertical" size="middle" style={{ width: '100%' }}>
              {data
                .slice()
                .sort((a, b) => b.mastery - a.mastery)
                .map((item) => (
                  <div key={item.chapter}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
                      <span>{item.chapter}</span>
                      <span style={{ color: '#64748B' }}>
                        {item.mastery}% · {item.pointCount} 个知识点 · {item.totalAttempts} 次练习
                      </span>
                    </div>
                    <Progress
                      percent={item.mastery}
                      strokeColor={getMasteryColor(item.mastery)}
                      format={() => getMasteryLabel(item.mastery)}
                    />
                  </div>
                ))}
            </Space>
          </div>

          {strongest && (
            <div style={{ marginTop: 12 }}>
              <Tag color="success">
                最强章节：{strongest.chapter} {strongest.mastery}%
              </Tag>
            </div>
          )}
        </>
      )}
    </Card>
  );
};

const ProgressPage: React.FC = () => {
  const [overview, setOverview] = useState<ProgressOverview | null>(null);
  const [chapters, setChapters] = useState<ChapterProgress[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([fetchProgressOverview(), fetchProgressDetail()])
      .then(([ov, ch]) => { setOverview(ov); setChapters(ch); })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <Spin size="large" style={{ display: 'block', margin: '100px auto' }} />;

  if (!overview || overview.total_attempts === 0) {
    return (
      <Card title="学习统计">
        <Empty description="还没有刷题记录，先去刷题吧" image={Empty.PRESENTED_IMAGE_SIMPLE} />
      </Card>
    );
  }

  const cChapters = chapters.filter((ch) => ch.part === 'C_programming');
  const dsChapters = chapters.filter((ch) => ch.part === 'data_structure');
  const cRadarData = buildChapterRadarData(cChapters);
  const dsRadarData = buildChapterRadarData(dsChapters);

  const cAvgMastery = cChapters.length > 0
    ? Math.round(cChapters.reduce((s, c) => s + c.mastery_level, 0) / cChapters.length)
    : 0;
  const dsAvgMastery = dsChapters.length > 0
    ? Math.round(dsChapters.reduce((s, c) => s + c.mastery_level, 0) / dsChapters.length)
    : 0;

  const chapterColumns = [
    { title: '章节', dataIndex: 'chapter', key: 'chapter', width: 80 },
    { title: '知识点', dataIndex: 'name', key: 'name' },
    {
      title: '考频', dataIndex: 'exam_weight', key: 'exam_weight', width: 70,
      render: (w: string) => <Tag color={examWeightColors[w] || '#888'}>{w}</Tag>,
    },
    {
      title: '掌握度', dataIndex: 'mastery_level', key: 'mastery', width: 200,
      render: (v: number) => (
        <Progress
          percent={v} size="small"
          strokeColor={v >= 70 ? '#10B981' : v >= 40 ? '#F59E0B' : '#EF4444'}
          format={() => `${v}%`}
        />
      ),
    },
    { title: '练习次数', dataIndex: 'total_attempts', key: 'attempts', width: 80 },
    {
      title: '下次复习', dataIndex: 'next_review_at', key: 'review', width: 140,
      render: (v: string | null) => v
        ? new Date(v).toLocaleDateString('zh-CN')
        : <Tag color="orange">待复习</Tag>,
    },
  ];

  return (
    <div style={{ maxWidth: 1200 }}>
      {/* 概览统计卡片 */}
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col xs={12} sm={6}>
          <Card>
            <Statistic
              title="总刷题数"
              value={overview.total_attempts}
              prefix={<BookOutlined />}
              suffix={`正确 ${overview.total_correct} 题`}
            />
          </Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card>
            <Statistic
              title="总体正确率"
              value={overview.accuracy}
              precision={1}
              prefix={<TrophyOutlined />}
              suffix="%"
              styles={{ content: { color: overview.accuracy >= 60 ? '#10B981' : '#EF4444' } }}
            />
          </Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card>
            <Statistic
              title="C语言正确率"
              value={overview.c_accuracy}
              precision={1}
              prefix={<CodeOutlined />}
              suffix="%"
              styles={{ content: { color: overview.c_accuracy >= 60 ? '#6366F1' : '#EF4444' } }}
            />
          </Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card>
            <Statistic
              title="数据结构正确率"
              value={overview.ds_accuracy}
              precision={1}
              prefix={<RadarChartOutlined />}
              suffix="%"
              styles={{ content: { color: overview.ds_accuracy >= 60 ? '#10B981' : '#EF4444' } }}
            />
          </Card>
        </Col>
      </Row>

      {/* 两科目对比 */}
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col xs={24} md={12}>
          <Card title={<span><CodeOutlined /> C语言程序设计</span>}>
            <Row gutter={16}>
              <Col span={12}>
                <Statistic title="刷题数" value={overview.c_attempts} prefix={<BookOutlined />} />
              </Col>
              <Col span={12}>
                <Statistic
                  title="正确率"
                  value={overview.c_accuracy}
                  precision={1}
                  suffix="%"
                  prefix={<CheckCircleOutlined />}
                />
              </Col>
            </Row>
            <div style={{ marginTop: 16 }}>
              <div style={{ marginBottom: 4, color: '#64748B' }}>平均掌握度</div>
              <Progress
                percent={cAvgMastery}
                strokeColor="#6366F1"
                format={() => `${cAvgMastery}%`}
              />
            </div>
          </Card>
        </Col>
        <Col xs={24} md={12}>
          <Card title={<span><RadarChartOutlined /> 数据结构</span>}>
            <Row gutter={16}>
              <Col span={12}>
                <Statistic title="刷题数" value={overview.ds_attempts} prefix={<BookOutlined />} />
              </Col>
              <Col span={12}>
                <Statistic
                  title="正确率"
                  value={overview.ds_accuracy}
                  precision={1}
                  suffix="%"
                  prefix={<CheckCircleOutlined />}
                />
              </Col>
            </Row>
            <div style={{ marginTop: 16 }}>
              <div style={{ marginBottom: 4, color: '#64748B' }}>平均掌握度</div>
              <Progress
                percent={dsAvgMastery}
                strokeColor="#10B981"
                format={() => `${dsAvgMastery}%`}
              />
            </div>
          </Card>
        </Col>
      </Row>

      {/* 可视化 Tabs */}
      <Card>
        <Tabs
          defaultActiveKey="radar"
          items={[
            {
              key: 'radar',
              label: <span><RadarChartOutlined /> 章节掌握雷达图</span>,
              children: cRadarData.length > 0 || dsRadarData.length > 0 ? (
                <Row gutter={[16, 16]}>
                  <Col xs={24} xl={12}>
                    <SubjectRadarCard
                      title="C语言程序设计"
                      color={partColors.C_programming}
                      icon={<CodeOutlined />}
                      data={cRadarData}
                    />
                  </Col>
                  <Col xs={24} xl={12}>
                    <SubjectRadarCard
                      title="数据结构"
                      color={partColors.data_structure}
                      icon={<RadarChartOutlined />}
                      data={dsRadarData}
                    />
                  </Col>
                </Row>
              ) : (
                <Empty description="暂无章节掌握数据" />
              ),
            },
            {
              key: 'detail',
              label: <span><RiseOutlined /> 章节掌握度详情</span>,
              children: (
                <Collapse
                  size="small"
                  items={[
                    {
                      key: 'C_programming',
                      label: <span><CodeOutlined /> C语言程序设计 ({cChapters.length} 个知识点)</span>,
                      children: (
                        <Table
                          dataSource={cChapters}
                          columns={chapterColumns}
                          rowKey="id"
                          pagination={false}
                          size="small"
                        />
                      ),
                    },
                    {
                      key: 'data_structure',
                      label: <span><RadarChartOutlined /> 数据结构 ({dsChapters.length} 个知识点)</span>,
                      children: (
                        <Table
                          dataSource={dsChapters}
                          columns={chapterColumns}
                          rowKey="id"
                          pagination={false}
                          size="small"
                        />
                      ),
                    },
                  ]}
                  defaultActiveKey={['C_programming', 'data_structure']}
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
