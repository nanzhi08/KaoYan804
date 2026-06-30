import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { Card, Form, Input, Button, Typography, App } from "antd";
import { UserOutlined, LockOutlined, BookOutlined } from "@ant-design/icons";
import { useAuthStore } from "../../stores/useAuthStore";

const { Title, Text } = Typography;

const LoginPage: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const login = useAuthStore((s) => s.login);
  const { message } = App.useApp();

  const onFinish = async (values: { username: string; password: string }) => {
    setLoading(true);
    try {
      await login(values.username, values.password);
      message.success("登录成功");
      navigate("/", { replace: true });
    } catch (e: unknown) {
      const msg = (e as { response?: { data?: { message?: string; detail?: string } } })?.response?.data?.message
        || (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail
        || "登录失败";
      message.error(msg);
    } finally {
      setLoading(false);
    }
  };

  const particles = [
    { left: "8%", bottom: "20%", size: 3, delay: "0s", duration: "5.5s" },
    { left: "18%", bottom: "55%", size: 4, delay: "1.3s", duration: "6.5s" },
    { left: "28%", bottom: "15%", size: 2, delay: "2.7s", duration: "5s" },
    { left: "45%", bottom: "70%", size: 5, delay: "0.6s", duration: "7s" },
    { left: "58%", bottom: "35%", size: 3, delay: "3.4s", duration: "6s" },
    { left: "72%", bottom: "60%", size: 4, delay: "1.9s", duration: "5.8s" },
    { left: "85%", bottom: "22%", size: 2, delay: "4.2s", duration: "6.2s" },
    { left: "38%", bottom: "82%", size: 3, delay: "2.1s", duration: "7.5s" },
  ];

  return (
    <div
      style={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        background: "linear-gradient(135deg, #EEF2FF 0%, #E8ECF4 25%, #E0E7FF 55%, #F0E6FF 80%, #EDE9FE 100%)",
        padding: 24,
        position: "relative",
        overflowY: "auto",
      }}
    >
      {/* Animated floating blobs */}
      <div style={{
        position: "absolute", top: "8%", left: "5%",
        width: 360, height: 360, borderRadius: "50%",
        background: "radial-gradient(circle, rgba(99,102,241,0.13), transparent 70%)",
        animation: "blobMorph 14s ease-in-out infinite, blobDrift1 20s ease-in-out infinite",
      }} />
      <div style={{
        position: "absolute", bottom: "12%", right: "6%",
        width: 460, height: 460, borderRadius: "50%",
        background: "radial-gradient(circle, rgba(139,92,246,0.09), transparent 70%)",
        animation: "blobMorph 16s ease-in-out infinite 1s, blobDrift2 22s ease-in-out infinite",
      }} />
      <div style={{
        position: "absolute", top: "42%", right: "22%",
        width: 220, height: 220, borderRadius: "50%",
        background: "radial-gradient(circle, rgba(16,185,129,0.07), transparent 70%)",
        animation: "blobDrift3 16s ease-in-out infinite 0.5s",
      }} />

      {/* Floating particles */}
      {particles.map((p, i) => (
        <div key={i} style={{
          position: "absolute",
          left: p.left, bottom: p.bottom,
          width: p.size, height: p.size,
          borderRadius: "50%",
          background: "rgba(99, 102, 241, 0.22)",
          animation: `particleRise ${p.duration} ease-in-out infinite`,
          animationDelay: p.delay,
        }} />
      ))}

      <Card
        className="auth-card-enter"
        style={{
          width: 420,
          maxWidth: "100%",
          borderRadius: 20,
          boxShadow: "0 20px 60px rgba(99,102,241,0.08), 0 4px 16px rgba(0,0,0,0.04), 0 0 0 1px rgba(99,102,241,0.06)",
          background: "rgba(255,255,255,0.88)",
          backdropFilter: "blur(24px) saturate(180%)",
          WebkitBackdropFilter: "blur(24px) saturate(180%)",
          position: "relative",
          zIndex: 1,
        }}
      >
        <div style={{ textAlign: "center", marginBottom: 32 }}>
          <div style={{
            width: 72, height: 72, margin: "0 auto 16px",
            borderRadius: 18, background: "linear-gradient(135deg, #6366F1, #8B5CF6)",
            display: "flex", alignItems: "center", justifyContent: "center",
            animation: "iconPulse 3s ease-in-out infinite",
          }}>
            <BookOutlined style={{ fontSize: 32, color: "#fff" }} />
          </div>
          <Title level={4} style={{ marginBottom: 4, fontWeight: 700, color: "#1E293B" }}>
            欢迎回来
          </Title>
          <Title level={3} style={{ marginTop: 0, marginBottom: 8, fontWeight: 800, color: "#0F172A" }}>
            考研804知识库
          </Title>
          <Text type="secondary">登录以继续学习</Text>
        </div>

        <Form
          name="login"
          onFinish={onFinish}
          layout="vertical"
          size="large"
          initialValues={{ username: "", password: "" }}
        >
          <Form.Item
            name="username"
            rules={[{ required: true, message: "请输入用户名" }]}
          >
            <Input prefix={<UserOutlined style={{ color: "#94A3B8" }} />} placeholder="用户名" />
          </Form.Item>

          <Form.Item
            name="password"
            rules={[{ required: true, message: "请输入密码" }]}
          >
            <Input.Password prefix={<LockOutlined style={{ color: "#94A3B8" }} />} placeholder="密码" />
          </Form.Item>

          <Form.Item>
            <Button type="primary" htmlType="submit" block loading={loading}
              style={{ height: 44, borderRadius: 12, fontWeight: 600, fontSize: 15 }}
            >
              登录
            </Button>
          </Form.Item>
        </Form>

        <div style={{ textAlign: "center" }}>
          <Text type="secondary">
            没有账号？{" "}
            <Link to="/register" style={{ fontWeight: 500, color: "#6366F1" }}>立即注册</Link>
          </Text>
        </div>
      </Card>

      <div style={{ position: "absolute", bottom: 24, left: 0, right: 0, textAlign: "center", zIndex: 1 }}>
        <Text style={{ color: "rgba(100,116,139,0.5)", fontSize: 12 }}>
          804考研辅导平台
        </Text>
      </div>
    </div>
  );
};

export default LoginPage;
