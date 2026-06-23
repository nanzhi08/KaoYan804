import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Alert,
  Button,
  Card,
  Col,
  Descriptions,
  Empty,
  Modal,
  Row,
  Space,
  Spin,
  Statistic,
  Table,
  Tag,
  message,
} from 'antd';
import {
  EyeOutlined,
  ReloadOutlined,
  FireOutlined,
  HistoryOutlined,
} from '@ant-design/icons';

import { usePracticeStore } from '../../stores/usePracticeStore';
import { QuestionTypeLabel } from '../../types';
import type { PracticeRecord, Question, QuestionType } from '../../types';
import {
  fetchPracticeHistory,
  fetchQuestion,
  fetchWrongQuestions,
} from '../../services/questionApi';

const REFRESH_INTERVAL_MS = 60 * 1000;

const WrongRecords: React.FC = () => {
  const navigate = useNavigate();
  const { setQuestions, reset } = usePracticeStore();
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [lastUpdatedAt, setLastUpdatedAt] = useState<string>('');
  const [wrongRecords, setWrongRecords] = useState<PracticeRecord[]>([]);
  const [pendingWrongQuestions, setPendingWrongQuestions] = useState<Question[]>([]);
  const [selectedQuestion, setSelectedQuestion] = useState<Question | null>(null);
  const [selectedRecord, setSelectedRecord] = useState<PracticeRecord | null>(null);
  const [detailOpen, setDetailOpen] = useState(false);
  const [detailLoading, setDetailLoading] = useState(false);

  const loadData = useCallback(async (silent = false) => {
    if (silent) {
      setRefreshing(true);
    } else {
      setLoading(true);
    }

    try {
      const [history, wrongQuestions] = await Promise.all([
        fetchPracticeHistory({ page: 1, page_size: 100 }),
        fetchWrongQuestions(50),
      ]);
      setWrongRecords((history.items || []).filter((record) => !record.is_correct));
      setPendingWrongQuestions(wrongQuestions);
      setLastUpdatedAt(new Date().toLocaleTimeString('zh-CN', { hour12: false }));
    } catch {
      message.error('错题数据加载失败');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    queueMicrotask(() => {
      void loadData();
    });
  }, [loadData]);

  useEffect(() => {
    const timer = window.setInterval(() => {
      loadData(true);
    }, REFRESH_INTERVAL_MS);

    return () => window.clearInterval(timer);
  }, [loadData]);

  const uniqueWrongQuestionCount = useMemo(
    () => new Set(wrongRecords.map((record) => record.question_id)).size,
    [wrongRecords],
  );

  const handleStartWrongPractice = useCallback(() => {
    if (pendingWrongQuestions.length === 0) {
      message.info('当前没有待复习错题');
      return;
    }

    reset();
    setQuestions(pendingWrongQuestions);
    navigate('/study', { state: { tab: 'practice', autoStart: true, mode: 'wrong' } });
  }, [navigate, pendingWrongQuestions, reset, setQuestions]);

  const handleOpenDetail = useCallback(async (record: PracticeRecord) => {
    setSelectedRecord(record);
    setDetailOpen(true);
    setDetailLoading(true);
    setSelectedQuestion(null);

    try {
      const question = await fetchQuestion(record.question_id);
      setSelectedQuestion(question);
    } catch {
      message.error('错题讲解加载失败');
    } finally {
      setDetailLoading(false);
    }
  }, []);

  if (loading) {
    return <Spin size="large" style={{ display: 'block', margin: '80px auto' }} />;
  }

  return (
    <div>
      <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
        <Col xs={24} md={8}>
          <Card>
            <Statistic title="待复习错题" value={pendingWrongQuestions.length} />
          </Card>
        </Col>
        <Col xs={24} md={8}>
          <Card>
            <Statistic title="错题记录数" value={wrongRecords.length} />
          </Card>
        </Col>
        <Col xs={24} md={8}>
          <Card>
            <Statistic title="涉及题目数" value={uniqueWrongQuestionCount} />
          </Card>
        </Col>
      </Row>

      <Card
        title={<span><HistoryOutlined style={{ marginRight: 8 }} />错题记录</span>}
        extra={(
          <Space>
            <Button
              icon={<ReloadOutlined />}
              loading={refreshing}
              onClick={() => loadData(true)}
            >
              立即刷新
            </Button>
            <Button
              type="primary"
              icon={<FireOutlined />}
              onClick={handleStartWrongPractice}
            >
              复习错题
            </Button>
          </Space>
        )}
      >
        <Alert
          type="info"
          showIcon
          style={{ marginBottom: 16 }}
          title={`错题数据每 1 分钟自动刷新一次，最近刷新时间：${lastUpdatedAt || '刚刚'}`}
        />

        {wrongRecords.length === 0 ? (
          <Empty description="暂无错题记录，继续保持" />
        ) : (
          <Table
            dataSource={wrongRecords}
            rowKey="id"
            size="middle"
            pagination={{ pageSize: 10, showSizeChanger: false }}
            columns={[
              {
                title: '记录时间',
                dataIndex: 'created_at',
                width: 180,
                render: (value: string) => value?.replace('T', ' ').substring(0, 19),
              },
              {
                title: '题目',
                dataIndex: 'question_content',
                ellipsis: true,
              },
              {
                title: '题型',
                dataIndex: 'question_type',
                width: 110,
                render: (value: string) => <Tag>{QuestionTypeLabel[value as QuestionType] || value}</Tag>,
              },
              {
                title: '你的答案',
                dataIndex: 'user_answer',
                width: 160,
                ellipsis: true,
              },
              {
                title: '正确答案',
                dataIndex: 'correct_answer',
                width: 160,
                ellipsis: true,
              },
              {
                title: '操作',
                key: 'action',
                width: 120,
                render: (_, record: PracticeRecord) => (
                  <Button type="link" icon={<EyeOutlined />} onClick={() => handleOpenDetail(record)}>
                    查看讲解
                  </Button>
                ),
              },
            ]}
          />
        )}
      </Card>

      <Modal
        title="错题讲解"
        open={detailOpen}
        onCancel={() => {
          setDetailOpen(false);
          setSelectedQuestion(null);
          setSelectedRecord(null);
        }}
        footer={null}
        width={860}
      >
        {detailLoading ? (
          <Spin size="large" style={{ display: 'block', margin: '60px auto' }} />
        ) : selectedQuestion && selectedRecord ? (
          <Space orientation="vertical" size="large" style={{ width: '100%' }}>
            <Descriptions bordered column={1} size="small">
              <Descriptions.Item label="题型">
                <Tag>{QuestionTypeLabel[selectedQuestion.type] || selectedQuestion.type}</Tag>
              </Descriptions.Item>
              <Descriptions.Item label="题目">
                <div style={{ whiteSpace: 'pre-wrap', lineHeight: 1.8 }}>{selectedQuestion.content}</div>
              </Descriptions.Item>
              {selectedQuestion.code_snippet && (
                <Descriptions.Item label="代码片段">
                  <pre style={{ margin: 0, background: '#F8FAFC', padding: 12, borderRadius: 8, overflow: 'auto' }}>
                    <code>{selectedQuestion.code_snippet}</code>
                  </pre>
                </Descriptions.Item>
              )}
              {selectedQuestion.options && (
                <Descriptions.Item label="选项">
                  <Space orientation="vertical" size="small" style={{ width: '100%' }}>
                    {Object.entries(selectedQuestion.options).map(([key, value]) => (
                      <div key={key}>
                        <strong>{key}.</strong> {value}
                      </div>
                    ))}
                  </Space>
                </Descriptions.Item>
              )}
              <Descriptions.Item label="你的答案">
                <Tag color="error">{selectedRecord.user_answer || '未作答'}</Tag>
              </Descriptions.Item>
              <Descriptions.Item label="正确答案">
                <Tag color="success">{selectedQuestion.answer}</Tag>
              </Descriptions.Item>
              <Descriptions.Item label="错题讲解">
                <div style={{ whiteSpace: 'pre-wrap', lineHeight: 1.8 }}>
                  {selectedQuestion.explanation || '暂无讲解'}
                </div>
              </Descriptions.Item>
            </Descriptions>
          </Space>
        ) : (
          <Empty description="暂无讲解数据" />
        )}
      </Modal>
    </div>
  );
};

export default WrongRecords;
