import React, { useState, useEffect } from 'react';
import { Card, List, Button, Tag, Space, Spin, Result, Progress, Rate, message, Statistic, Row, Col } from 'antd';
import { ScheduleOutlined, BookOutlined, CheckCircleOutlined } from '@ant-design/icons';
import api from '../../services/api';

interface ReviewItem {
  mastery_id: number;
  knowledge_point_id: number;
  name: string;
  chapter: string;
  part: string;
  mastery_level: number;
  ease_factor: number;
  interval_days: number;
  repetitions: number;
  next_review_at: string | null;
  sample_question: { id: number; content: string; type: string } | null;
}

interface ReviewStats {
  total_knowledge_points: number;
  average_mastery: number;
  due_now: number;
  due_this_week: number;
  message: string;
}

const ReviewPlan: React.FC = () => {
  const [items, setItems] = useState<ReviewItem[]>([]);
  const [stats, setStats] = useState<ReviewStats | null>(null);
  const [loading, setLoading] = useState(false);
  const [reviewing, setReviewing] = useState<number | null>(null);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [dueRes, statsRes] = await Promise.all([
        api.get('/review/due'),
        api.get('/review/stats'),
      ]);
      setItems(dueRes.data.items || []);
      setStats(statsRes.data);
    } catch (e) { /* handled by interceptor */ }
    finally { setLoading(false); }
  };

  useEffect(() => { fetchData(); }, []);

  const handleReview = async (masteryId: number, quality: number) => {
    setReviewing(masteryId);
    try {
      await api.post(`/review/${masteryId}/review`, null, { params: { quality } });
      message.success('复习记录已更新！');
      fetchData();
    } catch (e) { /* handled by interceptor */ }
    finally { setReviewing(null); }
  };

  if (loading) return <Spin size="large" style={{ display: 'block', margin: '100px auto' }} />;

  if (!stats) return null;

  return (
    <div>
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}><Card><Statistic title="知识点总数" value={stats.total_knowledge_points} prefix={<BookOutlined />} /></Card></Col>
        <Col span={6}><Card><Statistic title="平均掌握度" value={`${stats.average_mastery}%`} /></Card></Col>
        <Col span={6}><Card><Statistic title="今日待复习" value={stats.due_now} styles={{ content: { color: stats.due_now > 0 ? '#C56C6C' : '#3D8B5E' } }} /></Card></Col>
        <Col span={6}><Card><Statistic title="本周待复习" value={stats.due_this_week} /></Card></Col>
      </Row>

      <Card title={<span><ScheduleOutlined /> 待复习知识点</span>}
        extra={<Button onClick={fetchData} loading={loading}>刷新</Button>}>
        {items.length === 0 ? (
          <Result icon={<CheckCircleOutlined style={{ color: '#3D8B5E' }} />}
            title="暂无到期复习任务"
            subTitle="你已掌握所有知识点，继续保持！" />
        ) : (
          <List
            dataSource={items}
            renderItem={(item) => (
              <List.Item
                key={item.mastery_id}
                extra={
                  <Space orientation="vertical">
                    <div style={{ fontSize: 12, color: '#9B9590' }}>
                      间隔: {item.interval_days}天 | 重复: {item.repetitions}次
                    </div>
                    <Rate
                      count={5}
                      value={Math.round(item.mastery_level / 20)}
                      onChange={(val) => handleReview(item.mastery_id, val)}
                      disabled={reviewing === item.mastery_id}
                    />
                    <span style={{ fontSize: 11, color: '#9B9590' }}>
                      评分: 1=遗忘 3=基本记住 5=轻松掌握
                    </span>
                  </Space>
                }
              >
                <List.Item.Meta
                  title={
                    <Space>
                      <Tag color={item.part === 'C_programming' ? 'blue' : 'green'}>
                        {item.part === 'C_programming' ? 'C语言' : 'DS'}
                      </Tag>
                      {item.name}
                      <Tag>{item.chapter}</Tag>
                    </Space>
                  }
                  description={
                    <div>
                      <Progress percent={item.mastery_level} size="small" />
                      {item.sample_question && (
                        <p style={{ marginTop: 5, color: '#6B6560', fontSize: 13 }}>
                          示例题: {item.sample_question.content}
                        </p>
                      )}
                    </div>
                  }
                />
              </List.Item>
            )}
          />
        )}
      </Card>
    </div>
  );
};

export default ReviewPlan;
