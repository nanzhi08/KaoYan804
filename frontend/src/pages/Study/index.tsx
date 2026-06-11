import React, { Suspense, lazy, useState } from "react";
import { useLocation } from "react-router-dom";
import { Tabs } from "antd";
import { ApartmentOutlined, EditOutlined, ExclamationCircleOutlined } from "@ant-design/icons";

const KnowledgeMap = lazy(() => import("../KnowledgeMap"));
const Practice = lazy(() => import("../Practice"));
const WrongRecords = lazy(() => import("../WrongRecords"));

const Loading = () => <div style={{ textAlign: "center", padding: 40 }}>加载中...</div>;

const TAB_ITEMS = [
  { key: "knowledge", label: <span><ApartmentOutlined /> 知识地图</span>, children: <Suspense fallback={<Loading />}><KnowledgeMap /></Suspense> },
  { key: "practice", label: <span><EditOutlined /> 刷题练习</span>, children: <Suspense fallback={<Loading />}><Practice /></Suspense> },
  { key: "wrong", label: <span><ExclamationCircleOutlined /> 错题本</span>, children: <Suspense fallback={<Loading />}><WrongRecords /></Suspense> },
];

const Study: React.FC = () => {
  const location = useLocation();
  const initialTab = (location.state as { tab?: string } | null)?.tab || "knowledge";
  const [activeTab, setActiveTab] = useState(initialTab);

  return (
    <Tabs activeKey={activeTab} onChange={setActiveTab} items={TAB_ITEMS} size="large" tabBarStyle={{ marginBottom: 16 }} />
  );
};

export default Study;
