import React, { useEffect, useState } from 'react';
import { Card, Row, Col, Statistic, Progress, Spin, Empty } from 'antd';
import {
  BookOutlined,
  CheckCircleOutlined,
  PercentageOutlined,
  ThunderboltOutlined,
} from '@ant-design/icons';
import { fetchProgressOverview, fetchProgressDetail } from '../../services/progressApi';
import type { ProgressOverview, ChapterProgress } from '../../types';

const Dashboard: React.FC = () => {
  const [overview, setOverview] = useState<ProgressOverview | null>(null);
  const [chapters, setChapters] = useState<ChapterProgress[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([fetchProgressOverview(), fetchProgressDetail()])
      .then(([ov, ch]) => {
        setOverview(ov);
        setChapters(ch);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <Spin size="large" style={{ display: 'block', margin: '100px auto' }} />;

  return (
    <div>
      {/* Hero Welcome Section */}
      <div style={{
        marginBottom: 24,
        padding: '36px 32px',
        background: 'linear-gradient(135deg, #6366F1 0%, #818CF8 50%, #A78BFA 100%)',
        borderRadius: 20,
        color: '#fff',
        position: 'relative',
        overflow: 'hidden',
      }}>
        <div style={{
          position: 'absolute',
          top: 0, right: 0, bottom: 0,
          width: '45%',
          background: 'radial-gradient(circle at 70% 30%, rgba(255,255,255,0.12) 0%, transparent 60%)',
          pointerEvents: 'none',
        }} />
        <h2 style={{ fontSize: 24, fontWeight: 700, margin: '0 0 8px 0', position: 'relative' }}>
          学习仪表盘
        </h2>
        <p style={{ fontSize: 14, opacity: 0.85, margin: 0, position: 'relative' }}>
          跟踪你的学习进度，高效备战 804 考研
        </p>
      </div>

      <Row gutter={[16, 16]} className="stagger-children">
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic title="总练习次数" value={overview?.total_attempts ?? 0} prefix={<BookOutlined />} />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic title="正确次数" value={overview?.total_correct ?? 0} prefix={<CheckCircleOutlined />} styles={{ content: { color: '#10B981' } }} />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic title="正确率" value={overview?.accuracy ?? 0} suffix="%" prefix={<PercentageOutlined />} styles={{ content: { color: '#EF4444' } }} />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic title="知识点章节" value={chapters.length} prefix={<ThunderboltOutlined />} />
          </Card>
        </Col>
      </Row>

      <Card title="各章节掌握度" style={{ marginTop: 16 }}>
        {chapters.length === 0 ? (
          <Empty description="暂无练习数据，去刷题吧！" />
        ) : (
          chapters.map((ch) => (
            <div key={ch.id} style={{ marginBottom: 16 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                <span>
                  <span style={{ marginRight: 8, color: '#94A3B8' }}>[{ch.chapter}]</span>
                  {ch.name}
                  <span style={{
                    marginLeft: 8,
                    fontSize: 12,
                    color: ch.exam_weight === '高频' ? '#EF4444' : '#F59E0B',
                  }}>
                    {ch.exam_weight}
                  </span>
                </span>
                <span>{Math.round(ch.mastery_level * 100)}%</span>
              </div>
              <Progress
                percent={Math.round(ch.mastery_level * 100)}
                strokeColor={
                  ch.mastery_level >= 0.7 ? '#10B981' : ch.mastery_level >= 0.4 ? '#6366F1' : '#F59E0B'
                }
                size="small"
              />
            </div>
          ))
        )}
      </Card>
    </div>
  );
};

export default Dashboard;
