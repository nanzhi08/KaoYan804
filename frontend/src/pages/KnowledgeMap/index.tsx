import React, { useEffect, useState } from 'react';
import { Card, Tree, Spin, Empty, Descriptions, Tag, Button, Row, Col, Space, Modal, message as antdMessage } from 'antd';
import { useNavigate } from 'react-router-dom';
import { RobotOutlined, BookOutlined, ArrowRightOutlined, ReloadOutlined } from '@ant-design/icons';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { fetchKnowledgePoints, fetchKnowledgePoint } from '../../services/knowledgeApi';
import { useAppStore } from '../../stores/useAppStore';
import type { KnowledgePoint } from '../../types';

const partColors: Record<string, string> = {
  C_programming: '#4A5BC9',
  data_structure: '#3D8B5E',
  root: '#D4953A',
};

const markdownComponents = {
  code({ node, className, children, ...props }: any) {
    const match = /language-(\w+)/.exec(className || '');
    const codeText = String(children).replace(/\n$/, '');
    const inline = !match && !codeText.includes('\n');
    if (inline) {
      return <code className={className} {...props}>{children}</code>;
    }
    return (
      <SyntaxHighlighter
        style={oneDark}
        language={match?.[1] || 'c'}
        PreTag="div"
        customStyle={{ borderRadius: 6, fontSize: 13 }}
      >
        {codeText}
      </SyntaxHighlighter>
    );
  },
};

