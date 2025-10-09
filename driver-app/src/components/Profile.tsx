import React from 'react';
import { 
  Card, 
  Descriptions, 
  Typography, 
  Button, 
  Space,
  Avatar,
  Divider
} from 'antd';
import { 
  UserOutlined, 
  PhoneOutlined, 
  MailOutlined,
  IdcardOutlined,
  BankOutlined,
  ArrowLeftOutlined
} from '@ant-design/icons';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';

const { Title, Text } = Typography;

const Profile: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();

  return (
    <div style={{ padding: '16px', maxWidth: '600px', margin: '0 auto' }}>
      {/* Header */}
      <Card style={{ marginBottom: '16px', borderRadius: '12px' }}>
        <div style={{ display: 'flex', alignItems: 'center', marginBottom: '16px' }}>
          <Button 
            type="text" 
            icon={<ArrowLeftOutlined />} 
            onClick={() => navigate('/')}
            style={{ marginRight: '8px' }}
          />
          <Title level={4} style={{ margin: 0, color: '#1890ff' }}>
            Profile
          </Title>
        </div>
      </Card>

      {/* Profile Card */}
      <Card style={{ borderRadius: '12px', marginBottom: '16px' }}>
        <div style={{ textAlign: 'center', marginBottom: '24px' }}>
          <Avatar 
            size={80} 
            icon={<UserOutlined />} 
            style={{ 
              backgroundColor: '#1890ff',
              marginBottom: '16px'
            }}
          />
          <div>
            <Title level={3} style={{ margin: 0, color: '#1890ff' }}>
              {user?.full_name || user?.username}
            </Title>
            <Text type="secondary" style={{ fontSize: '16px' }}>
              Driver
            </Text>
          </div>
        </div>

        <Descriptions column={1} size="middle">
          <Descriptions.Item 
            label={
              <Space>
                <UserOutlined />
                Username
              </Space>
            }
          >
            {user?.username}
          </Descriptions.Item>

          <Descriptions.Item 
            label={
              <Space>
                <MailOutlined />
                Email
              </Space>
            }
          >
            {user?.email}
          </Descriptions.Item>

          {user?.phone_number && (
            <Descriptions.Item 
              label={
                <Space>
                  <PhoneOutlined />
                  Phone
                </Space>
              }
            >
              {user.phone_number}
            </Descriptions.Item>
          )}

          {user?.driver_license && (
            <Descriptions.Item 
              label={
                <Space>
                  <IdcardOutlined />
                  Driver License
                </Space>
              }
            >
              {user.driver_license}
            </Descriptions.Item>
          )}

          {user?.company && (
            <Descriptions.Item 
              label={
                <Space>
                  <BankOutlined />
                  Company
                </Space>
              }
            >
              {user.company}
            </Descriptions.Item>
          )}
        </Descriptions>
      </Card>

      {/* Quick Stats */}
      <Card title="Quick Stats" style={{ borderRadius: '12px', marginBottom: '16px' }}>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#1890ff' }}>
              12
            </div>
            <Text type="secondary">Collections Today</Text>
          </div>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#52c41a' }}>
              98%
            </div>
            <Text type="secondary">Success Rate</Text>
          </div>
        </div>
      </Card>

      {/* Actions */}
      <Card style={{ borderRadius: '12px' }}>
        <Space direction="vertical" size="middle" style={{ width: '100%' }}>
          <Button 
            type="primary" 
            block 
            size="large"
            onClick={() => navigate('/upload')}
            style={{ borderRadius: '8px' }}
          >
            Upload Delivery Note
          </Button>
          
          <Button 
            block 
            size="large"
            onClick={() => navigate('/instructions')}
            style={{ borderRadius: '8px' }}
          >
            View Instructions
          </Button>

          <Divider style={{ margin: '16px 0' }} />

          <Button 
            type="default" 
            block 
            size="large"
            style={{ borderRadius: '8px' }}
          >
            Change Password
          </Button>

          <Button 
            type="default" 
            block 
            size="large"
            style={{ borderRadius: '8px' }}
          >
            Contact Support
          </Button>
        </Space>
      </Card>
    </div>
  );
};

export default Profile;
