import React, { useState, useEffect } from 'react';
import { Card, Row, Col } from 'antd';
import { RobotOutlined } from '@ant-design/icons';
import { useLocation } from 'react-router-dom';
import ChatWindow from '../../components/AIChat/ChatWindow';
import ModelSelector from '../../components/AIChat/ModelSelector';
import type { KnowledgePoint } from '../../types';

const AITutor: React.FC = () => {
  const [provider, setProvider] = useState('deepseek');
  const location = useLocation();
  const [knowledgePoint, setKnowledgePoint] = useState<KnowledgePoint | null>(null);

  useEffect(() => {
    const state = location.state as { knowledgePoint?: KnowledgePoint } | null;
    if (state?.knowledgePoint) {
      setKnowledgePoint(state.knowledgePoint);
      window.history.replaceState({}, document.title);
    }
  }, []);

  return (
    <Card
      title={
        <Row justify="space-between" align="middle" style={{ width: '100%' }}>
          <Col>
            <RobotOutlined style={{ marginRight: 8 }} />
            AI 导师
            {knowledgePoint && (
              <span style={{ fontSize: 14, color: '#666', marginLeft: 12 }}>
                正在讲解：{knowledgePoint.name}
              </span>
            )}
          </Col>
          <Col>
            <ModelSelector value={provider} onChange={setProvider} />
          </Col>
        </Row>
      }
    >
      <ChatWindow knowledgePoint={knowledgePoint} provider={provider} />
    </Card>
  );
};

export default AITutor;
