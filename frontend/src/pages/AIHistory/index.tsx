import React, { useEffect, useState } from 'react';
import { Card, Spin, Empty, Tag, Collapse, List, Typography } from 'antd';
import { HistoryOutlined, RobotOutlined, UserOutlined, ClockCircleOutlined } from '@ant-design/icons';
import ReactMarkdown from 'react-markdown';
import api from '../../services/api';
import type { Message } from '../../types';

const { Text, Paragraph } = Typography;

interface Conversation {
  id: number;
  provider: string;
  title: string;
  message_count: number;
  created_at: string;
  updated_at: string;
}

interface ConversationDetail {
  id: number;
  messages: Message[];
  knowledge_point_id?: number;
  question_id?: number;
}

const AIHistory: React.FC = () => {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [loading, setLoading] = useState(true);
  const [detailLoading, setDetailLoading] = useState<number | null>(null);
  const [details, setDetails] = useState<Record<number, Message[]>>({});

  useEffect(() => {
    api.get('/ai/conversations')
      .then((res: any) => setConversations(res.data || []))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const loadDetail = async (convId: number) => {
    if (details[convId]) return;
    setDetailLoading(convId);
    try {
      const res = await api.get(`/ai/conversations/${convId}`) as any;
      setDetails(prev => ({ ...prev, [convId]: res.data?.messages || [] }));
    } catch {} finally {
      setDetailLoading(null);
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
                  <span style={{ display: 'flex', gap: 12, color: '#8C8882', fontSize: 12 }}>
                    <Tag color="blue">{conv.message_count} 条消息</Tag>
                    <span><ClockCircleOutlined /> {formatTime(conv.updated_at)}</span>
                  </span>
                </div>
              ),
              children: detailLoading === conv.id ? (
                <Spin size="small" style={{ display: 'block', margin: '20px auto' }} />
              ) : (
                <List
                  dataSource={details[conv.id] || []}
                  renderItem={(msg: Message, idx: number) => (
                    <List.Item style={{ border: 'none', padding: '12px 0' }}>
                      <div style={{ display: 'flex', gap: 10, width: '100%' }}>
                        <div style={{
                          width: 32, height: 32, borderRadius: '50%', display: 'flex',
                          alignItems: 'center', justifyContent: 'center', color: '#fff',
                          flexShrink: 0, fontSize: 13,
                          background: msg.role === 'user' ? '#4A5BC9' : '#3D8B5E',
                        }}>
                          {msg.role === 'user' ? <UserOutlined /> : <RobotOutlined />}
                        </div>
                        <div style={{
                          flex: 1, padding: '10px 14px', borderRadius: 10,
                          background: msg.role === 'user' ? '#F0F1FC' : '#F9F8F5',
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
                    </List.Item>
                  )}
                />
              ),
            }))}
          />
        )}
      </Card>
    </div>
  );
};

export default AIHistory;
