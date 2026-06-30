import React, { useEffect, useState } from "react";
import { Card, Tabs, Table, Button, Popconfirm, App, Tag, Space, Typography, Progress } from "antd";
import { PlusOutlined, DeleteOutlined, UserOutlined, KeyOutlined } from "@ant-design/icons";
import { adminApi } from "../../services/adminApi";
import type { UserWithStats, InviteCode } from "../../types";
import { useAuthStore } from "../../stores/useAuthStore";

const { Title } = Typography;

const AdminPage: React.FC = () => {
  const { message } = App.useApp();
  const [users, setUsers] = useState<UserWithStats[]>([]);
  const [inviteCodes, setInviteCodes] = useState<InviteCode[]>([]);
  const [loadingUsers, setLoadingUsers] = useState(false);
  const [loadingCodes, setLoadingCodes] = useState(false);
  const currentUser = useAuthStore((s) => s.user);

  const loadUsers = async () => {
    setLoadingUsers(true);
    try {
      const res = await adminApi.fetchUsers();
      setUsers(res.data);
    } catch {
      message.error("加载用户列表失败");
    } finally {
      setLoadingUsers(false);
    }
  };

  const loadInviteCodes = async () => {
    setLoadingCodes(true);
    try {
      const res = await adminApi.fetchInviteCodes();
      setInviteCodes(res.data);
    } catch {
      message.error("加载邀请码列表失败");
    } finally {
      setLoadingCodes(false);
    }
  };

  useEffect(() => {
    loadUsers();
    loadInviteCodes();
  }, []);

  const handleDeleteUser = async (id: number) => {
    try {
      await adminApi.deleteUser(id);
      message.success("用户已删除");
      loadUsers();
    } catch {
      message.error("删除用户失败");
    }
  };

  const handleCreateCode = async () => {
    try {
      const res = await adminApi.createInviteCode();
      message.success(`邀请码已生成：${res.data.code}`);
      loadInviteCodes();
    } catch {
      message.error("生成邀请码失败");
    }
  };

  const handleDeleteCode = async (id: number) => {
    try {
      await adminApi.deleteInviteCode(id);
      message.success("邀请码已删除");
      loadInviteCodes();
    } catch {
      message.error("删除邀请码失败");
    }
  };

  const normalizeAccuracy = (v: number | null | undefined): number => {
    if (v == null) return 0;
    return v <= 1 ? Math.round(v * 100) : Math.round(v);
  };

  const totalPractices = users.reduce((sum, u) => sum + (u.practice_count || 0), 0);
  const avgAccuracy = users.length > 0
    ? Math.round(users.reduce((sum, u) => sum + normalizeAccuracy(u.accuracy), 0) / users.length)
    : 0;
  const unusedCodes = inviteCodes.filter((c) => !c.is_used).length;

  const userColumns = [
    { title: "用户名", dataIndex: "username", key: "username" },
    {
      title: "角色",
      dataIndex: "role",
      key: "role",
      render: (role: string) => (
        <Tag color={role === "admin" ? "red" : "blue"}>{role === "admin" ? "管理员" : "用户"}</Tag>
      ),
    },
    { title: "练习次数", dataIndex: "practice_count", key: "practice_count" },
    {
      title: "正确率",
      dataIndex: "accuracy",
      key: "accuracy",
      width: 160,
      render: (v: number) => {
        const pct = normalizeAccuracy(v);
        return (
          <Progress
            percent={pct}
            size="small"
            strokeColor={pct >= 80 ? "#10B981" : pct >= 60 ? "#F59E0B" : "#EF4444"}
            format={() => `${pct}%`}
          />
        );
      },
    },
    {
      title: "注册时间",
      dataIndex: "created_at",
      key: "created_at",
      render: (v: string | null) => v?.split("T")[0] || "-",
    },
    {
      title: "操作",
      key: "actions",
      render: (_: unknown, record: UserWithStats) =>
        record.id !== currentUser?.id ? (
          <Popconfirm
            title="确定删除该用户及其所有数据？"
            onConfirm={() => handleDeleteUser(record.id)}
          >
            <Button type="text" danger icon={<DeleteOutlined />}>
              删除
            </Button>
          </Popconfirm>
        ) : null,
    },
  ];

  const codeColumns = [
    {
      title: "邀请码",
      dataIndex: "code",
      key: "code",
      render: (v: string) => (
        <code
          style={{ cursor: "pointer", padding: "2px 6px", background: "#F1F5F9", borderRadius: 4 }}
          onClick={() => { navigator.clipboard.writeText(v); message.success("已复制邀请码"); }}
        >
          {v}
        </code>
      ),
    },
    {
      title: "状态",
      dataIndex: "is_used",
      key: "is_used",
      render: (v: boolean) => (
        <Tag color={v ? "default" : "green"}>{v ? "已使用" : "可用"}</Tag>
      ),
    },
    {
      title: "创建时间",
      dataIndex: "created_at",
      key: "created_at",
      render: (v: string | null) => v?.split("T")[0] || "-",
    },
    {
      title: "操作",
      key: "actions",
      render: (_: unknown, record: InviteCode) =>
        !record.is_used ? (
          <Popconfirm
            title="确定删除该邀请码？"
            onConfirm={() => handleDeleteCode(record.id)}
          >
            <Button type="text" danger icon={<DeleteOutlined />}>
              删除
            </Button>
          </Popconfirm>
        ) : null,
    },
  ];

  return (
    <div style={{ padding: "0 0 24px" }}>
      <Title level={4} style={{ marginBottom: 20 }}>
        <UserOutlined /> 管理面板
      </Title>

      <Space size={16} style={{ width: "100%", marginBottom: 24 }} wrap>
        <Card size="small" style={{ minWidth: 160, flex: 1 }}>
          <div style={{ color: "#64748B", fontSize: 13 }}>总用户数</div>
          <div style={{ fontSize: 28, fontWeight: 700, color: "#6366F1" }}>{users.length}</div>
        </Card>
        <Card size="small" style={{ minWidth: 160, flex: 1 }}>
          <div style={{ color: "#64748B", fontSize: 13 }}>总练习次数</div>
          <div style={{ fontSize: 28, fontWeight: 700, color: "#10B981" }}>{totalPractices}</div>
        </Card>
        <Card size="small" style={{ minWidth: 160, flex: 1 }}>
          <div style={{ color: "#64748B", fontSize: 13 }}>平均正确率</div>
          <div style={{ fontSize: 28, fontWeight: 700, color: "#F59E0B" }}>{avgAccuracy}%</div>
        </Card>
        <Card size="small" style={{ minWidth: 160, flex: 1 }}>
          <div style={{ color: "#64748B", fontSize: 13 }}>可用邀请码</div>
          <div style={{ fontSize: 28, fontWeight: 700, color: "#8B5CF6" }}>{unusedCodes}</div>
        </Card>
      </Space>

      <Tabs
        defaultActiveKey="users"
        items={[
          {
            key: "users",
            label: (
              <span>
                <UserOutlined /> 用户管理
              </span>
            ),
            children: (
              <Card>
                <Table
                  dataSource={users}
                  columns={userColumns}
                  rowKey="id"
                  loading={loadingUsers}
                  pagination={{ pageSize: 20 }}
                />
              </Card>
            ),
          },
          {
            key: "invite-codes",
            label: (
              <span>
                <KeyOutlined /> 邀请码管理
              </span>
            ),
            children: (
              <Card>
                <Space style={{ marginBottom: 16 }}>
                  <Button type="primary" icon={<PlusOutlined />} onClick={handleCreateCode}>
                    生成邀请码
                  </Button>
                </Space>
                <Table
                  dataSource={inviteCodes}
                  columns={codeColumns}
                  rowKey="id"
                  loading={loadingCodes}
                  pagination={{ pageSize: 20 }}
                />
              </Card>
            ),
          },
        ]}
      />
    </div>
  );
};

export default AdminPage;
