import React, { useState, useRef, useEffect, useCallback, useMemo } from 'react';
import { Input, Button, Empty, Spin, Alert } from 'antd';
import { SendOutlined, RobotOutlined, UserOutlined, ClearOutlined } from '@ant-design/icons';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';
import type { KnowledgePoint, Message } from '../../types';
import FeedbackButton from './FeedbackButton';

interface ChatWindowProps {
  knowledgePoint?: KnowledgePoint | null;
  provider: string;
  initialMessage?: string;
  compact?: boolean;
}

/** Memoized code block to avoid re-rendering unchanged highlight blocks */
const CodeBlock = React.memo(({ language, code }: { language: string; code: string }) => (
  <SyntaxHighlighter
    style={oneDark}
    language={language || 'c'}
    PreTag="div"
    customStyle={{ borderRadius: 6, fontSize: 13 }}
  >
    {code}
  </SyntaxHighlighter>
));
CodeBlock.displayName = 'CodeBlock';

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
              code({ node, className, children, ...props }) {
                const match = /language-(\w+)/.exec(className || '');
                const codeText = String(children).replace(/\n$/, '');
                if (match || codeText.includes('\n')) {
                  return <CodeBlock language={match?.[1] || 'c'} code={codeText} />;
                }
                return <code className={className} {...props}>{children}</code>;
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

const ChatWindow: React.FC<ChatWindowProps> = ({ knowledgePoint, provider, initialMessage, compact }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [conversationId, setConversationId] = useState<number | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const rafRef = useRef<number | null>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  useEffect(() => {
    if (knowledgePoint) {
      setMessages([]);
      setConversationId(null);
      handleAIExplain(knowledgePoint);
    }
  }, [knowledgePoint?.id]);

  useEffect(() => {
    if (initialMessage) {
      handleSendWithMessage(initialMessage);
    }
  }, []);

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
            const data = JSON.parse(line.slice(6));
            if (data.error) throw new Error(data.error);
            if (data.chunk) fullText += data.chunk;
            if (data.conversation_id) convId = data.conversation_id;
            if (data.msg_id) msgId = data.msg_id;
          } catch (e: any) {
            if (e.message && !e.message.startsWith('Unexpected')) throw e;
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
    } catch (e: any) {
      setError(e.message || 'AI请求失败，请检查后端服务');
    } finally {
      setLoading(false);
    }
  }, []);

  const handleAIExplain = async (kp: KnowledgePoint) => {
    const explainMsg = `请帮我详细讲解【${kp.name}】这个知识点。`;
    const baseMessages: Message[] = [{ role: 'user', content: explainMsg }];
    setMessages(baseMessages);

    const params = new URLSearchParams({ kp_id: String(kp.id), provider });
    await streamResponse(
      fetch(`/api/ai/explain?${params}`, { method: 'POST' }),
      baseMessages,
    );
  };

  const handleSend = async () => {
    if (!input.trim() || loading) return;
    const userMsg = input.trim();
    setInput('');
    const newMessages: Message[] = [...messages, { role: 'user', content: userMsg }];
    setMessages(newMessages);

    await streamResponse(
      fetch('/api/ai/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          provider,
          message: userMsg,
          conversation_id: conversationId,
          knowledge_point_id: knowledgePoint?.id,
          messages,
        }),
      }),
      newMessages,
    );
  };

  const handleSendWithMessage = async (msg: string) => {
    const newMessages: Message[] = [...messages, { role: 'user', content: msg }];
    setMessages(newMessages);
    await streamResponse(
      fetch('/api/ai/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          provider,
          message: msg,
          conversation_id: conversationId,
          messages,
        }),
      }),
      newMessages,
    );
  };

  const handleClear = () => {
    setMessages([]);
    setConversationId(null);
    setError(null);
  };

  const msgListHeight = compact ? 260 : 'calc(100vh - 240px)';

  return (
    <>
      <style>{`
        .msg-row { display: flex; gap: 12px; margin-bottom: 16px; }
        .msg-bubble { padding: 12px 16px; border-radius: 10px; overflow: hidden; }
        .msg-bubble-user { background: #F0F1FC; }
        .msg-bubble-assistant { background: #F9F8F5; }
        .msg-avatar { width: 36px; height: 36px; border-radius: 50%; display: flex;
          align-items: center; justify-content: center; color: #fff; flex-shrink: 0; font-size: 14px; }
        .msg-avatar-user { background: #4A5BC9; }
        .msg-avatar-assistant { background: #3D8B5E; }
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
              <Spin size="small" /><span style={{ marginLeft: 8, color: '#9B9590' }}>AI思考中...</span>
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
