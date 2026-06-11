import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { ConfigProvider, App as AntdApp } from 'antd';
import zhCN from 'antd/locale/zh_CN';

import MainLayout from './components/Layout/MainLayout';

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
      <BrowserRouter>
        <Routes>
          <Route path="*" element={<MainLayout />} />
        </Routes>
      </BrowserRouter>
    </AntdApp>
  </ConfigProvider>
);

export default App;
