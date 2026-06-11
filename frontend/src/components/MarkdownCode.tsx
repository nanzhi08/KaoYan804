import React from 'react';

export type MarkdownCodeProps = React.HTMLAttributes<HTMLElement> & {
  inline?: boolean;
  children?: React.ReactNode;
};

const codeBlockStyle: React.CSSProperties = {
  margin: '12px 0',
  padding: '12px 14px',
  overflowX: 'auto',
  borderRadius: 6,
  background: '#111827',
  color: '#E5E7EB',
  fontSize: 13,
  lineHeight: 1.7,
};

const inlineCodeStyle: React.CSSProperties = {
  padding: '2px 6px',
  borderRadius: 4,
  background: '#EEF2FF',
  color: '#3730A3',
  fontSize: '0.92em',
};

const codeStyle: React.CSSProperties = {
  fontFamily: 'Consolas, "Liberation Mono", Menlo, monospace',
};

const MarkdownCode: React.FC<MarkdownCodeProps> = ({ className, children, ...props }) => {
  const codeText = String(children ?? '').replace(/\n$/, '');
  const language = /language-(\w+)/.exec(className || '')?.[1];
  const isBlock = Boolean(language) || codeText.includes('\n');

  if (!isBlock) {
    return (
      <code className={className} style={{ ...codeStyle, ...inlineCodeStyle }} {...props}>
        {children}
      </code>
    );
  }

  return (
    <pre style={codeBlockStyle}>
      <code className={className} style={codeStyle} data-language={language || undefined} {...props}>
        {codeText}
      </code>
    </pre>
  );
};

export default MarkdownCode;
