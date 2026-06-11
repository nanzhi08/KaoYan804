import React, { useEffect, useState, useRef, useCallback } from 'react';
import { useLocation } from 'react-router-dom';
import {
  Card, Select, Button, Space, Radio, Input, Tag, Spin, Empty, Result, Divider,
  Checkbox, Slider, Table, Statistic, Row, Col, Progress, Tabs, Badge, Modal,
  message,
} from 'antd';
import {
  PlayCircleOutlined, LeftOutlined, RightOutlined,
  ClockCircleOutlined, HistoryOutlined, AppstoreOutlined,
  CodeOutlined, RadarChartOutlined, FileTextOutlined, RobotOutlined,
  ThunderboltOutlined, AimOutlined, CheckCircleOutlined,
} from '@ant-design/icons';
import ChatWindow from '../../components/AIChat/ChatWindow';
import { fetchRandomQuestions, submitPractice, fetchPracticeHistory, fetchPracticeStats, fetchChapterSummaries, fetchAllQuestionsByChapter } from '../../services/questionApi';
import { usePracticeStore } from '../../stores/usePracticeStore';
import { QuestionTypeLabel } from '../../types';
import type { QuestionType, PracticeRecord, PracticeStats, ChapterSummary, Question } from '../../types';

type QuestionTypeFilter = QuestionType | '';

type PracticeRouteState = {
  autoStart?: boolean;
  mode?: string;
  knowledgePoint?: {
    id?: number;
    part?: string;
    chapter?: string;
    name?: string;
  };
  knowledgePointIds?: number[];
};

type PracticeStartOverrides = {
  count?: number;
  difficulty?: number;
  knowledgePointIds?: number[];
};

const ALL_TYPES: { value: QuestionTypeFilter; label: string }[] = [
  { value: '', label: '全部题型' },
  { value: 'single_choice', label: '选择题' },
  { value: 'multi_choice', label: '多选题' },
  { value: 'fill_blank', label: '填空题' },
  { value: 'program_reading', label: '程序阅读题' },
  { value: 'analysis', label: '分析题' },
  { value: 'calculation', label: '计算题' },
  { value: 'programming', label: '编程题' },
  { value: 'short_answer', label: '简答题' },
];

const partOptions = [
  { value: '', label: '全部' },
  { value: 'C_programming', label: 'C语言程序设计' },
  { value: 'data_structure', label: '数据结构' },
];

const difficultyMarks = { 0: '全部', 1: '1', 2: '2', 3: '3', 4: '4', 5: '5' };

const practiceModes = [
  { key: 'random', title: '随机巩固', desc: '按当前筛选快速抽题', icon: <ThunderboltOutlined /> },
  { key: 'focused', title: '专注十题', desc: '短时间保持手感', icon: <AimOutlined /> },
  { key: 'review', title: '记忆回捞', desc: '答完立刻看解析', icon: <CheckCircleOutlined /> },
];

const getRouteKnowledgePointIds = (state: PracticeRouteState | null) => {
  if (state?.knowledgePointIds?.length) return state.knowledgePointIds;
  if (state?.knowledgePoint?.id) return [state.knowledgePoint.id];
  return [];
};

