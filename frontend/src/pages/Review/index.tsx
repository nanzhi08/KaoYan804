import React, { Suspense, lazy, useState, useEffect } from "react";
import { useLocation } from "react-router-dom";
import { Tabs } from "antd";
import { ScheduleOutlined, BarChartOutlined } from "@ant-design/icons";

const ReviewPlan = lazy(() => import("../ReviewPlan"));
const ProgressPage = lazy(() => import("../Progress"));

const Loading = () => (
  <div style={{ display: "flex", justifyContent: "center", alignItems: "center", minHeight: 300 }}>
    <span style={{ color: "#94A3B8" }}>加载中...</span>
  </div>
);

const TAB_ITEMS = [
  {
    key: "plan",
    label: <span><ScheduleOutlined /> 复习计划</span>,
    children: <Suspense fallback={<Loading />}><ReviewPlan /></Suspense>,
  },
  {
    key: "stats",
    label: <span><BarChartOutlined /> 学习统计</span>,
    children: <Suspense fallback={<Loading />}><ProgressPage /></Suspense>,
  },
];

const Review: React.FC = () => {
  const location = useLocation();
  const initialTab = (location.state as { tab?: string } | null)?.tab || "plan";
  const [activeTab, setActiveTab] = useState(initialTab);

  useEffect(() => {
    const tab = (location.state as { tab?: string } | null)?.tab;
    if (tab) {
      setActiveTab(tab);
    }
  }, [location.state]);

  return (
    <Tabs
      activeKey={activeTab}
      onChange={setActiveTab}
      items={TAB_ITEMS}
      size="large"
      tabBarStyle={{
        marginBottom: 0,
        padding: "0 4px",
        background: "#FFFFFF",
        borderRadius: "12px 12px 0 0",
        border: "1px solid #E2E8F0",
        borderBottom: "none",
      }}
    />
  );
};

export default Review;
