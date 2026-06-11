import React, { Suspense, lazy, useState } from "react";
import { Tabs } from "antd";
import { RobotOutlined, HistoryOutlined } from "@ant-design/icons";
import ChatWindow from "../../components/AIChat/ChatWindow";
import ModelSelector from "../../components/AIChat/ModelSelector";

const AIHistory = lazy(() => import("../AIHistory"));

const Loading = () => <div style={{ textAlign: "center", padding: 40 }}>加载中...</div>;

const AITutor: React.FC = () => {
  const [provider, setProvider] = useState("deepseek");
  const [activeTab, setActiveTab] = useState("chat");

  const tabItems = [
    {
      key: "chat",
      label: <span><RobotOutlined /> AI对话</span>,
      children: <ChatWindow provider={provider} />,
    },
    {
      key: "history",
      label: <span><HistoryOutlined /> 历史记录</span>,
      children: (
        <Suspense fallback={<Loading />}>
          <AIHistory />
        </Suspense>
      ),
    },
  ];

  return (
    <Tabs
      activeKey={activeTab}
      onChange={setActiveTab}
      tabBarExtraContent={<ModelSelector value={provider} onChange={setProvider} />}
      items={tabItems}
      size="large"
      tabBarStyle={{ marginBottom: 16 }}
    />
  );
};

export default AITutor;