// ============ 练习配置面板 ============
const PracticeConfig: React.FC<{
  onStart: (mode: string) => void;
  onShowHistory: () => void;
  onBrowseChapters: () => void;
  stats: PracticeStats | null;
}> = ({ onStart, onShowHistory, onBrowseChapters, stats }) => {
  const location = useLocation();
  const routeState = location.state as PracticeRouteState | null;
  const [qType, setQType] = useState<QuestionTypeFilter>('');
  const [part, setPart] = useState(() => {
    return routeState?.knowledgePoint?.part || '';
  });
  const [selectedKnowledgePointIds, setSelectedKnowledgePointIds] = useState<number[]>(() =>
    getRouteKnowledgePointIds(routeState),
  );
  const [count, setCount] = useState(10);
  const [difficulty, setDifficulty] = useState<number>(0);
  const { setQuestions } = usePracticeStore();
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (location.pathname !== '/practice') return;

    const nextState = location.state as PracticeRouteState | null;
    const nextIds = getRouteKnowledgePointIds(nextState);
    setPart(nextState?.knowledgePoint?.part || '');
    setSelectedKnowledgePointIds(nextIds);
  }, [location.pathname, location.state]);

  const handleStart = useCallback(async (mode: string, overrides: PracticeStartOverrides = {}) => {
    const nextCount = overrides.count ?? count;
    const nextDifficulty = overrides.difficulty ?? difficulty;
    const nextKnowledgePointIds = overrides.knowledgePointIds ?? selectedKnowledgePointIds;
    setLoading(true);
    try {
      const questions = await fetchRandomQuestions({
        count: nextCount,
        type: qType || undefined,
        part: part || undefined,
        difficulty: nextDifficulty > 0 ? nextDifficulty : undefined,
        knowledge_point_ids: nextKnowledgePointIds.length > 0 ? nextKnowledgePointIds.join(',') : undefined,
      });
      if (questions.length === 0) {
        message.info('当前筛选条件下暂无题目，请调整题型、范围或难度');
        return;
      }
      setQuestions(questions);
      onStart(mode);
    } catch { /* handled by interceptor */ }
    finally { setLoading(false); }
  }, [count, qType, part, difficulty, selectedKnowledgePointIds, setQuestions, onStart]);

  return (
    <div style={{ maxWidth: 980, margin: '0 auto' }}>
      <div style={{
        border: '1px solid #E2E8F0',
        borderRadius: 16,
        padding: 24,
        marginBottom: 16,
        background: 'linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 62%, #ECFDF5 100%)',
      }}>
        <Row gutter={[20, 16]} align="middle">
          <Col xs={24} lg={14}>
            <Tag color="green" style={{ marginBottom: 10 }}>刷题入口</Tag>
            <h2 style={{ margin: '0 0 8px 0', fontSize: 24 }}>先做一组，再复盘错因</h2>
            <p style={{ margin: 0, color: '#64748B', maxWidth: 560 }}>
              804 复习更适合短组高频反馈。建议每次 10-15 题，做完立刻看解析、标记错因，再进入复习计划。
            </p>
          </Col>
          <Col xs={24} lg={10}>
            <Row gutter={8}>
              {practiceModes.map((item) => (
                <Col span={8} key={item.key}>
                  <button
                    type="button"
                    onClick={() => {
                      if (item.key === 'focused') {
                        setCount(10);
                        void handleStart(item.key, { count: 10 });
                        return;
                      }
                      if (item.key === 'review') {
                        const reviewDifficulty = Math.max(difficulty, 2);
                        setDifficulty(reviewDifficulty);
                        void handleStart(item.key, { difficulty: reviewDifficulty });
                        return;
                      }
                      void handleStart(item.key);
                    }}
                    disabled={loading}
                    style={{
                      width: '100%',
                      minHeight: 100,
                      border: '1px solid #E2E8F0',
                      borderRadius: 12,
                      background: '#FFFFFF',
                      cursor: 'pointer',
                      padding: 10,
                      textAlign: 'left',
                      color: '#0F172A',
                      opacity: loading ? 0.6 : 1,
                    }}
                  >
                    <div style={{ color: '#6366F1', fontSize: 18, marginBottom: 8 }}>{item.icon}</div>
                    <div style={{ fontWeight: 700, marginBottom: 4 }}>{item.title}</div>
                    <div style={{ fontSize: 12, color: '#64748B', lineHeight: 1.45 }}>{item.desc}</div>
                  </button>
                </Col>
              ))}
            </Row>
          </Col>
        </Row>
      </div>

      <Card title="练习配置">
      {stats && (
        <Row gutter={12} style={{ marginBottom: 16 }}>
          <Col span={6}><Statistic title="总练习" value={stats.total} /></Col>
          <Col span={6}><Statistic title="正确率" value={stats.accuracy} suffix="%" styles={{ content: { color: stats.accuracy >= 60 ? '#10B981' : '#EF4444' } }} /></Col>
          <Col span={6}><Statistic title="今日" value={stats.today} /></Col>
          <Col span={6}><Statistic title="错题" value={stats.wrong} styles={{ content: { color: stats.wrong > 0 ? '#EF4444' : '#10B981' } }} /></Col>
        </Row>
      )}

      <Row gutter={[20, 20]}>
        <Col xs={24} lg={14}>
          <Space orientation="vertical" size="large" style={{ width: '100%' }}>
            <div>
              <div style={{ marginBottom: 8, fontWeight: 600 }}>题目类型</div>
              <Radio.Group value={qType} onChange={(e) => setQType(e.target.value)}>
                {ALL_TYPES.map((opt) => (
                  <Radio.Button key={opt.value} value={opt.value} style={{ marginBottom: 4 }}>{opt.label}</Radio.Button>
                ))}
              </Radio.Group>
            </div>
            <Row gutter={16}>
              <Col xs={24} md={12}>
                <div style={{ marginBottom: 8, fontWeight: 600 }}>科目范围</div>
                <Select
                  value={part}
                  onChange={(value) => {
                    setPart(value);
                    setSelectedKnowledgePointIds([]);
                  }}
                  options={partOptions}
                  style={{ width: '100%' }}
                />
              </Col>
              <Col xs={24} md={12}>
                <div style={{ marginBottom: 8, fontWeight: 600 }}>题目数量</div>
                <Input type="number" value={count} onChange={(e) => setCount(Number(e.target.value))} min={1} max={50} />
              </Col>
            </Row>
            <div>
              <div style={{ marginBottom: 8, fontWeight: 600 }}>难度筛选</div>
              <Slider min={0} max={5} value={difficulty} onChange={setDifficulty} marks={difficultyMarks} />
            </div>
          </Space>
        </Col>
        <Col xs={24} lg={10}>
          <div style={{ border: '1px solid #E2E8F0', borderRadius: 12, padding: 16, height: '100%' }}>
            <div style={{ fontWeight: 700, marginBottom: 12 }}>本组建议</div>
            <Space orientation="vertical" size={10} style={{ width: '100%' }}>
              <Tag color="blue">题型：{ALL_TYPES.find((item) => item.value === qType)?.label}</Tag>
              <Tag color="green">范围：{partOptions.find((item) => item.value === part)?.label}</Tag>
              {selectedKnowledgePointIds.length > 0 && (
                <Tag color="red">定向知识点：{selectedKnowledgePointIds.length} 个</Tag>
              )}
              <Tag color="orange">数量：{count} 题 · 难度：{difficulty === 0 ? '全部' : difficulty}</Tag>
              <Button type="primary" icon={<PlayCircleOutlined />} loading={loading} onClick={() => handleStart('random')} block size="large">
                开始刷题
              </Button>
              <Button icon={<AppstoreOutlined />} onClick={onBrowseChapters} block>按章节浏览</Button>
              <Button icon={<HistoryOutlined />} onClick={onShowHistory} block>查看练习历史</Button>
            </Space>
          </div>
        </Col>
      </Row>
      </Card>
    </div>
  );
};

