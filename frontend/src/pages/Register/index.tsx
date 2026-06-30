import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { Card, Form, Input, Button, Typography, App } from "antd";
import { UserOutlined, LockOutlined, KeyOutlined, BookOutlined } from "@ant-design/icons";
import { useAuthStore } from "../../stores/useAuthStore";

const { Title, Text } = Typography;

const RegisterPage: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const register = useAuthStore((s) => s.register);
  const { message } = App.useApp();

  const onFinish = async (values: {
    username: string;
    password: string;
    confirmPassword: string;
    inviteCode: string;
  }) => {
    if (values.password !== values.confirmPassword) {
      message.error("两次输入的密码不一致");
      return;
    }
    setLoading(true);
    try {
      await register(values.username, values.password, values.inviteCode);
      message.success("注册成功！");
      navigate("/", { replace: true });
    } catch (e: unknown) {
      let msg = "注册失败";
      if (e instanceof Error) {
        msg = e.message || msg;
      } else {
        msg = (e as { response?: { data?: { message?: string; detail?: string } } })?.response?.data?.message
          || (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail
          || msg;
      }
      message.error(msg);
    } finally {
      setLoading(false);
    }
  };

  const particles = [
    { left: "10%", bottom: "25%", size: 3, delay: "0s", duration: "5.2s" },
    { left: "22%", bottom: "58%", size: 4, delay: "1.5s", duration: "6.8s" },
    { left: "35%", bottom: "18%", size: 2, delay: "2.9s", duration: "5.5s" },
    { left: "50%", bottom: "72%", size: 5, delay: "0.8s", duration: "7.2s" },
    { left: "64%", bottom: "40%", size: 3, delay: "3.6s", duration: "6s" },
    { left: "76%", bottom: "62%", size: 4, delay: "2.1s", duration: "5.8s" },
    { left: "88%", bottom: "28%", size: 2, delay: "4.5s", duration: "6.5s" },
    { left: "42%", bottom: "85%", size: 3, delay: "1.8s", duration: "7s" },
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
        position: "absolute", top: "6%", right: "8%",
        width: 340, height: 340, borderRadius: "50%",
        background: "radial-gradient(circle, rgba(99,102,241,0.12), transparent 70%)",
        animation: "blobMorph 15s ease-in-out infinite 0.5s, blobDrift1 21s ease-in-out infinite",
      }} />
      <div style={{
        position: "absolute", bottom: "10%", left: "5%",
        width: 440, height: 440, borderRadius: "50%",
        background: "radial-gradient(circle, rgba(139,92,246,0.08), transparent 70%)",
        animation: "blobMorph 17s ease-in-out infinite 1.5s, blobDrift2 23s ease-in-out infinite",
      }} />
      <div style={{
        position: "absolute", top: "38%", left: "22%",
        width: 200, height: 200, borderRadius: "50%",
        background: "radial-gradient(circle, rgba(16,185,129,0.07), transparent 70%)",
        animation: "blobDrift3 15s ease-in-out infinite 1s",
      }} />

      {/* Floating particles */}
      {particles.map((p, i) => (
        <div key={i} style={{
          position: "absolute",
          left: p.left, bottom: p.bottom,
          width: p.size, height: p.size,
          borderRadius: "50%",
          background: "rgba(99, 102, 241, 0.2)",
          animation: `particleRise ${p.duration} ease-in-out infinite`,
          animationDelay: p.delay,
        }} />
      ))}

      <Card
        className="auth-card-enter"
        style={{
          width: 440,
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
        <div style={{ textAlign: "center", marginBottom: 28 }}>
          <div style={{
            width: 72, height: 72, margin: "0 auto 16px",
            borderRadius: 18, background: "linear-gradient(135deg, #10B981, #059669)",
            display: "flex", alignItems: "center", justifyContent: "center",
            animation: "iconPulseGreen 3s ease-in-out infinite",
          }}>
            <BookOutlined style={{ fontSize: 32, color: "#fff" }} />
          </div>
          <Title level={4} style={{ marginBottom: 4, fontWeight: 700, color: "#1E293B" }}>
            创建账号
          </Title>
          <Title level={3} style={{ marginTop: 0, marginBottom: 8, fontWeight: 800, color: "#0F172A" }}>
            加入考研804知识库
          </Title>
          <Text type="secondary">使用管理员提供的邀请码注册</Text>
        </div>

        {/* Step indicator (visual) */}
        <div style={{ display: "flex", justifyContent: "center", marginBottom: 24, gap: 4 }}>
          {["填写信息", "验证邀请码", "开始学习"].map((label, i) => (
            <div key={label} style={{ display: "flex", alignItems: "center", gap: 4 }}>
              <div style={{
                width: 28, height: 28, borderRadius: "50%",
                background: i <= 1 ? "#6366F1" : "#E2E8F0",
                color: i <= 1 ? "#fff" : "#94A3B8",
                display: "flex", alignItems: "center", justifyContent: "center",
                fontSize: 12, fontWeight: 600,
              }}>
                {i + 1}
              </div>
              <span style={{ fontSize: 12, color: i <= 1 ? "#475569" : "#94A3B8", fontWeight: i <= 1 ? 500 : 400 }}>
                {label}
              </span>
              {i < 2 && <div style={{ width: 24, height: 1, background: "#E2E8F0", margin: "0 4px" }} />}
            </div>
          ))}
        </div>

        <Form
          name="register"
          onFinish={onFinish}
          layout="vertical"
          size="large"
        >
          <Form.Item
            name="username"
            rules={[
              { required: true, message: "请输入用户名" },
              { min: 2, message: "用户名至少需要2个字符" },
            ]}
          >
            <Input prefix={<UserOutlined style={{ color: "#94A3B8" }} />} placeholder="用户名" />
          </Form.Item>

          <Form.Item
            name="password"
            rules={[
              { required: true, message: "请输入密码" },
              { min: 6, message: "密码至少需要6个字符" },
            ]}
          >
            <Input.Password prefix={<LockOutlined style={{ color: "#94A3B8" }} />} placeholder="密码" />
          </Form.Item>

          <Form.Item
            name="confirmPassword"
            rules={[
              { required: true, message: "请再次输入密码" },
              ({ getFieldValue }) => ({
                validator(_, value) {
                  if (!value || getFieldValue("password") === value) {
                    return Promise.resolve();
                  }
                  return Promise.reject(new Error("两次输入的密码不一致"));
                },
              }),
            ]}
          >
            <Input.Password prefix={<LockOutlined style={{ color: "#94A3B8" }} />} placeholder="确认密码" />
          </Form.Item>

          <Form.Item
            name="inviteCode"
            rules={[{ required: true, message: "请输入邀请码" }]}
          >
            <Input
              prefix={<KeyOutlined style={{ color: "#F59E0B" }} />}
              placeholder="邀请码"
              style={{ borderColor: "#FCD34D" }}
            />
          </Form.Item>

          <Form.Item>
            <Button type="primary" htmlType="submit" block loading={loading}
              style={{ height: 44, borderRadius: 12, fontWeight: 600, fontSize: 15 }}
            >
              注册
            </Button>
          </Form.Item>
        </Form>

        <div style={{ textAlign: "center" }}>
          <Text type="secondary">
            已有账号？{" "}
            <Link to="/login" style={{ fontWeight: 500, color: "#6366F1" }}>去登录</Link>
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

export default RegisterPage;
