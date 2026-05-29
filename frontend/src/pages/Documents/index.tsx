import React, { useEffect, useState } from 'react';
import { Card, Upload, Button, List, Tag, Popconfirm, Spin, Empty, message } from 'antd';
import { UploadOutlined, FileTextOutlined, DeleteOutlined } from '@ant-design/icons';
import { fetchDocuments, uploadDocument, deleteDocument } from '../../services/documentApi';
import type { Document as DocType } from '../../types';

const fileTypeColors: Record<string, string> = {
  pdf: '#EF4444',
  docx: '#6366F1',
  txt: '#10B981',
  md: '#6366F1',
};

const Documents: React.FC = () => {
  const [docs, setDocs] = useState<DocType[]>([]);
  const [loading, setLoading] = useState(true);

  const loadDocs = () => {
    setLoading(true);
    fetchDocuments().then(setDocs).finally(() => setLoading(false));
  };

  useEffect(() => { loadDocs(); }, []);

  const handleUpload = async (file: File) => {
    try {
      await uploadDocument(file);
      message.success(`文件 ${file.name} 上传成功`);
      loadDocs();
    } catch {
      message.error('上传失败');
    }
    return false;
  };

  const handleDelete = async (id: number) => {
    try {
      await deleteDocument(id);
      message.success('删除成功');
      loadDocs();
    } catch {
      message.error('删除失败');
    }
  };

  return (
    <Card
      title={<span><FileTextOutlined style={{ marginRight: 8 }} />资料管理</span>}
      extra={
        <Upload
          accept=".pdf,.docx,.txt,.md"
          showUploadList={false}
          beforeUpload={(file) => { handleUpload(file); return false; }}
        >
          <Button type="primary" icon={<UploadOutlined />}>上传文件</Button>
        </Upload>
      }
    >
      {loading ? (
        <Spin style={{ display: 'block', margin: '40px auto' }} />
      ) : docs.length === 0 ? (
        <Empty description="暂无资料，请上传" />
      ) : (
        <List
          dataSource={docs}
          renderItem={(doc) => (
            <List.Item
              actions={[
                <Popconfirm title="确定删除？" onConfirm={() => handleDelete(doc.id)} key="delete">
                  <Button type="text" danger icon={<DeleteOutlined />} />
                </Popconfirm>,
              ]}
            >
              <List.Item.Meta
                avatar={<FileTextOutlined style={{ fontSize: 24, color: fileTypeColors[doc.file_type] || '#94A3B8' }} />}
                title={doc.original_name}
                description={
                  <span>
                    <Tag color={fileTypeColors[doc.file_type]}>{doc.file_type.toUpperCase()}</Tag>
                    {doc.tags?.map((tag: string) => <Tag key={tag}>{tag}</Tag>)}
                    <span style={{ color: '#94A3B8', marginLeft: 8 }}>
                      {new Date(doc.uploaded_at).toLocaleDateString('zh-CN')}
                    </span>
                  </span>
                }
              />
            </List.Item>
          )}
        />
      )}
    </Card>
  );
};

export default Documents;
