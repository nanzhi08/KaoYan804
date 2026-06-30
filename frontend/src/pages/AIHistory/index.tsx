import React, { useEffect, useState } from 'react';
import { Card, Spin, Empty, Tag, Collapse, Typography, Button, Popconfirm, App } from 'antd';
import { HistoryOutlined, RobotOutlined, UserOutlined, ClockCircleOutlined, DeleteOutlined } from '@ant-design/icons';
import ReactMarkdown from 'react-markdown';
import api from '../../services/api';
import type { APIResponse, Message } from '../../types';

const { Paragraph } = Typography;

interface Conversation {
  id: number;
  provider: string;
  title: string;
  message_count: number;
  created_at: string;
  updated_at: string;
}

interface ConversationDetail {
  messages: Message[];
}

const AIHistory: React.FC = () => {
  const { message } = App.useApp();
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [loading, setLoading] = useState(true);
  const [detailLoading, setDetailLoading] = useState<number | null>(null);
  const [details, setDetails] = useState<Record<number, Message[]>>({});

  useEffect(() => {
    api.get('/ai/conversations')
      .then((res) => {
        const body = res as unknown as APIResponse<Conversation[]>;
        setConversations(body.data || []);
      })
      .catch(() => undefined)
      .finally(() => setLoading(false));
  }, []);

  const loadDetail = async (convId: number) => {
    if (details[convId]) return;
    setDetailLoading(convId);
    try {
      const res = await api.get(`/ai/conversations/${convId}`) as unknown as APIResponse<ConversationDetail>;
      setDetails(prev => ({ ...prev, [convId]: res.data?.messages || [] }));
    } catch {
      // handled by api interceptor
    } finally {
      setDetailLoading(null);
    }
  };

  const handleDelete = async (convId: number) => {
    try {
      await api.delete(`/ai/conversations/${convId}`);
      setConversations(prev => prev.filter(c => c.id !== convId));
      setDetails(prev => { const n = { ...prev }; delete n[convId]; return n; });
      message.success('已删除');
    } catch {
      message.error('删除失败');
    }
  };

  const formatTime = (t: string) => t?.replace('T', ' ').substring(0, 19) || '';

  if (loading) return <Spin size="large" style={{ display: 'block', margin: '100px auto' }} />;

  return (
    <div style={{ maxWidth: 800, margin: '0 auto' }}>
      <Card
        title={
          <span><HistoryOutlined style={{ marginRight: 8 }} />AI 回答历史</span>
        }
      >
        {conversations.length === 0 ? (
          <Empty description="暂无对话记录，去AI导师页面开始提问吧" />
        ) : (
          <Collapse
            accordion
            onChange={(keys) => {
              const id = Number(keys[0]);
              if (id) loadDetail(id);
            }}
            items={conversations.map(conv => ({
              key: conv.id,
              label: (
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 8 }}>
                  <span style={{ fontWeight: 500 }}>{conv.title || '新对话'}</span>
                  <span style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
                    <span style={{ display: 'flex', gap: 12, color: '#94A3B8', fontSize: 12 }}>
                      <Tag color="blue">{conv.message_count} 条消息</Tag>
                      <span><ClockCircleOutlined /> {formatTime(conv.updated_at)}</span>
                    </span>
                    <Popconfirm
                      title="确定删除这条对话记录？"
                      onConfirm={(e) => { e?.stopPropagation(); handleDelete(conv.id); }}
                      onCancel={(e) => e?.stopPropagation()}
                      okText="删除" cancelText="取消"
                    >
                      <Button
                        type="text" danger size="small"
                        icon={<DeleteOutlined />}
                        onClick={(e) => e.stopPropagation()}
                      />
                    </Popconfirm>
                  </span>
                </div>
              ),
              children: detailLoading === conv.id ? (
                <Spin size="small" style={{ display: 'block', margin: '20px auto' }} />
              ) : (
                <div style={{ display: 'grid', gap: 12 }}>
                  {(details[conv.id] || []).map((msg, index) => (
                    <div key={`${msg.role}-${index}`} style={{ display: 'flex', gap: 10, width: '100%' }}>
                      <div style={{
                        width: 32, height: 32, borderRadius: '50%', display: 'flex',
                        alignItems: 'center', justifyContent: 'center', color: '#fff',
                        flexShrink: 0, fontSize: 13,
                        background: msg.role === 'user' ? '#6366F1' : '#10B981',
                      }}>
                        {msg.role === 'user' ? <UserOutlined /> : <RobotOutlined />}
                      </div>
                      <div style={{
                        flex: 1, padding: '10px 14px', borderRadius: 10,
                        background: msg.role === 'user' ? '#F5F3FF' : '#F8FAFC',
                        overflow: 'hidden',
                      }}>
                        {msg.role === 'assistant' ? (
                          <ReactMarkdown>{msg.content}</ReactMarkdown>
                        ) : (
                          <Paragraph style={{ whiteSpace: 'pre-wrap', margin: 0 }}>
                            {msg.content}
                          </Paragraph>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              ),
            }))}
          />
        )}
      </Card>
    </div>
  );
};

export default AIHistory;
