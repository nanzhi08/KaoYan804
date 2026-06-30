import React, { useState, useEffect, useCallback } from "react";
import { Card, Button, Tag, Space, Spin, Result, Progress, Rate, App, Statistic, Row, Col } from "antd";
import {
  ScheduleOutlined,
  BookOutlined,
  CheckCircleOutlined,
  ReloadOutlined,
  FieldTimeOutlined,
  FlagOutlined,
  BulbOutlined,
} from "@ant-design/icons";
import api from "../../services/api";

interface ReviewItem {
  mastery_id: number;
  knowledge_point_id: number;
  name: string;
  chapter: string;
  part: string;
  mastery_level: number;
  ease_factor: number;
  interval_days: number;
  repetitions: number;
  next_review_at: string | null;
  sample_question: { id: number; content: string; type: string } | null;
}

interface ReviewStats {
  total_knowledge_points: number;
  average_mastery: number;
  due_now: number;
  due_this_week: number;
  message: string;
}

const qualityGuides = [
  { score: 1, label: "遗忘", desc: "重新看解析，今天再刷同类题", color: "red" },
  { score: 3, label: "勉强记住", desc: "保留在近期复习队列", color: "orange" },
  { score: 5, label: "稳定掌握", desc: "拉长间隔，减少重复打扰", color: "green" },
];

const partLabel: Record<string, string> = {
  C_programming: "C语言",
  data_structure: "DS",
};

const formatReviewDate = (value: string | null) => {
  if (!value) return "现在复习";
  return new Date(value).toLocaleDateString("zh-CN");
};

