import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Layout, Menu, Drawer, Button } from 'antd';
import {
  DashboardOutlined,
  ApartmentOutlined,
  EditOutlined,
  RobotOutlined,
  FileTextOutlined,
  FormOutlined,
  ExclamationCircleOutlined,
  MenuOutlined,
  HistoryOutlined,
} from '@ant-design/icons';

import KeepAlive from './KeepAlive';
import Dashboard from '../../pages/Dashboard';
import KnowledgeMap from '../../pages/KnowledgeMap';
import Practice from '../../pages/Practice';
import AITutor from '../../pages/AITutor';
import MockExam from '../../pages/MockExam';
import Documents from '../../pages/Documents';
import WrongRecords from '../../pages/WrongRecords';
import AIHistory from '../../pages/AIHistory';

const { Sider, Content, Header } = Layout;

const menuItems = [
  { key: '/', icon: <DashboardOutlined />, label: '学习仪表盘' },
  { key: '/knowledge-map', icon: <ApartmentOutlined />, label: '知识地图' },
  { key: '/practice', icon: <EditOutlined />, label: '刷题练习' },
  { key: '/wrong-records', icon: <ExclamationCircleOutlined />, label: '错题记录' },
  { key: '/ai-tutor', icon: <RobotOutlined />, label: 'AI导师' },
  { key: '/ai-history', icon: <HistoryOutlined />, label: '历史回答' },
  { key: '/mock-exam', icon: <FormOutlined />, label: '模拟考试' },
  { key: '/documents', icon: <FileTextOutlined />, label: '资料管理' },
];

interface PageConfig {
  path: string;
  component: React.ReactNode;
}

const pages: PageConfig[] = [
  { path: '/', component: <Dashboard /> },
  { path: '/knowledge-map', component: <KnowledgeMap /> },
  { path: '/practice', component: <Practice /> },
  { path: '/wrong-records', component: <WrongRecords /> },
  { path: '/ai-tutor', component: <AITutor /> },
  { path: '/ai-history', component: <AIHistory /> },
  { path: '/mock-exam', component: <MockExam /> },
  { path: '/documents', component: <Documents /> },
];

const SIDEBAR_WIDTH = 200;

const SidebarMenu: React.FC<{ onItemClick?: () => void }> = ({ onItemClick }) => {
  const navigate = useNavigate();
  const location = useLocation();

  const handleClick = (key: string) => {
    navigate(key);
    onItemClick?.();
  };

  return (
    <Menu
      theme="dark"
      mode="inline"
      selectedKeys={[location.pathname === '/' ? '/' : `/${location.pathname.split('/')[1]}`]}
      items={menuItems}
      onClick={({ key }) => handleClick(key)}
      style={{
        marginTop: 8,
        background: 'transparent',
        borderRight: 0,
      }}
    />
  );
};

const MainLayout: React.FC = () => {
  const location = useLocation();
  const [mobileDrawerOpen, setMobileDrawerOpen] = useState(false);
  const [isMobile, setIsMobile] = useState(window.innerWidth <= 768);

  useEffect(() => {
    const onResize = () => setIsMobile(window.innerWidth <= 768);
    window.addEventListener('resize', onResize);
    return () => window.removeEventListener('resize', onResize);
  }, []);

  return (
    <Layout style={{ minHeight: '100vh' }}>
      {/* Desktop Sidebar */}
      {!isMobile && (
        <Sider
          width={SIDEBAR_WIDTH}
          style={{
            background: '#2A2D35',
            overflow: 'auto',
            height: '100vh',
            position: 'fixed',
            left: 0,
            top: 0,
            bottom: 0,
            zIndex: 10,
            borderRight: '1px solid rgba(255,255,255,0.06)',
          }}
        >
          <div style={{
            height: 64,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: 8,
            color: '#fff',
            fontSize: 17,
            fontFamily: "'LXGW WenKai', 'KaiTi', serif",
            letterSpacing: 2,
            borderBottom: '1px solid rgba(255,255,255,0.08)',
          }}>
            考研804知识库
          </div>
          <SidebarMenu />
        </Sider>
      )}

      {/* Mobile Drawer */}
      {isMobile && (
        <Drawer
          placement="left"
          width={SIDEBAR_WIDTH}
          open={mobileDrawerOpen}
          onClose={() => setMobileDrawerOpen(false)}
          styles={{
            body: { padding: 0, background: '#2A2D35' },
            header: { background: '#2A2D35', borderBottom: '1px solid rgba(255,255,255,0.08)' },
          }}
          title={<span style={{ color: '#fff', fontFamily: "'LXGW WenKai', 'KaiTi', serif", fontSize: 16 }}>考研804知识库</span>}
          closeIcon={<span style={{ color: '#fff' }}>✕</span>}
        >
          <SidebarMenu onItemClick={() => setMobileDrawerOpen(false)} />
        </Drawer>
      )}

      {/* Main Content Area */}
      <Layout style={{ marginLeft: isMobile ? 0 : SIDEBAR_WIDTH }}>
        <Header style={{
          background: 'rgba(255,255,255,0.85)',
          backdropFilter: 'blur(12px)',
          padding: isMobile ? '0 12px' : '0 28px',
          boxShadow: '0 1px 8px rgba(0,0,0,0.04)',
          display: 'flex',
          alignItems: 'center',
          gap: 12,
          fontSize: isMobile ? 13 : 15,
          fontWeight: 500,
          color: '#2C2C2C',
          letterSpacing: 1,
          position: 'sticky',
          top: 0,
          zIndex: 9,
          height: 56,
          borderBottom: '1px solid #F0ECE5',
        }}>
          {isMobile && (
            <Button
              type="text"
              icon={<MenuOutlined />}
              onClick={() => setMobileDrawerOpen(true)}
              style={{ color: '#2C2C2C', fontSize: 18 }}
            />
          )}
          <span style={{ flex: 1 }}>
            {isMobile ? '804知识库' : '上海第二工业大学 · 804 数据结构与高级程序设计'}
          </span>
        </Header>

        <Content style={{
          margin: isMobile ? 12 : 28,
          minHeight: 280,
        }}>
          {pages.map(({ path, component }) => (
            <KeepAlive
              key={path}
              active={
                location.pathname === path ||
                (path !== '/' && location.pathname.startsWith(path))
              }
            >
              {component}
            </KeepAlive>
          ))}
        </Content>
      </Layout>
    </Layout>
  );
};

export default MainLayout;
