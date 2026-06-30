import React, { useState, useRef, useEffect, useCallback } from 'react';
import { Input, Button, Empty, Spin, Alert } from 'antd';
import { SendOutlined, RobotOutlined, UserOutlined, ClearOutlined } from '@ant-design/icons';
import ReactMarkdown from 'react-markdown';
import type { KnowledgePoint, Message } from '../../types';
import MarkdownCode from '../MarkdownCode';
import FeedbackButton from './FeedbackButton';

interface ChatWindowProps {
  knowledgePoint?: KnowledgePoint | null;
  provider: string;
  initialMessage?: string;
  compact?: boolean;
}

/** Memoized message bubble - avoids re-render when sibling messages update */
const MessageBubble = React.memo(({ msg, idx, convId }: {
  msg: Message; idx: number; convId: number | null;
}) => (
  <div className="msg-row">
    <div className={`msg-avatar ${msg.role === 'user' ? 'msg-avatar-user' : 'msg-avatar-assistant'}`}>
      {msg.role === 'user' ? <UserOutlined /> : <RobotOutlined />}
    </div>
    <div style={{ flex: 1 }}>
      <div className={`msg-bubble ${msg.role === 'user' ? 'msg-bubble-user' : 'msg-bubble-assistant'}`}>
        {msg.role === 'assistant' ? (
          <ReactMarkdown
            components={{
              code({ className, children, ...props }) {
                return <MarkdownCode className={className} {...props}>{children}</MarkdownCode>;
              },
            }}
          >
            {msg.content}
          </ReactMarkdown>
        ) : (
          <div style={{ whiteSpace: 'pre-wrap' }}>{msg.content}</div>
        )}
      </div>
      {msg.role === 'assistant' && convId !== null && (
        <div className="msg-feedback-area">
          <FeedbackButton
            messageId={msg.id || `msg-${idx}`}
            conversationId={convId}
            messageIndex={idx}
          />
        </div>
      )}
    </div>
  </div>
));
MessageBubble.displayName = 'MessageBubble';

interface StreamPayload {
  error?: string;
  chunk?: string;
  conversation_id?: number;
  msg_id?: string;
}

const isJsonChunkBoundaryError = (error: unknown) => (
  error instanceof Error && error.message.startsWith('Unexpected')
);