const ReviewPlan: React.FC = () => {
  const { message } = App.useApp();
  const [items, setItems] = useState<ReviewItem[]>([]);
  const [stats, setStats] = useState<ReviewStats | null>(null);
  const [loading, setLoading] = useState(false);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [reviewing, setReviewing] = useState<number | null>(null);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setLoadError(null);
    try {
      const [dueRes, statsRes] = await Promise.all([
        api.get("/review/due"),
        api.get("/review/stats"),
      ]);
      setItems(dueRes.data.items || []);
      setStats(statsRes.data);
    } catch {
      setLoadError("复习计划数据加载失败，请确认后端服务已启动后重试");
    }
    finally { setLoading(false); }
  }, []);

  useEffect(() => {
    void fetchData();
  }, [fetchData]);

  const handleReview = async (masteryId: number, quality: number) => {
    setReviewing(masteryId);
    try {
      await api.post(`/review/${masteryId}/review`, null, { params: { quality } });
      message.success("复习记录已更新！");
      void fetchData();
    } catch { /* handled by interceptor */ }
    finally { setReviewing(null); }
  };

  if (loading && !stats) return <Spin size="large" style={{ display: "block", margin: "100px auto" }} />;

  if (!stats) {
    return (
      <Result
        status="warning"
        title={loadError || "复习计划暂不可用"}
        subTitle="当前页面依赖 /api/review/due 和 /api/review/stats。请先确认后端 8000 端口运行正常。"
        extra={<Button type="primary" icon={<ReloadOutlined />} onClick={fetchData}>重新加载</Button>}
      />
    );
  }

  const queueProgress = stats.due_this_week > 0
    ? Math.max(0, Math.round(((stats.due_this_week - stats.due_now) / stats.due_this_week) * 100))
    : 100;

  return (
    <div>
      <div style={{
        marginBottom: 18,
        padding: 24,
        border: "1px solid #E2E8F0",
        borderRadius: 14,
        background: "linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 58%, #EFF6FF 100%)",
      }}>
        <Row gutter={[20, 16]} align="middle">
          <Col xs={24} lg={14}>
            <Tag color={stats.due_now > 0 ? "red" : "green"} style={{ marginBottom: 10 }}>
              今日记忆队列
            </Tag>
            <h2 style={{ margin: "0 0 8px 0", fontSize: 24 }}>先回忆，再评分，最后拉开复习间隔</h2>
            <p style={{ margin: 0, color: "#64748B", maxWidth: 620 }}>
              每个知识点先在脑中复述核心定义或解题步骤，再看示例题校验。评分会影响下一次复习时间。
            </p>
          </Col>
          <Col xs={24} lg={10}>
            <div style={{
              padding: 16,
              border: "1px solid #DBEAFE",
              borderRadius: 12,
              background: "#FFFFFF",
            }}>
              <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 10 }}>
                <span style={{ color: "#64748B" }}>本周记忆队列消化度</span>
                <strong>{queueProgress}%</strong>
              </div>
              <Progress percent={queueProgress} showInfo={false} strokeColor="#2563EB" />
              <div style={{ marginTop: 10, color: "#64748B", fontSize: 13 }}>
                今日待复习 {stats.due_now} 个 · 本周待复习 {stats.due_this_week} 个
              </div>
            </div>
          </Col>
        </Row>
      </div>

      <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
        <Col xs={12} lg={6}><Card><Statistic title="知识点总数" value={stats.total_knowledge_points} prefix={<BookOutlined />} /></Card></Col>
        <Col xs={12} lg={6}><Card><Statistic title="平均掌握度" value={stats.average_mastery} suffix="%" /></Card></Col>
        <Col xs={12} lg={6}><Card><Statistic title="今日待复习" value={stats.due_now} prefix={<FieldTimeOutlined />} styles={{ content: { color: stats.due_now > 0 ? "#EF4444" : "#10B981" } }} /></Card></Col>
        <Col xs={12} lg={6}><Card><Statistic title="本周待复习" value={stats.due_this_week} prefix={<ScheduleOutlined />} /></Card></Col>
      </Row>

      <Row gutter={[12, 12]} style={{ marginBottom: 16 }}>
        {qualityGuides.map((guide) => (
          <Col xs={24} md={8} key={guide.score}>
            <div style={{
              padding: 14,
              border: "1px solid #E2E8F0",
              borderRadius: 12,
              background: "#FFFFFF",
              height: "100%",
            }}>
              <Space align="start">
                <Tag color={guide.color}>{guide.score} 分</Tag>
                <div>
                  <div style={{ fontWeight: 700 }}>{guide.label}</div>
                  <div style={{ color: "#64748B", fontSize: 13 }}>{guide.desc}</div>
                </div>
              </Space>
            </div>
          </Col>
        ))}
      </Row>

      <Card title={<span><ScheduleOutlined /> 待复习知识点</span>}
        extra={<Button icon={<ReloadOutlined />} onClick={fetchData} loading={loading}>刷新</Button>}>
        {items.length === 0 ? (
          <Result icon={<CheckCircleOutlined style={{ color: "#10B981" }} />}
            title="暂无到期复习任务"
            subTitle="今天的记忆队列已经清空，可以去刷一组新题保持手感。" />
        ) : (
          <div style={{ display: "grid", gap: 14 }}>
            {items.map((item) => (
              <div
                key={item.mastery_id}
                style={{
                  display: "grid",
                  gridTemplateColumns: "minmax(0, 1fr) minmax(190px, 220px)",
                  gap: 18,
                  padding: "16px 0",
                  borderBottom: "1px solid #F1F5F9",
                  alignItems: "start",
                }}
              >
                <div style={{ minWidth: 0 }}>
                  <Space wrap style={{ marginBottom: 10 }}>
                    <Tag color={item.part === "C_programming" ? "blue" : "green"}>
                      {partLabel[item.part] || item.part}
                    </Tag>
                    <span style={{ fontWeight: 700 }}>{item.name}</span>
                    <Tag>{item.chapter}</Tag>
                    <Tag icon={<FlagOutlined />}>掌握 {item.mastery_level}%</Tag>
                    <Tag icon={<FieldTimeOutlined />}>{formatReviewDate(item.next_review_at)}</Tag>
                  </Space>
                  <Progress percent={item.mastery_level} size="small" />
                  {item.sample_question && (
                    <div style={{
                      marginTop: 10,
                      padding: 12,
                      border: "1px solid #E2E8F0",
                      borderRadius: 10,
                      background: "#F8FAFC",
                    }}>
                      <Space align="start">
                        <BulbOutlined style={{ color: "#F59E0B", marginTop: 3 }} />
                        <div>
                          <div style={{ fontWeight: 600, color: "#334155", marginBottom: 4 }}>示例题回忆</div>
                          <div style={{ color: "#64748B", fontSize: 13, lineHeight: 1.7 }}>
                            {item.sample_question.content}
                          </div>
                        </div>
                      </Space>
                    </div>
                  )}
                </div>
                <Space orientation="vertical" style={{ minWidth: 190 }}>
                  <div style={{ fontSize: 12, color: "#94A3B8" }}>
                    间隔: {item.interval_days}天 · 重复: {item.repetitions}次
                  </div>
                  <Rate
                    count={5}
                    allowClear={false}
                    value={Math.round(item.mastery_level / 20)}
                    onChange={(val) => handleReview(item.mastery_id, val)}
                    disabled={reviewing === item.mastery_id}
                  />
                  <span style={{ fontSize: 11, color: "#94A3B8" }}>
                    点击星级即完成本次复习
                  </span>
                </Space>
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  );
};

export default ReviewPlan;
