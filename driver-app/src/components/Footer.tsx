import React from 'react';
import { Typography, Space } from 'antd';

const { Text } = Typography;

const Footer: React.FC = () => {
  return (
    <div style={{ 
      textAlign: 'center', 
      padding: '16px', 
      backgroundColor: '#f5f5f5',
      borderTop: '1px solid #d9d9d9',
      marginTop: 'auto'
    }}>
      <Space>
        <Text type="secondary" style={{ fontSize: '12px' }}>
          Powered by
        </Text>
        <Text strong style={{ 
          fontSize: '14px', 
          color: '#1890ff',
          fontFamily: 'Arial, sans-serif'
        }}>
          NUVARU
        </Text>
      </Space>
    </div>
  );
};

export default Footer;
