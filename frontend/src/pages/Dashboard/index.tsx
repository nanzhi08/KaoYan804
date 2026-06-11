import React, { useEffect, useState } from 'react';
import { Button, Card, Col, Empty, Progress, Row, Space, Spin, Statistic, Tag } from 'antd';
import {
  BookOutlined,
  CheckCircleOutlined,
  PercentageOutlined,
  ThunderboltOutlined,
  FireOutlined,
  ScheduleOutlined,
  RightOutlined,
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { fetchProgressOverview, fetchProgressDetail } from '../../services/progressApi';
import type { ProgressOverview, ChapterProgress } from '../../types';

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
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

  const weakChapters = chapters
    .slice()
    .sort((a, b) => a.mastery_level - b.mastery_level)
    .slice(0, 4);
  const nextReviewCount = overview?.due_review_count
    ?? chapters.filter((ch) => !ch.next_review_at || new Date(ch.next_review_at) <= new Date()).length;
  const accuracy = overview?.accuracy ?? 0;
  const todayAttempts = overview?.today_attempts ?? 0;
  const dailyTarget = overview?.daily_target ?? 10;
  const targetProgress = Math.min(100, Math.round((todayAttempts / dailyTarget) * 100));
  const startKnowledgePointPractice = (ch: ChapterProgress) => {
    navigate('/practice', {
      state: {
        knowledgePoint: { id: ch.id, part: ch.part, chapter: ch.chapter, name: ch.name },
        knowledgePointIds: [ch.id],
      },
    });
  };

  return (
    <div className="dashboard-command">
      {/* Hero Welcome Section */}
      <div style={{
        marginBottom: 24,
        padding: '32px',
        background: 'linear-gradient(135deg, #0F172A 0%, #1E293B 54%, #064E3B 100%)',
        borderRadius: 16,
        color: '#fff',
        position: 'relative',
        overflow: 'hidden',
      }}>
        <div style={{
          position: 'absolute',
          top: 0, right: 0, bottom: 0,
          width: '38%',
          background: 'repeating-linear-gradient(135deg, rgba(255,255,255,0.08) 0 1px, transparent 1px 14px)',
          pointerEvents: 'none',
        }} />
        <Row gutter={[24, 18]} align="middle" style={{ position: 'relative' }}>
          <Col xs={24} lg={15}>
            <Tag color={accuracy >= 70 ? 'success' : accuracy >= 45 ? 'warning' : 'error'} style={{ marginBottom: 12 }}>
              {accuracy >= 70 ? '稳定保持' : accuracy >= 45 ? '需要巩固' : '优先补弱'}
            </Tag>
            <h2 style={{ fontSize: 26, fontWeight: 700, margin: '0 0 8px 0' }}>
              今日学习指挥台
            </h2>
            <p style={{ fontSize: 14, opacity: 0.86, margin: '0 0 18px 0', maxWidth: 560 }}>
              先复习到期知识点，再用章节刷题补最弱环节，把练习记录转成可记住的知识点。
            </p>
            <Space wrap>
              <Button type="primary" icon={<FireOutlined />} onClick={() => navigate('/study', { state: { tab: 'practice' } })}>
                开始刷题
              </Button>
              <Button icon={<ScheduleOutlined />} onClick={() => navigate('/review', { state: { tab: 'plan' } })}>
                查看复习计划
              </Button>
              <Button icon={<RightOutlined />} onClick={() => navigate('/review', { state: { tab: 'stats' } })}>
                定位薄弱章节
              </Button>
            </Space>
          </Col>
          <Col xs={24} lg={9}>
            <div style={{
              background: 'rgba(255,255,255,0.08)',
              border: '1px solid rgba(255,255,255,0.16)',
              borderRadius: 12,
              padding: 16,
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 10 }}>
                <span style={{ opacity: 0.78 }}>今日刷题目标</span>
                <strong>{todayAttempts}/{dailyTarget}</strong>
              </div>
              <Progress percent={targetProgress} showInfo={false} strokeColor="#34D399" railColor="rgba(255,255,255,0.18)" />
              <div style={{ marginTop: 12, color: 'rgba(255,255,255,0.78)', fontSize: 13 }}>
                待复习知识点：{nextReviewCount} 个 · 优先章节：{weakChapters[0]?.chapter || '暂无'}
              </div>
              <div style={{ marginTop: 8, color: 'rgba(255,255,255,0.68)', fontSize: 12, lineHeight: 1.6 }}>
                今日已完成来自今日 0 点后的练习记录；目标 = 基础 10 题 + 到期复习和薄弱知识点加权，最高 30 题。
              </div>
            </div>
          </Col>
        </Row>
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

      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col xs={24} xl={10}>
          <Card title="优先补弱章节" extra={<Button type="link" onClick={() => navigate('/review', { state: { tab: 'stats' } })}>查看全部</Button>}>
            {weakChapters.length === 0 ? (
              <Empty description="暂无练习数据，先完成一组章节题" />
            ) : (
              <Space orientation="vertical" size={12} style={{ width: '100%' }}>
                {weakChapters.map((ch, index) => (
                  <div key={ch.id} style={{ padding: 12, border: '1px solid #E2E8F0', borderRadius: 10 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', gap: 12, marginBottom: 8 }}>
                      <Space size={8}>
                        <Tag color={index === 0 ? 'red' : 'orange'}>#{index + 1}</Tag>
                        <strong>{ch.chapter} {ch.name}</strong>
                      </Space>
                      <span style={{ color: '#64748B' }}>{Math.round(ch.mastery_level)}%</span>
                    </div>
                    <Progress
                      percent={Math.round(ch.mastery_level)}
                      size="small"
                      strokeColor={ch.mastery_level >= 70 ? '#10B981' : ch.mastery_level >= 40 ? '#F59E0B' : '#EF4444'}
                    />
                    <Button
                      type="link"
                      size="small"
                      style={{ padding: 0, marginTop: 6 }}
                      onClick={() => startKnowledgePointPractice(ch)}
                    >
                      刷这个知识点
                    </Button>
                  </div>
                ))}
              </Space>
            )}
          </Card>
        </Col>
        <Col xs={24} xl={14}>
          <Card title="章节掌握度快览" extra={<Button type="link" onClick={() => navigate('/study', { state: { tab: 'practice' } })}>去刷题</Button>}>
            {chapters.length === 0 ? (
              <Empty description="暂无练习数据，去刷题吧！" />
            ) : (
              chapters.slice(0, 8).map((ch) => (
                <div key={ch.id} style={{ marginBottom: 16 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4, gap: 12 }}>
                    <span>
                      <span style={{ marginRight: 8, color: '#94A3B8' }}>[{ch.chapter}]</span>
                      {ch.name}
                      <Tag color={ch.exam_weight === '高频' ? 'red' : 'orange'} style={{ marginLeft: 8 }}>
                        {ch.exam_weight}
                      </Tag>
                    </span>
                    <span>{Math.round(ch.mastery_level)}%</span>
                  </div>
                  <Progress
                    percent={Math.round(ch.mastery_level)}
                    strokeColor={
                      ch.mastery_level >= 70 ? '#10B981' : ch.mastery_level >= 40 ? '#6366F1' : '#F59E0B'
                    }
                    size="small"
                  />
                </div>
              ))
            )}
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Dashboard;
