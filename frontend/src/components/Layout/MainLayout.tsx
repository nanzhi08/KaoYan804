import React, { Suspense, lazy, useState, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { Layout, Menu, Drawer, Button, Tag, Spin, Space } from "antd";
import {
  DashboardOutlined,
  ReadOutlined,
  FormOutlined,
  MenuOutlined,
  RiseOutlined,
  SettingOutlined,
} from "@ant-design/icons";

import KeepAlive from "./KeepAlive";
import { useAuthStore } from "../../stores/useAuthStore";

const { Sider, Content, Header } = Layout;

const Dashboard = lazy(() => import("../../pages/Dashboard"));
const Study = lazy(() => import("../../pages/Study"));
const Review = lazy(() => import("../../pages/Review"));
const MockExam = lazy(() => import("../../pages/MockExam"));
const AdminPage = lazy(() => import("../../pages/Admin"));

const useMenuItems = () => {
  const isAdmin = useAuthStore((s) => s.isAdmin);
  const items = [
    { key: "/", icon: <DashboardOutlined />, label: "首页" },
    { key: "/study", icon: <ReadOutlined />, label: "学习" },
    { key: "/review", icon: <RiseOutlined />, label: "复习" },
    { key: "/mock-exam", icon: <FormOutlined />, label: "模拟考试" },
  ];
  if (isAdmin) {
    items.push({ key: "/admin", icon: <SettingOutlined />, label: "管理" });
  }
  return items;
};

interface PageConfig {
  path: string;
  Component: React.LazyExoticComponent<React.ComponentType>;
}

const pages: PageConfig[] = [
  { path: "/", Component: Dashboard },
  { path: "/study", Component: Study },
  { path: "/review", Component: Review },
  { path: "/mock-exam", Component: MockExam },
  { path: "/admin", Component: AdminPage },
];

const SIDEBAR_WIDTH = 200;

const PageLoading: React.FC = () => (
  <div style={{ display: "grid", minHeight: 280, placeItems: "center" }}>
    <Spin />
  </div>
);

function getMenuSelectedKey(pathname: string, menuItems: { key: string }[]): string {
  if (pathname === "/") return "/";
  const firstSegment = "/" + pathname.split("/")[1];
  const validPaths = menuItems.map((m) => m.key);
  return validPaths.includes(firstSegment) ? firstSegment : "/";
}

const SidebarMenu: React.FC<{ onItemClick?: () => void }> = ({ onItemClick }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const menuItems = useMenuItems();

  const handleClick = (key: string) => {
    navigate(key);
    onItemClick?.();
  };

  return (
    <Menu
      theme="dark"
      mode="inline"
      selectedKeys={[getMenuSelectedKey(location.pathname, menuItems)]}
      items={menuItems}
      onClick={({ key }) => handleClick(key)}
      style={{
        marginTop: 8,
        background: "transparent",
        borderRight: 0,
      }}
    />
  );
};

const HeaderUser: React.FC = () => {
  const { user, isAdmin, logout } = useAuthStore();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login", { replace: true });
  };

  if (!user) return null;

  return (
    <Space size={8}>
      <Tag color={isAdmin ? "red" : "blue"}>{user.username}</Tag>
      {isAdmin && <Tag color="gold">管理员</Tag>}
      <Button type="text" size="small" onClick={handleLogout} style={{ color: "#64748B" }}>
        退出登录
      </Button>
    </Space>
  );
};