const KnowledgeMap: React.FC = () => {
  const [treeData, setTreeData] = useState<KnowledgePoint[]>([]);
  const [loading, setLoading] = useState(true);
  const { selectedKnowledgePoint, setSelectedKnowledgePoint } = useAppStore();
  const navigate = useNavigate();

  useEffect(() => {
    fetchKnowledgePoints()
      .then(setTreeData)
      .catch(() => {}) // handled by api interceptor
      .finally(() => setLoading(false));
  }, []);

  const convertToTreeData = (nodes: KnowledgePoint[]): any[] =>
    nodes.map((node) => ({
      title: (
        <span>
          <Tag color={partColors[node.part] || '#9B9590'} style={{ marginRight: 8 }}>
            {node.chapter || node.part}
          </Tag>
          {node.name}
        </span>
      ),
      key: node.id,
      children: node.children?.length > 0 ? convertToTreeData(node.children) : undefined,
      isLeaf: node.children?.length === 0,
    }));

  const [kpLoading, setKpLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [streamingText, setStreamingText] = useState('');
  const [explainModalOpen, setExplainModalOpen] = useState(false);

  const handleGenerateExplanation = async () => {
    if (!selectedKnowledgePoint) return;
    setGenerating(true);
    setStreamingText('');
    try {
      const params = new URLSearchParams({ kp_id: String(selectedKnowledgePoint.id), provider: 'deepseek' });
      const response = await fetch(`/api/ai/explain/save-stream?${params}`, { method: 'POST' });
      if (!response.ok) throw new Error(`Server error (${response.status})`);

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let fullText = '';

      while (reader) {
        const { done, value } = await reader.read();
        if (done) break;
        const text = decoder.decode(value);
        const lines = text.split('\n').filter(l => l.startsWith('data: '));
        for (const line of lines) {
          try {
            const data = JSON.parse(line.slice(6));
            if (data.error) throw new Error(data.error);
            if (data.chunk) { fullText += data.chunk; setStreamingText(fullText); }
            if (data.done) {
              const updated = await fetchKnowledgePoint(selectedKnowledgePoint.id);
              setSelectedKnowledgePoint(updated);
            }
          } catch (e: any) {
            if (e.message && !e.message.startsWith('Unexpected')) throw e;
          }
        }
      }
    } catch (e: any) {
      antdMessage.error(e.message || 'AI讲解生成失败');
    } finally {
      setGenerating(false);
      setStreamingText('');
    }
  };

  const handleRegenerateExplanation = async () => {
    await handleGenerateExplanation();
  };

  const handleSelect = async (_selectedKeys: any, info: any) => {
    if (info.node.isLeaf) {
      setKpLoading(true);
      try {
        const kp = await fetchKnowledgePoint(info.node.key);
        setSelectedKnowledgePoint(kp);
      } catch (e) { /* handled by interceptor */ }
      finally { setKpLoading(false); }
    } else {
      setSelectedKnowledgePoint(null);
    }
  };

  if (loading) return <Spin size="large" style={{ display: 'block', margin: '100px auto' }} />;

  return (
    <Row gutter={24}>
      <Col xs={24} lg={10}>
        <Card title="804 知识地图" extra={<Tag color="blue">共{treeData.flatMap(n => n.children || []).length}个章节知识点</Tag>}>
          {treeData.length > 0 ? (
            <Tree
              showLine
              defaultExpandAll
              treeData={convertToTreeData(treeData)}
              onSelect={handleSelect}
              style={{ fontSize: 14 }}
            />
          ) : (
            <Empty description="知识点数据为空" />
          )}
        </Card>
      </Col>
      <Col xs={24} lg={14}>
        <Spin spinning={kpLoading}>
        {selectedKnowledgePoint ? (
          <Card
            title={
              <span>
                <BookOutlined style={{ marginRight: 8 }} />
                {selectedKnowledgePoint.name}
              </span>
            }
            extra={
              <Space>
                {selectedKnowledgePoint.ai_explanation && (
                  <Button
                    type="default"
                    icon={<ReloadOutlined />}
                    loading={generating}
                    onClick={handleRegenerateExplanation}
                  >
                    重新生成
                  </Button>
                )}
                <Button
                  type="primary"
                  icon={<RobotOutlined />}
                  loading={generating}
                  onClick={handleGenerateExplanation}
                >
                  {selectedKnowledgePoint.ai_explanation ? 'AI讲解(已缓存)' : '生成AI讲解'}
                </Button>
                <Button
                  type="default"
                  icon={<ArrowRightOutlined />}
                  onClick={() => navigate('/ai-tutor', {
                    state: { knowledgePoint: selectedKnowledgePoint }
                  })}
                >
                  对话
                </Button>
              </Space>
            }
          >
            <Descriptions column={1} bordered size="small">
              <Descriptions.Item label="章节">{selectedKnowledgePoint.chapter}</Descriptions.Item>
              <Descriptions.Item label="所属部分">
                <Tag color={partColors[selectedKnowledgePoint.part]}>
                  {selectedKnowledgePoint.part === 'C_programming' ? 'C语言程序设计' : '数据结构'}
                </Tag>
              </Descriptions.Item>
              <Descriptions.Item label="难度">
                {'★'.repeat(selectedKnowledgePoint.difficulty)}{'☆'.repeat(5 - selectedKnowledgePoint.difficulty)}
              </Descriptions.Item>
              <Descriptions.Item label="考试频率">
                <Tag color={selectedKnowledgePoint.exam_weight === '高频' ? 'red' : 'orange'}>
                  {selectedKnowledgePoint.exam_weight}
                </Tag>
              </Descriptions.Item>
              <Descriptions.Item label="内容说明">
                {selectedKnowledgePoint.description || '暂无详细说明'}
              </Descriptions.Item>
            </Descriptions>

            {streamingText && (
              <Card
                title={<span><RobotOutlined style={{ marginRight: 8 }} />AI 讲解（生成中...）</span>}
                size="small"
                style={{ marginTop: 16 }}
              >
                <div style={{ maxHeight: 400, overflow: 'auto', fontSize: 14, lineHeight: 1.8 }}>
                  <ReactMarkdown components={markdownComponents}>
                    {streamingText}
                  </ReactMarkdown>
                </div>
              </Card>
            )}

            {selectedKnowledgePoint.ai_explanation && !streamingText && !generating && (
              <div
                style={{ marginTop: 16 }}
                onClick={() => setExplainModalOpen(true)}
              >
                <Card
                  size="small"
                  title={
                    <span>
                      <span style={{
                        display: 'inline-block', width: 8, height: 8, borderRadius: '50%',
                        background: '#3D8B5E', marginRight: 8, verticalAlign: 'middle'
                      }} />
                      AI 讲解（已缓存）
                    </span>
                  }
                  extra={
                    <Button type="link" size="small" style={{ padding: 0 }}>
                      查看完整讲解 →
                    </Button>
                  }
                  hoverable
                  style={{ cursor: 'pointer', borderColor: '#E8E3DC' }}
                  styles={{
                    body: { padding: '12px 16px' }
                  }}
                >
                  <div style={{
                    maxHeight: 100, overflow: 'hidden', position: 'relative',
                    fontSize: 13, lineHeight: 1.7, color: '#6B6560',
                  }}>
                    <ReactMarkdown components={markdownComponents}>
                      {selectedKnowledgePoint.ai_explanation.slice(0, 300) + '...'}
                    </ReactMarkdown>
                    <div style={{
                      position: 'absolute', bottom: 0, left: 0, right: 0, height: 48,
                      background: 'linear-gradient(transparent, #FFFFFF)',
                      pointerEvents: 'none',
                    }} />
                  </div>
                </Card>
              </div>
            )}

            <div style={{ marginTop: 16 }}>
              <Button
                type="default"
                icon={<ArrowRightOutlined />}
                onClick={() => navigate('/practice', {
                  state: { knowledgePoint: selectedKnowledgePoint }
                })}
              >
                练习此章节题目
              </Button>
            </div>
          </Card>
        ) : (
          <Card>
            <Empty description="请在左侧知识树中选择一个知识点查看详情" />
          </Card>
        )}
        </Spin>
      </Col>

      <Modal
        title={
          <span style={{ fontSize: 16, fontWeight: 600 }}>
            <RobotOutlined style={{ marginRight: 8, color: '#4A5BC9' }} />
            AI 讲解
            <span style={{ fontSize: 13, fontWeight: 400, color: '#9B9590', marginLeft: 12 }}>
              {selectedKnowledgePoint?.name}
            </span>
          </span>
        }
        open={explainModalOpen}
        onCancel={() => setExplainModalOpen(false)}
        footer={null}
        width={820}
        style={{ top: 28 }}
        styles={{
          body: {
            maxHeight: 'calc(100vh - 180px)',
            overflow: 'auto',
            fontSize: 15,
            lineHeight: 1.9,
            padding: '20px 28px',
            color: '#2C2C2C',
          },
        }}
      >
        {selectedKnowledgePoint?.ai_explanation && (
          <ReactMarkdown components={markdownComponents}>
            {selectedKnowledgePoint.ai_explanation}
          </ReactMarkdown>
        )}
      </Modal>
    </Row>
  );
};

export default KnowledgeMap;
