import React, { useEffect, lazy, Suspense } from 'react';
import { BrowserRouter, Routes, Route, useNavigate } from 'react-router-dom';
import { ConfigProvider, App as AntdApp, Spin } from 'antd';
import zhCN from 'antd/locale/zh_CN';

import MainLayout from './components/Layout/MainLayout';
import { useAuthStore } from './stores/useAuthStore';
import { setMessageApi } from './services/api';

const AuthGuard: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, loading, init } = useAuthStore();
  const navigate = useNavigate();

  useEffect(() => {
    init();
  }, []);

  useEffect(() => {
    if (!loading && !isAuthenticated) {
      navigate("/login", { replace: true });
    }
  }, [loading, isAuthenticated, navigate]);

  if (loading) {
    return (
      <div style={{ display: "flex", justifyContent: "center", alignItems: "center", minHeight: "100vh" }}>
        <Spin size="large" />
      </div>
    );
  }

  return isAuthenticated ? <>{children}</> : null;
};

const LoginPage = lazy(() => import("./pages/Login"));
const RegisterPage = lazy(() => import("./pages/Register"));

const AppInner: React.FC = () => {
  const { message } = AntdApp.useApp();

  useEffect(() => {
    setMessageApi(message);
    return () => setMessageApi(null as unknown as typeof message);
  }, [message]);

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Suspense fallback={<div style={{ display: "flex", justifyContent: "center", alignItems: "center", minHeight: "100vh" }}><Spin size="large" /></div>}><LoginPage /></Suspense>} />
        <Route path="/register" element={<Suspense fallback={<div style={{ display: "flex", justifyContent: "center", alignItems: "center", minHeight: "100vh" }}><Spin size="large" /></div>}><RegisterPage /></Suspense>} />
        <Route path="*" element={<AuthGuard><MainLayout /></AuthGuard>} />
      </Routes>
    </BrowserRouter>
  );
};

const App: React.FC = () => (
  <ConfigProvider locale={zhCN} theme={{
    token: {
      colorPrimary: '#6366F1',
      colorSuccess: '#10B981',
      colorWarning: '#F59E0B',
      colorError: '#EF4444',
      colorInfo: '#6366F1',
      borderRadius: 10,
      borderRadiusLG: 14,
      borderRadiusSM: 8,
      colorBgContainer: '#FFFFFF',
      colorBgLayout: '#F8FAFC',
      colorBgElevated: '#FFFFFF',
      colorText: '#0F172A',
      colorTextSecondary: '#64748B',
      colorTextTertiary: '#94A3B8',
      colorBorder: '#E2E8F0',
      colorBorderSecondary: '#F1F5F9',
      fontFamily: "'Noto Sans SC', -apple-system, BlinkMacSystemFont, sans-serif",
      fontSize: 14,
      lineHeight: 1.7,
      controlHeight: 36,
      controlHeightLG: 44,
      paddingContentHorizontal: 20,
      boxShadow: '0 1px 3px rgba(0, 0, 0, 0.04), 0 1px 2px rgba(0, 0, 0, 0.03)',
      boxShadowSecondary: '0 4px 6px -1px rgba(0, 0, 0, 0.06), 0 2px 4px -2px rgba(0, 0, 0, 0.05)',
    },
    components: {
      Button: {
        borderRadius: 9999,
        borderRadiusLG: 9999,
        borderRadiusSM: 9999,
        controlHeight: 36,
        controlHeightLG: 44,
        controlHeightSM: 28,
        fontWeight: 500,
        paddingInline: 18,
        paddingInlineLG: 24,
        paddingInlineSM: 12,
      },
      Card: {
        borderRadiusLG: 14,
        paddingLG: 24,
      },
      Table: {
        borderRadius: 12,
        borderRadiusLG: 12,
        headerBg: '#F8FAFC',
      },
      Menu: {
        darkItemBg: '#0F172A',
        darkSubMenuItemBg: '#0F172A',
        darkItemSelectedBg: 'rgba(99, 102, 241, 0.18)',
        itemBorderRadius: 10,
      },
      Statistic: {
        titleFontSize: 13,
        contentFontSize: 28,
      },
      Tag: {
        borderRadiusSM: 6,
      },
      Progress: {
        borderRadius: 9999,
      },
      Modal: {
        borderRadiusLG: 16,
      },
      Input: {
        borderRadius: 10,
        borderRadiusLG: 12,
      },
      Select: {
        borderRadius: 10,
      },
      Tabs: {
        itemColor: '#64748B',
        itemSelectedColor: '#6366F1',
        inkBarColor: '#6366F1',
      },
    },
  }}>
    <AntdApp>
      <AppInner />
    </AntdApp>
  </ConfigProvider>
);

export default App;