const MainLayout: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [mobileDrawerOpen, setMobileDrawerOpen] = useState(false);
  const [isMobile, setIsMobile] = useState(window.innerWidth <= 768);
  const isAdmin = useAuthStore((s) => s.isAdmin);

  useEffect(() => {
    const onResize = () => setIsMobile(window.innerWidth <= 768);
    window.addEventListener("resize", onResize);
    return () => window.removeEventListener("resize", onResize);
  }, []);

  const filteredPages = pages.filter(p => p.path !== "/admin" || isAdmin);

  useEffect(() => {
    if (location.pathname.startsWith("/admin") && !isAdmin) {
      navigate("/", { replace: true });
    }
  }, [location.pathname, isAdmin, navigate]);

  function isPageActive(path: string): boolean {
    if (path === "/") return location.pathname === "/";
    return location.pathname === path || location.pathname.startsWith(path + "/");
  }

  return (
    <Layout style={{ minHeight: "100vh" }}>
      {/* Desktop Sidebar */}
      {!isMobile && (
        <Sider
          width={SIDEBAR_WIDTH}
          style={{
            background: "#0F172A",
            overflow: "auto",
            height: "100vh",
            position: "fixed",
            left: 0,
            top: 0,
            bottom: 0,
            zIndex: 10,
            borderRight: "1px solid rgba(255,255,255,0.06)",
          }}
        >
          <div style={{
            height: 64,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            gap: 8,
            color: "#E2E8F0",
            fontSize: 16,
            fontWeight: 600,
            fontFamily: "'Noto Sans SC', sans-serif",
            letterSpacing: 1,
            background: "linear-gradient(180deg, rgba(99,102,241,0.08) 0%, transparent 100%)",
            borderBottom: "1px solid rgba(255,255,255,0.06)",
          }}>
            <span style={{ fontSize: 20 }}>&#x1F4DA;</span> 考研804知识库
          </div>
          <SidebarMenu />
        </Sider>
      )}

      {/* Mobile Drawer */}
      {isMobile && (
        <Drawer
          placement="left"
          size={SIDEBAR_WIDTH}
          open={mobileDrawerOpen}
          onClose={() => setMobileDrawerOpen(false)}
          styles={{
            body: { padding: 0, background: "#0F172A" },
            header: { background: "#0F172A", borderBottom: "1px solid rgba(255,255,255,0.06)" },
          }}
          title={<span style={{ color: "#E2E8F0", fontFamily: "'Noto Sans SC', sans-serif", fontSize: 16, fontWeight: 600 }}>考研804知识库</span>}
          closeIcon={<span style={{ color: "#fff" }}>&#x2715;</span>}
        >
          <SidebarMenu onItemClick={() => setMobileDrawerOpen(false)} />
        </Drawer>
      )}

      {/* Main Content Area */}
      <Layout style={{ marginLeft: isMobile ? 0 : SIDEBAR_WIDTH }}>
        <Header style={{
          background: "rgba(248,250,252,0.8)",
          backdropFilter: "blur(20px) saturate(180%)",
          WebkitBackdropFilter: "blur(20px) saturate(180%)",
          padding: isMobile ? "0 12px" : "0 28px",
          boxShadow: "0 1px 3px rgba(0,0,0,0.04)",
          display: "flex",
          alignItems: "center",
          gap: 12,
          fontSize: isMobile ? 13 : 14,
          fontWeight: 500,
          color: "#0F172A",
          position: "sticky",
          top: 0,
          zIndex: 9,
          height: 52,
          borderBottom: "1px solid #E2E8F0",
        }}>
          {isMobile && (
            <Button
              type="text"
              icon={<MenuOutlined />}
              onClick={() => setMobileDrawerOpen(true)}
              style={{ color: "#0F172A", fontSize: 18 }}
            />
          )}
          <span style={{ flex: 1 }}>
            {isMobile ? "804知识库" : "804 数据结构与高级程序设计"}
          </span>
          {!isMobile && <HeaderUser />}
        </Header>

        <Content style={{
          margin: isMobile ? 12 : 28,
          minHeight: 280,
          position: "relative",
        }}>
          {filteredPages.map(({ path, Component }) => (
            <KeepAlive
              key={path}
              active={isPageActive(path)}
            >
              <Suspense fallback={<PageLoading />}>
                <Component />
              </Suspense>
            </KeepAlive>
          ))}
        </Content>
      </Layout>
    </Layout>
  );
};

export default MainLayout;