// ============ 答题界面 ============
const QuizView: React.FC<{ onBack: () => void; mode: string }> = ({ onBack, mode }) => {
  const { questions, currentIndex, answers, results, setCurrentIndex, setAnswer, setResult } = usePracticeStore();
  const question = questions[currentIndex];
  const [submitting, setSubmitting] = useState(false);
  const [timer, setTimer] = useState(0);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const [aiModalOpen, setAiModalOpen] = useState(false);
  const [aiInitialMsg, setAiInitialMsg] = useState('');

  const currentResult = results[question?.id];
  const savedAnswer = question ? answers[question.id] || '' : '';
  const selectedMultiAnswers = question?.type === 'multi_choice' && savedAnswer
    ? savedAnswer.split(',').filter(Boolean)
    : [];

  // Open AI mini window with current question context
  const handleAskAI = useCallback(() => {
    if (!question) return;
    const text = [
      question.content,
      question.code_snippet ? `\n代码:\n${question.code_snippet}` : '',
      question.options && Object.keys(question.options).length > 0
        ? `\n选项:\n${Object.entries(question.options).map(([k, v]) => `${k}. ${v}`).join('\n')}` : '',
    ].filter(Boolean).join('\n');
    setAiInitialMsg(`请帮我讲解这道题目：\n\n${text}`);
    setAiModalOpen(true);
  }, [question]);

  // Timer
  useEffect(() => {
    timerRef.current = setInterval(() => setTimer(t => t + 1), 1000);
    return () => { if (timerRef.current) clearInterval(timerRef.current); };
  }, [currentIndex]);

  const formatTime = (sec: number) => `${Math.floor(sec / 60)}:${(sec % 60).toString().padStart(2, '0')}`;

  const handleSubmit = async () => {
    if (!question || submitting) return;
    const answer = question.type === 'multi_choice'
      ? selectedMultiAnswers.slice().sort().join(',')
      : savedAnswer;
    setSubmitting(true);
    try {
      const result = await submitPractice({
        question_id: question.id,
        user_answer: answer,
        time_spent: timer,
        practice_mode: mode,
      });
      setResult(question.id, result);
      setAnswer(question.id, answer);
      if (timerRef.current) clearInterval(timerRef.current);
    } catch { /* handled by interceptor */ }
    finally { setSubmitting(false); }
  };

  const goNext = () => {
    setTimer(0);
    if (currentIndex < questions.length - 1) setCurrentIndex(currentIndex + 1);
  };
  const goPrev = () => {
    setTimer(0);
    if (currentIndex > 0) setCurrentIndex(currentIndex - 1);
  };

  if (!question) return <Empty description="没有题目" />;
  const allAnswered = Object.keys(results).length === questions.length;
  const correctCount = Object.values(results).filter(r => r.is_correct).length;
  const isReady = question.type === 'multi_choice' ? selectedMultiAnswers.length > 0 : !!savedAnswer;
  const answeredCount = Object.keys(results).length;
  const currentAccuracy = answeredCount > 0 ? Math.round((correctCount / answeredCount) * 100) : 0;

  return (
    <div style={{ maxWidth: 920, margin: '0 auto' }}>
      <div style={{
        marginBottom: 16,
        padding: 14,
        border: '1px solid #E2E8F0',
        borderRadius: 14,
        background: '#FFFFFF',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        gap: 12,
        flexWrap: 'wrap',
      }}>
        <Button icon={<LeftOutlined />} onClick={onBack}>返回</Button>
        <Space>
          <Tag>{QuestionTypeLabel[question.type]}</Tag>
          <span>第{currentIndex + 1}/{questions.length}题</span>
          <Tag icon={<ClockCircleOutlined />}>{formatTime(timer)}</Tag>
          <Tag color={answeredCount > 0 && currentAccuracy >= 70 ? 'green' : 'orange'}>当前正确率 {currentAccuracy}%</Tag>
          {!currentResult && <Tag>难度: {'★'.repeat(question.difficulty)}</Tag>}
        </Space>
      </div>

      {/* Progress bar */}
      <Progress percent={Math.round(((currentIndex + 1) / questions.length) * 100)} size="small" style={{ marginBottom: 12 }} />

      <Card
        title={<div style={{ whiteSpace: 'pre-wrap', fontSize: 17, lineHeight: 1.8 }}>{question.content}</div>}
        extra={
          <Button type="default" icon={<RobotOutlined />} size="small" onClick={handleAskAI}>
            AI 讲解
          </Button>
        }
      >
        {question.code_snippet && (
          <pre className="code-block">
            <code>{question.code_snippet}</code>
          </pre>
        )}

        <div style={{ marginTop: 16 }}>
          {question.type === 'single_choice' && question.options && (
            <Radio.Group value={answers[question.id]} onChange={(e) => setAnswer(question.id, e.target.value)}
              disabled={!!currentResult} style={{ width: '100%' }}>
              <Space orientation="vertical" style={{ width: '100%' }}>
                {Object.entries(question.options).map(([key, val]) => (
                  <Radio key={key} value={key} style={{
                    padding: '12px 16px', border: '1px solid #E2E8F0', borderRadius: 8, width: '100%',
                    background: currentResult && key === question.answer ? '#ECFDF5' :
                      currentResult && key === answers[question.id] && key !== question.answer ? '#FEF2F2' : undefined,
                  }}><strong>{key}.</strong> {val}</Radio>
                ))}
              </Space>
            </Radio.Group>
          )}

          {question.type === 'multi_choice' && question.options && (
            <Checkbox.Group
              value={selectedMultiAnswers}
              onChange={(vals) => setAnswer(question.id, (vals as string[]).sort().join(','))}
              disabled={!!currentResult} style={{ width: '100%' }}>
              <Space orientation="vertical" style={{ width: '100%' }}>
                {Object.entries(question.options).map(([key, val]) => (
                  <Checkbox key={key} value={key} style={{ padding: '12px 16px', border: '1px solid #E2E8F0', borderRadius: 8, width: '100%' }}>
                    <strong>{key}.</strong> {val}
                  </Checkbox>
                ))}
              </Space>
            </Checkbox.Group>
          )}

          {(question.type === 'fill_blank' || question.type === 'programming') && (
            <Input.TextArea value={savedAnswer}
              onChange={(e) => setAnswer(question.id, e.target.value)}
              disabled={!!currentResult}
              rows={question.type === 'programming' ? 10 : 3}
              placeholder={question.type === 'programming' ? '请输入C语言代码...' : '请输入答案...'} />
          )}

          {(question.type === 'program_reading' || question.type === 'analysis'
            || question.type === 'calculation' || question.type === 'short_answer') && (
            <Input.TextArea value={savedAnswer}
              onChange={(e) => setAnswer(question.id, e.target.value)}
              disabled={!!currentResult} rows={4} placeholder="请输入你的答案..." />
          )}
        </div>

        {currentResult && (
          <div style={{ marginTop: 16 }}>
            <Result
              status={currentResult.is_correct ? 'success' : 'error'}
              title={currentResult.is_correct ? '回答正确！' : '回答错误'}
              subTitle={<div><Tag color={currentResult.is_correct ? 'green' : 'red'}>正确答案</Tag>{currentResult.correct_answer}</div>} />
            {currentResult.explanation && (
              <div style={{
                marginTop: 8,
                padding: 14,
                borderRadius: 10,
                border: '1px solid #E2E8F0',
                background: '#F8FAFC',
              }}>
                <div style={{ fontWeight: 700, marginBottom: 6 }}>解析</div>
                <div style={{ whiteSpace: 'pre-wrap', lineHeight: 1.8 }}>{currentResult.explanation}</div>
              </div>
            )}
            <div style={{
              marginTop: 10,
              padding: 14,
              borderRadius: 10,
              border: currentResult.is_correct ? '1px solid #BBF7D0' : '1px solid #FED7AA',
              background: currentResult.is_correct ? '#F0FDF4' : '#FFF7ED',
            }}>
              <Space orientation="vertical" size={4}>
                <Tag color={currentResult.is_correct ? 'green' : 'orange'}>复盘动作</Tag>
                <span style={{ color: '#475569' }}>
                  {currentResult.is_correct
                    ? '确认本题关键条件和易混点，下一题保持节奏。'
                    : '先对照正确答案定位错因，再读解析；同类知识点建议放入今日复习。'}
                </span>
              </Space>
            </div>
          </div>
        )}

        <Divider />
        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
          <Button onClick={goPrev} disabled={currentIndex === 0} icon={<LeftOutlined />}>上一题</Button>
          <Space>
            {!currentResult && (
              <Button type="primary" onClick={handleSubmit} loading={submitting} disabled={!isReady}>提交答案</Button>
            )}
            {currentIndex < questions.length - 1 && currentResult && (
              <Button onClick={goNext} icon={<RightOutlined />}>下一题</Button>
            )}
          </Space>
        </div>

        {allAnswered && currentIndex === questions.length - 1 && currentResult && (
          <div style={{ marginTop: 16, textAlign: 'center' }}>
            <Result status="success" title="练习完成！"
              subTitle={`正确 ${correctCount} / ${questions.length} 题 (${Math.round(correctCount / questions.length * 100)}%)`}
              extra={<Button type="primary" onClick={onBack}>返回</Button>} />
          </div>
        )}
      </Card>

      {/* AI 小窗 — 复制题目后弹出 */}
      <Modal
        title={<span><RobotOutlined style={{ marginRight: 8 }} />AI 导师</span>}
        open={aiModalOpen}
        onCancel={() => setAiModalOpen(false)}
        width={900}
        style={{ top: 20 }}
        footer={null}
        destroyOnHidden={false}
      >
        <ChatWindow provider="deepseek" compact initialMessage={aiInitialMsg} />
      </Modal>
    </div>
  );
};

