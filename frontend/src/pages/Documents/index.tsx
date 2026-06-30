import React, { useCallback, useEffect, useState } from 'react';
import { Card, Upload, Button, Tag, Popconfirm, Spin, Empty, App } from 'antd';
import { UploadOutlined, FileTextOutlined, DeleteOutlined } from '@ant-design/icons';
import { fetchDocuments, uploadDocument, deleteDocument } from '../../services/documentApi';
import type { Document as DocType } from '../../types';

const fileTypeColors: Record<string, string> = {
  pdf: '#EF4444',
  doc: '#6366F1',
  docx: '#6366F1',
  txt: '#10B981',
  md: '#6366F1',
  png: '#F59E0B',
  jpg: '#F59E0B',
  jpeg: '#F59E0B',
};

function normalizeTags(tags: DocType['tags']): string[] {
  if (Array.isArray(tags)) {
    return tags.filter(Boolean);
  }

  if (typeof tags === 'string' && tags.trim()) {
    return tags.split(/\s+/).filter(Boolean);
  }

  return [];
}

const Documents: React.FC = () => {
  const { message } = App.useApp();
  const [docs, setDocs] = useState<DocType[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);

  const loadDocs = useCallback(() => {
    setLoading(true);
    fetchDocuments()
      .then(setDocs)
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    loadDocs();
  }, [loadDocs]);

  const handleUpload = async (file: File) => {
    setUploading(true);
    try {
      await uploadDocument(file);
      message.success(`文件 ${file.name} 上传成功`);
      loadDocs();
    } catch {
      message.error('上传失败');
    } finally {
      setUploading(false);
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
          accept=".pdf,.doc,.docx,.txt,.md,.png,.jpg,.jpeg"
          showUploadList={false}
          beforeUpload={(file) => { handleUpload(file); return false; }}
          disabled={uploading}
        >
          <Button type="primary" icon={<UploadOutlined />} loading={uploading}>上传文件</Button>
        </Upload>
      }
    >
      {loading ? (
        <Spin style={{ display: 'block', margin: '40px auto' }} />
      ) : docs.length === 0 ? (
        <Empty description="暂无资料，请上传" />
      ) : (
        <div style={{ display: 'grid', gap: 10 }}>
          {docs.map((doc) => {
            const tags = normalizeTags(doc.tags);

            return (
              <div
                key={doc.id}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  gap: 16,
                  padding: '14px 0',
                  borderBottom: '1px solid #F1F5F9',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: 12, minWidth: 0 }}>
                  <FileTextOutlined style={{ fontSize: 24, color: fileTypeColors[doc.file_type] || '#94A3B8' }} />
                  <div style={{ minWidth: 0 }}>
                    <div style={{ fontWeight: 600, marginBottom: 6, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {doc.original_name}
                    </div>
                    <div>
                      <Tag color={fileTypeColors[doc.file_type]}>{doc.file_type.toUpperCase()}</Tag>
                      {tags.map((tag) => <Tag key={tag}>{tag}</Tag>)}
                      <span style={{ color: '#94A3B8', marginLeft: 8 }}>
                        {new Date(doc.uploaded_at).toLocaleDateString('zh-CN')}
                      </span>
                    </div>
                  </div>
                </div>
                <div style={{ flexShrink: 0 }}>
                  <Popconfirm title="确定删除？" onConfirm={() => handleDelete(doc.id)}>
                    <Button type="text" danger icon={<DeleteOutlined />} />
                  </Popconfirm>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </Card>
  );
};

export default Documents;
