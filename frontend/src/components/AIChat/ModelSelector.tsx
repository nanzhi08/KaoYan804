import React from 'react';
import { Select, Tag } from 'antd';

interface ModelSelectorProps {
  value: string;
  onChange: (value: string) => void;
}

const options = [
  { value: 'deepseek', label: 'DeepSeek V4', desc: '默认模型' },
];

const ModelSelector: React.FC<ModelSelectorProps> = ({ value, onChange }) => (
  <Select
    value={value}
    onChange={onChange}
    style={{ width: 280 }}
    options={options.map((opt) => ({
      value: opt.value,
      label: (
        <span>
          {opt.label}
          <Tag style={{ marginLeft: 8, fontSize: 10 }}>{opt.desc}</Tag>
        </span>
      ),
    }))}
  />
);

export default ModelSelector;
