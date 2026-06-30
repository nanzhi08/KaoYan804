import React, { useState } from 'react';
import { Card, Button, Result, Space, Tag, Descriptions, Radio, Checkbox, Divider, Input } from 'antd';
import { FormOutlined, CheckOutlined } from '@ant-design/icons';
import api from '../../services/api';

interface ExamQuestion {
  id: number;
  score: number;
  type: string;
  part: string;
  content: string;
  options: Record<string, string> | null;
  code_snippet: string | null;
  answer: string;
}

interface ExamData {
  id: number;
  title: string;
  total_score: number;
  time_limit: number;
  question_count: number;
  questions: ExamQuestion[];
}

const MockExam: React.FC = () => {
  const [exam, setExam] = useState<ExamData | null>(null);
  const [loading, setLoading] = useState(false);
  const [answers, setAnswers] = useState<Record<number, string>>({});
  const [submitted, setSubmitted] = useState(false);
  const [showAnswers, setShowAnswers] = useState(false);
  const [score, setScore] = useState<number | null>(null);
  const [currentIndex, setCurrentIndex] = useState(0);

  const handleGenerate = async () => {
    setLoading(true);
    try {
      const res = await api.post('/exam/generate');
      setExam(res.data);
      setAnswers({});
      setSubmitted(false);
      setShowAnswers(false);
      setScore(null);
      setCurrentIndex(0);
    } catch { /* handled by interceptor */ }
    finally { setLoading(false); }
  };

  const handleSubmit = async () => {
    if (!exam) return;
    setLoading(true);
    try {
      await api.post(`/exam/${exam.id}/start`);
      const submitRes = await api.post(`/exam/${exam.id}/submit`, answers);
      setScore(submitRes.data.score);
      setSubmitted(true);
    } catch { /* handled by interceptor */ }
    finally { setLoading(false); }
  };

  if (!exam) {
    return (
      <Card title={<span><FormOutlined /> 模拟考试</span>}>
        <Result
          icon={<FormOutlined style={{ color: '#6366F1' }} />}
          title="804 全真模拟考试"
          subTitle="按真题比例自动组卷：DS 80分 + C语言 70分 = 150分，限时3小时"
          extra={
            <Button type="primary" size="large" loading={loading} onClick={handleGenerate}>
              生成模拟试卷
            </Button>
          }
        />
      </Card>
    );
  }

  if (submitted && !showAnswers) {
    return (
      <Card title="考试结果">
        <Result
          status={score && score >= 90 ? 'success' : 'info'}
          title={`得分: ${score} / ${exam.total_score}`}
          subTitle={`正确率: ${score != null ? ((score / exam.total_score) * 100).toFixed(1) : 0}%`}
          extra={
            <Space>
              <Button onClick={() => { setExam(null); setSubmitted(false); setShowAnswers(false); setScore(null); }}>
                重新生成
              </Button>
              <Button type="primary" onClick={() => setShowAnswers(true)}>
                查看答案
              </Button>
            </Space>
          }
        />
      </Card>
    );
  }

  if (submitted && showAnswers) {
    return (
      <Card title="答案详情">
        <Space style={{ marginBottom: 16 }}>
          <Button onClick={() => setShowAnswers(false)}>返回结果</Button>
          <Button onClick={() => { setExam(null); setSubmitted(false); setShowAnswers(false); setScore(null); }}>
            重新生成
          </Button>
        </Space>
        {exam.questions.map((q, i) => (
          <Card key={q.id} size="small" style={{ marginTop: 8 }}
            title={`${i + 1}. [${q.score}分] ${q.content?.substring(0, 80)}...`}>
            <p>你的答案: <Tag color={answers[q.id] === q.answer ? 'green' : 'red'}>{answers[q.id] || '未作答'}</Tag></p>
            <p>正确答案: <Tag color="green">{q.answer}</Tag></p>
            {q.options && <p>选项: {Object.entries(q.options).map(([k, v]) => `${k}. ${v}`).join(' | ')}</p>}
          </Card>
        ))}
      </Card>
    );
  }

  const q = exam.questions[currentIndex];
  if (!q) return null;

  return (
    <div style={{ maxWidth: 800, margin: '0 auto' }}>
      <Descriptions size="small" column={3} style={{ marginBottom: 16 }}
        items={[
          { key: '1', label: '试卷', children: exam.title },
          { key: '2', label: '总分', children: `${exam.total_score}分` },
          { key: '3', label: '进度', children: `${currentIndex + 1}/${exam.questions.length}` },
        ]}
      />

      <Card
        title={<Space>{q.content}</Space>}
        extra={<Tag color="purple">{q.score}分</Tag>}
      >
        {q.code_snippet && (
          <pre className="code-block">
            <code>{q.code_snippet}</code>
          </pre>
        )}

        {q.options && q.type === 'single_choice' && (
          <Radio.Group
            value={answers[q.id]}
            onChange={(e) => setAnswers({ ...answers, [q.id]: e.target.value })}
            style={{ width: '100%' }}
          >
            <Space orientation="vertical" style={{ width: '100%' }}>
              {Object.entries(q.options).map(([key, val]) => (
                <Radio key={key} value={key} style={{ padding: 8, borderRadius: 6, width: '100%' }}>
                  <strong>{key}.</strong> {val}
                </Radio>
              ))}
            </Space>
          </Radio.Group>
        )}

        {q.options && q.type === 'multi_choice' && (
          <Checkbox.Group
            value={answers[q.id] ? answers[q.id].split(',').filter(Boolean) : []}
            onChange={(vals) => setAnswers({ ...answers, [q.id]: (vals as string[]).sort().join(',') })}
            style={{ width: '100%' }}
          >
            <Space orientation="vertical" style={{ width: '100%' }}>
              {Object.entries(q.options).map(([key, val]) => (
                <Checkbox key={key} value={key} style={{ padding: 8, borderRadius: 6, width: '100%' }}>
                  <strong>{key}.</strong> {val}
                </Checkbox>
              ))}
            </Space>
          </Checkbox.Group>
        )}

        {!q.options && (
          <Input.TextArea
            value={answers[q.id] || ''}
            onChange={(e) => setAnswers({ ...answers, [q.id]: e.target.value })}
            rows={q.type === 'programming' ? 10 : 4}
            placeholder="请输入答案..."
          />
        )}
      </Card>

      <Divider />

      <div style={{ display: 'flex', justifyContent: 'space-between' }}>
        <Button onClick={() => setCurrentIndex(Math.max(0, currentIndex - 1))} disabled={currentIndex === 0}>
          上一题
        </Button>
        <Space>
          {currentIndex < exam.questions.length - 1 && (
            <Button type="primary" onClick={() => setCurrentIndex(currentIndex + 1)}>
              下一题
            </Button>
          )}
          {currentIndex === exam.questions.length - 1 && (
            <Button
              type="primary"
              danger
              onClick={handleSubmit}
              loading={loading}
              disabled={Object.keys(answers).length < exam.questions.length}
            >
              <CheckOutlined /> 交卷
            </Button>
          )}
        </Space>
      </div>
    </div>
  );
};

export default MockExam;