const ChatWindow: React.FC<ChatWindowProps> = ({ knowledgePoint, provider, initialMessage, compact }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [conversationId, setConversationId] = useState<number | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const rafRef = useRef<number | null>(null);
  const initialMessageSentRef = useRef<string | null>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const getAuthHeaders = (extra: Record<string, string> = {}) => {
    const token = localStorage.getItem('token');
    const headers: Record<string, string> = { ...extra };
    if (token) headers['Authorization'] = `Bearer ${token}`;
    return headers;
  };

  /** Shared SSE streaming logic with throttled UI updates via rAF */
  const streamResponse = useCallback(async (
    fetchPromise: Promise<Response>,
    baseMessages: Message[],
  ) => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetchPromise;
      if (!response.ok) throw new Error(`服务器返回错误 (${response.status})`);

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let fullText = '';
      let convId: number | null = null;
      let msgId: string | undefined;
      let pendingUpdate = false;

      const flushUI = () => {
        if (convId) setConversationId(prev => prev ?? convId);
        setMessages([...baseMessages, { role: 'assistant', content: fullText || '思考中...', id: msgId }]);
        pendingUpdate = false;
        rafRef.current = null;
      };

      while (reader) {
        const { done, value } = await reader.read();
        if (done) break;

        const text = decoder.decode(value);
        const lines = text.split('\n').filter(l => l.startsWith('data: '));
        for (const line of lines) {
          try {
            const data = JSON.parse(line.slice(6)) as StreamPayload;
            if (data.error) throw new Error(data.error);
            if (data.chunk) fullText += data.chunk;
            if (data.conversation_id) convId = data.conversation_id;
            if (data.msg_id) msgId = data.msg_id;
          } catch (error: unknown) {
            if (!isJsonChunkBoundaryError(error)) throw error;
          }
        }

        // Throttle: only schedule one rAF at a time
        if (!pendingUpdate) {
          pendingUpdate = true;
          rafRef.current = requestAnimationFrame(flushUI);
        }
      }

      // Flush remaining
      if (rafRef.current) cancelAnimationFrame(rafRef.current);
      setMessages([...baseMessages, { role: 'assistant', content: fullText, id: msgId }]);
      if (convId) setConversationId(convId);
    } catch (error) {
      const e = error as { message?: string };
      setError(e.message || 'AI请求失败，请检查后端服务');
    } finally {
      setLoading(false);
    }
  }, []);

  const handleAIExplain = useCallback(async (kp: KnowledgePoint) => {
    const explainMsg = `请帮我详细讲解【${kp.name}】这个知识点。`;
    const baseMessages: Message[] = [{ role: 'user', content: explainMsg }];
    setConversationId(null);
    setMessages(baseMessages);

    const params = new URLSearchParams({ kp_id: String(kp.id), provider });
    await streamResponse(
      fetch(`/api/ai/explain?${params}`, { method: 'POST', headers: getAuthHeaders() }),
      baseMessages,
    );
  }, [provider, streamResponse]);

  const handleSendWithMessage = useCallback(async (msg: string, baseMessages = messages) => {
    const newMessages: Message[] = [...baseMessages, { role: 'user', content: msg }];
    setMessages(newMessages);
    await streamResponse(
      fetch('/api/ai/chat', {
        method: 'POST',
        headers: getAuthHeaders({ 'Content-Type': 'application/json' }),
        body: JSON.stringify({
          provider,
          message: msg,
          conversation_id: conversationId,
          knowledge_point_id: knowledgePoint?.id,
          messages: baseMessages,
        }),
      }),
      newMessages,
    );
  }, [conversationId, knowledgePoint?.id, messages, provider, streamResponse]);

  const handleSend = async () => {
    if (!input.trim() || loading) return;
    const userMsg = input.trim();
    setInput('');
    await handleSendWithMessage(userMsg);
  };

  const handleClear = () => {
    setMessages([]);
    setConversationId(null);
    setError(null);
  };

  useEffect(() => {
    if (!knowledgePoint) return;
    queueMicrotask(() => {
      void handleAIExplain(knowledgePoint);
    });
  }, [handleAIExplain, knowledgePoint]);

  useEffect(() => {
    if (!initialMessage || initialMessageSentRef.current === initialMessage) return;
    initialMessageSentRef.current = initialMessage;
    queueMicrotask(() => {
      void handleSendWithMessage(initialMessage, []);
    });
  }, [handleSendWithMessage, initialMessage]);

  const msgListHeight = compact ? 520 : 'calc(100vh - 240px)';

  return (
    <>
      <style>{`
        .msg-row { display: flex; gap: 12px; margin-bottom: 20px; }
        .msg-bubble { padding: 14px 18px; border-radius: 14px; overflow: hidden; line-height: 1.7; }
        .msg-bubble-user { background: linear-gradient(135deg, #6366F1, #818CF8); color: #fff; }
        .msg-bubble-assistant { background: #F8FAFC; border: 1px solid #E2E8F0; }
        .msg-avatar { width: 38px; height: 38px; border-radius: 12px; display: flex;
          align-items: center; justify-content: center; color: #fff; flex-shrink: 0; font-size: 15px; }
        .msg-avatar-user { background: linear-gradient(135deg, #6366F1, #818CF8); }
        .msg-avatar-assistant { background: linear-gradient(135deg, #10B981, #34D399); }
        .msg-feedback-area { opacity: 0; transition: opacity 0.25s ease; }
        .msg-row:hover .msg-feedback-area { opacity: 1; }
      `}</style>

      <div style={{ display: 'flex', flexDirection: 'column', height: msgListHeight }}>
        {error && (
          <Alert title={error} type="error" closable onClose={() => setError(null)} style={{ marginBottom: 12 }} />
        )}
        <div style={{ flex: 1, overflow: 'auto', padding: '0 8px', marginBottom: 12, minHeight: compact ? 150 : 300 }}>
          {messages.length === 0 ? (
            <Empty description={knowledgePoint ? '正在加载AI讲解...' : '向AI导师提问'} style={{ marginTop: compact ? 40 : 80 }} />
          ) : (
            messages.map((msg, idx) => (
              <MessageBubble key={msg.id || idx} msg={msg} idx={idx} convId={conversationId} />
            ))
          )}
          {loading && (
            <div style={{ textAlign: 'center', margin: 8 }}>
              <Spin size="small" /><span style={{ marginLeft: 8, color: '#94A3B8' }}>AI思考中...</span>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div style={{ display: 'flex', gap: 8 }}>
          <Button icon={<ClearOutlined />} onClick={handleClear} disabled={messages.length === 0} size={compact ? 'small' : undefined}>
            清空
          </Button>
          <Input.TextArea
            value={input}
            onChange={e => setInput(e.target.value)}
            onPressEnter={e => { if (!e.shiftKey) { e.preventDefault(); handleSend(); } }}
            placeholder="输入问题，Enter 发送"
            autoSize={{ minRows: compact ? 1 : 2, maxRows: 4 }}
            disabled={loading}
            style={{ flex: 1 }}
          />
          <Button type="primary" icon={<SendOutlined />} onClick={handleSend}
            loading={loading} disabled={!input.trim()} size={compact ? 'small' : undefined}>
            发送
          </Button>
        </div>
      </div>
    </>
  );
};

export default ChatWindow;
