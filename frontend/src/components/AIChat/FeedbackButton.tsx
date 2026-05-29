import React, { useState } from 'react';
import { Tooltip } from 'antd';
import { LikeOutlined, LikeFilled, DislikeOutlined, DislikeFilled } from '@ant-design/icons';
import { aiFeedbackApi } from '../../services/api';

interface Props {
  messageId: string;
  conversationId: number;
  messageIndex: number;
}

const FeedbackButton: React.FC<Props> = ({ messageId, conversationId, messageIndex }) => {
  const [rating, setRating] = useState<number>(0);
  const [submitting, setSubmitting] = useState(false);
  const [animating, setAnimating] = useState<'like' | 'dislike' | null>(null);

  const handleRate = async (r: number) => {
    if (submitting) return;
    const newRating = rating === r ? 0 : r;
    setRating(newRating);
    if (newRating !== 0) {
      setAnimating(r === 1 ? 'like' : 'dislike');
      setTimeout(() => setAnimating(null), 500);
    }
    setSubmitting(true);
    try {
      await aiFeedbackApi.submit({
        conversation_id: conversationId,
        message_id: messageId,
        message_index: messageIndex,
        rating: newRating,
      });
    } catch {
      setRating(0);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="feedback-actions">
      <span className="feedback-divider" />
      <Tooltip title={rating === 1 ? '取消标记' : '有帮助'} mouseEnterDelay={0.5}>
        <button
          className={`feedback-btn ${rating === 1 ? 'active like' : ''} ${animating === 'like' ? 'pop' : ''}`}
          onClick={() => handleRate(1)}
          disabled={submitting}
        >
          {rating === 1 ? <LikeFilled /> : <LikeOutlined />}
        </button>
      </Tooltip>
      <Tooltip title={rating === -1 ? '取消标记' : '没帮助'} mouseEnterDelay={0.5}>
        <button
          className={`feedback-btn ${rating === -1 ? 'active dislike' : ''} ${animating === 'dislike' ? 'pop' : ''}`}
          onClick={() => handleRate(-1)}
          disabled={submitting}
        >
          {rating === -1 ? <DislikeFilled /> : <DislikeOutlined />}
        </button>
      </Tooltip>
      <style>{`
        .feedback-actions {
          display: flex;
          align-items: center;
          justify-content: flex-end;
          gap: 4px;
          margin-top: 10px;
          opacity: 0;
          transition: opacity 0.3s ease;
        }
        .feedback-actions:hover,
        .feedback-actions:has(.active) {
          opacity: 1;
        }
        .feedback-divider {
          flex: 1;
          height: 0;
          border-top: 1px dotted #D4CFC6;
          margin-right: 8px;
          transition: border-color 0.3s ease;
        }
        .feedback-btn {
          display: inline-flex;
          align-items: center;
          justify-content: center;
          width: 28px;
          height: 28px;
          border: none;
          border-radius: 50%;
          background: transparent;
          color: #B5B0A8;
          cursor: pointer;
          font-size: 13px;
          transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
          outline: none;
          position: relative;
        }
        .feedback-btn:hover {
          color: #7A7368;
          background: rgba(0, 0, 0, 0.04);
        }
        .feedback-btn:active {
          transform: scale(0.88);
        }
        .feedback-btn.active.like {
          color: #3D8B5E;
          background: rgba(61, 139, 94, 0.08);
          box-shadow: 0 0 0 1px rgba(61, 139, 94, 0.15);
        }
        .feedback-btn.active.like:hover {
          background: rgba(61, 139, 94, 0.14);
        }
        .feedback-btn.active.dislike {
          color: #C56C6C;
          background: rgba(197, 108, 108, 0.08);
          box-shadow: 0 0 0 1px rgba(197, 108, 108, 0.15);
        }
        .feedback-btn.active.dislike:hover {
          background: rgba(197, 108, 108, 0.14);
        }
        .feedback-btn.pop {
          animation: feedbackPop 0.45s cubic-bezier(0.4, 0, 0.2, 1);
        }
        @keyframes feedbackPop {
          0%   { transform: scale(1); }
          30%  { transform: scale(1.35); }
          60%  { transform: scale(0.85); }
          100% { transform: scale(1); }
        }
      `}</style>
    </div>
  );
};

export default FeedbackButton;