// ============ 练习历史面板 ============
const HistoryView: React.FC<{ onBack: () => void }> = ({ onBack }) => {
  const [records, setRecords] = useState<PracticeRecord[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchPracticeHistory({ page: 1, page_size: 50 })
      .then((d) => setRecords(d.items || []))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <Spin size="large" style={{ display: 'block', margin: '50px auto' }} />;

  return (
    <Card title="练习历史" extra={<Button onClick={onBack}>返回</Button>}>
      <Table
        dataSource={records}
        rowKey="id"
        size="small"
        pagination={{ pageSize: 20 }}
        columns={[
          { title: '时间', dataIndex: 'created_at', width: 160, render: (v: string) => v?.replace('T', ' ').substring(0, 19) },
          { title: '题目', dataIndex: 'question_content', ellipsis: true },
          { title: '类型', dataIndex: 'question_type', width: 110, render: (v: string) => <Tag>{QuestionTypeLabel[v as QuestionType] || v}</Tag> },
          { title: '你的答案', dataIndex: 'user_answer', width: 120, ellipsis: true },
          { title: '结果', dataIndex: 'is_correct', width: 80, render: (v: boolean) => <Tag color={v ? 'green' : 'red'}>{v ? '正确' : '错误'}</Tag> },
          { title: '耗时', dataIndex: 'time_spent', width: 80, render: (v: number) => `${v}s` },
        ]}
      />
    </Card>
  );
};

// ============ 按章节浏览 ============
const partLabel: Record<string, string> = {
  C_programming: 'C语言程序设计',
  data_structure: '数据结构',
};
const partColor: Record<string, string> = {
  C_programming: '#6366F1',
  data_structure: '#10B981',
};

const ChapterBrowse: React.FC<{
  onStartChapter: (questions: Question[]) => void;
  onBack: () => void;
}> = ({ onStartChapter, onBack }) => {
  const [summaries, setSummaries] = useState<ChapterSummary[]>([]);
  const [activeSubject, setActiveSubject] = useState<string>('C_programming');
  const [activeChapter, setActiveChapter] = useState<string | null>(null);
  const [questions, setQuestions] = useState<Question[]>([]);
  const [questionsLoading, setQuestionsLoading] = useState(false);
  const [summariesLoading, setSummariesLoading] = useState(true);

  useEffect(() => {
    fetchChapterSummaries()
      .then(setSummaries)
      .catch(() => {})
      .finally(() => setSummariesLoading(false));
  }, []);

  const subjectChapters = React.useMemo(() => summaries
    .filter(s => s.part === activeSubject)
    .sort((a, b) => a.chapter.localeCompare(b.chapter)), [activeSubject, summaries]);

  const handleSelectChapter = useCallback(async (chapter: string) => {
    setActiveChapter(chapter);
    setQuestionsLoading(true);
    try {
      const allQuestions = await fetchAllQuestionsByChapter({
        part: activeSubject,
        chapter,
      });
      setQuestions(allQuestions);
    } catch { setQuestions([]); }
    finally { setQuestionsLoading(false); }
  }, [activeSubject]);

  useEffect(() => {
    if (subjectChapters.length > 0 && !activeChapter) {
      const firstChapter = subjectChapters[0].chapter;
      void handleSelectChapter(firstChapter);
    }
  }, [activeChapter, handleSelectChapter, subjectChapters]);

  if (summariesLoading) return <Spin size="large" style={{ display: 'block', margin: '50px auto' }} />;

  return (
    <div style={{ maxWidth: 900, margin: '0 auto' }}>
      <div style={{ marginBottom: 16 }}>
        <Button icon={<LeftOutlined />} onClick={onBack}>返回配置</Button>
      </div>

      <Tabs
        activeKey={activeSubject}
        onChange={(key) => { setActiveSubject(key); setActiveChapter(null); setQuestions([]); }}
        items={[
          {
            key: 'C_programming',
            label: <span><CodeOutlined /> C语言程序设计</span>,
            children: null,
          },
          {
            key: 'data_structure',
            label: <span><RadarChartOutlined /> 数据结构</span>,
            children: null,
          },
        ]}
      />

      {subjectChapters.length === 0 ? (
        <Empty description="该科目暂无章节数据" />
      ) : (
        <>
          <Tabs
            activeKey={activeChapter || undefined}
            onChange={handleSelectChapter}
            style={{ marginBottom: 16 }}
            items={subjectChapters.map(s => ({
              key: s.chapter,
              label: (
                <Badge count={s.question_count} size="small" offset={[6, -2]} color={partColor[activeSubject]}>
                  <span style={{ paddingRight: 4 }}>{s.chapter_name}</span>
                </Badge>
              ),
            }))}
          />

          <Card
            title={
              <Space>
                <FileTextOutlined />
                <span>{subjectChapters.find(s => s.chapter === activeChapter)?.chapter_name || activeChapter} - 题目列表</span>
                <Tag color={partColor[activeSubject]}>{partLabel[activeSubject]}</Tag>
              </Space>
            }
            extra={
              <Button
                type="primary"
                icon={<PlayCircleOutlined />}
                disabled={questions.length === 0}
                onClick={() => onStartChapter(questions)}
              >
                全部练习（{questions.length}题）
              </Button>
            }
          >
            {questionsLoading ? (
              <Spin style={{ display: 'block', margin: '30px auto' }} />
            ) : questions.length === 0 ? (
              <Empty description="该章节暂无题目" />
            ) : (
              <div style={{ display: 'grid', gap: 10 }}>
                {questions.map((q, idx) => (
                  <div
                    key={q.id}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      gap: 16,
                      padding: '12px 0',
                      borderBottom: '1px solid #F1F5F9',
                    }}
                  >
                    <div style={{ display: 'flex', gap: 10, minWidth: 0, flex: 1 }}>
                      <Space size={4} style={{ flexShrink: 0 }}>
                        <Tag color="blue">{idx + 1}</Tag>
                        <Tag>{QuestionTypeLabel[q.type]}</Tag>
                      </Space>
                      <div style={{ minWidth: 0 }}>
                        <div style={{ fontSize: 14, lineHeight: 1.6, marginBottom: 6 }}>
                          {q.content.length > 80 ? q.content.slice(0, 80) + '...' : q.content}
                        </div>
                        <span style={{ color: '#64748B', fontSize: 13 }}>
                          难度: {'★'.repeat(q.difficulty)}{'☆'.repeat(5 - q.difficulty)}
                        </span>
                      </div>
                    </div>
                    <div style={{ flexShrink: 0 }}>
                      <Button
                        type="link"
                        icon={<PlayCircleOutlined />}
                        onClick={() => onStartChapter([q])}
                      >
                        练习此题
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </Card>
        </>
      )}
    </div>
  );
};

// ============ 主组件 ============
const Practice: React.FC = () => {
  const location = useLocation();
  const { questions, reset, setQuestions } = usePracticeStore();
  const routeState = location.state as PracticeRouteState | null;
  const [started, setStarted] = useState(() => Boolean(routeState?.autoStart && questions.length > 0));
  const [mode, setMode] = useState(() => routeState?.mode || 'random');
  const [view, setView] = useState<'config' | 'quiz' | 'history' | 'browse'>('config');
  const [stats, setStats] = useState<PracticeStats | null>(null);
  const autoStartedRef = useRef(false);

  useEffect(() => {
    fetchPracticeStats().then(setStats).catch(() => {});
  }, [started]);

  useEffect(() => {
    const state = location.state as PracticeRouteState | null;
    if (state?.autoStart && questions.length > 0 && !autoStartedRef.current) {
      autoStartedRef.current = true;
      setMode(state.mode || 'wrong');
      setStarted(true);
      setView('config');
    }
  }, [location.state, questions.length]);

  if (started && questions.length > 0) {
    return <QuizView onBack={() => { reset(); setStarted(false); setView('config'); }} mode={mode} />;
  }
  if (view === 'history') return <HistoryView onBack={() => setView('config')} />;
  if (view === 'browse') {
    return (
      <ChapterBrowse
        onStartChapter={(qs) => {
          setQuestions(qs);
          setMode('chapter');
          setStarted(true);
        }}
        onBack={() => setView('config')}
      />
    );
  }

  return (
    <PracticeConfig
      onStart={(m) => { setMode(m); setStarted(true); }}
      onShowHistory={() => setView('history')}
      onBrowseChapters={() => setView('browse')}
      stats={stats}
    />
  );
};

export default Practice;
