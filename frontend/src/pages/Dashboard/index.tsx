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
      .catch(() => {}) // handled by api interceptor
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <Spin size="large" style={{ display: 'block', margin: '100px auto' }} />;

  return (
    <div>
      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic title="总练习次数" value={overview?.total_attempts ?? 0} prefix={<BookOutlined />} />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic title="正确次数" value={overview?.total_correct ?? 0} prefix={<CheckCircleOutlined />} styles={{ content: { color: '#3D8B5E' } }} />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic title="正确率" value={overview?.accuracy ?? 0} suffix="%" prefix={<PercentageOutlined />} styles={{ content: { color: '#C56C6C' } }} />
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
                  <span style={{ marginRight: 8, color: '#9B9590' }}>[{ch.chapter}]</span>
                  {ch.name}
                  <span style={{
                    marginLeft: 8,
                    fontSize: 12,
                    color: ch.exam_weight === '高频' ? '#C56C6C' : '#D4953A',
                  }}>
                    {ch.exam_weight}
                  </span>
                </span>
                <span>{Math.round(ch.mastery_level * 100)}%</span>
              </div>
              <Progress
                percent={Math.round(ch.mastery_level * 100)}
                strokeColor={
                  ch.mastery_level >= 0.7 ? '#3D8B5E' : ch.mastery_level >= 0.4 ? '#4A5BC9' : '#D4953A'
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
