import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { ConfigProvider, App as AntdApp } from 'antd';
import zhCN from 'antd/locale/zh_CN';

import MainLayout from './components/Layout/MainLayout';

const App: React.FC = () => (
  <ConfigProvider locale={zhCN} theme={{
    token: {
      colorPrimary: '#4A5BC9',
      colorSuccess: '#3D8B5E',
      colorWarning: '#D4953A',
      colorError: '#C56C6C',
      colorInfo: '#4A5BC9',
      borderRadius: 10,
      colorBgContainer: '#FFFFFF',
      colorBgLayout: '#FAF7F2',
      colorText: '#2C2C2C',
      colorTextSecondary: '#6B6560',
      colorBorder: '#E8E3DC',
      fontFamily: "'Noto Sans SC', -apple-system, BlinkMacSystemFont, sans-serif",
      fontSize: 14,
      lineHeight: 1.7,
      controlHeight: 36,
      paddingContentHorizontal: 20,
      boxShadow: '0 2px 16px rgba(0, 0, 0, 0.04)',
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
