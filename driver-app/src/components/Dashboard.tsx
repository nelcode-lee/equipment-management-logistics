import React, { useState, useEffect } from 'react';
import { 
  Card, 
  Row, 
  Col, 
  Statistic, 
  Button, 
  Typography, 
  Space,
  List,
  Avatar,
  Badge,
  Spin
} from 'antd';
import axios from 'axios';
import { 
  CameraOutlined, 
  FileTextOutlined, 
  UserOutlined,
  LogoutOutlined,
  BellOutlined,
  TruckOutlined,
  EditOutlined
} from '@ant-design/icons';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';

const { Title, Text } = Typography;

interface DriverInstruction {
  id: string;
  customer_name: string;
  equipment_type: string;
  current_balance: number;
  threshold: number;
  excess: number;
  priority: string;
  status: string;
  notes: string;
}

const Dashboard: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [instructions, setInstructions] = useState<DriverInstruction[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchInstructions();
  }, []);

  const fetchInstructions = async () => {
    try {
      const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
      const response = await axios.get(`${API_URL}/driver-instructions`);
      setInstructions(response.data);
    } catch (error) {
      console.error('Error fetching instructions:', error);
      // Fallback to empty array if API fails
      setInstructions([]);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return '#ff4d4f';
      case 'medium': return '#faad14';
      case 'low': return '#52c41a';
      default: return '#d9d9d9';
    }
  };

  if (loading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh' 
      }}>
        <Spin size="large" />
      </div>
    );
  }

  return (
    <div style={{ padding: '16px', maxWidth: '600px', margin: '0 auto' }}>
      {/* Header */}
      <Card style={{ marginBottom: '16px', borderRadius: '12px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <Title level={4} style={{ margin: 0, color: '#1890ff' }}>
              Welcome, {user?.full_name || user?.username}
            </Title>
            <Text type="secondary">
              {user?.company || 'Equipment Logistics'}
            </Text>
          </div>
          <Button 
            type="text" 
            icon={<LogoutOutlined />} 
            onClick={handleLogout}
            style={{ color: '#ff4d4f' }}
          >
            Logout
          </Button>
        </div>
      </Card>

      {/* Quick Actions */}
      <Row gutter={[16, 16]} style={{ marginBottom: '16px' }}>
        <Col span={12}>
          <Card 
            hoverable
            onClick={() => navigate('/upload')}
            style={{ 
              textAlign: 'center', 
              borderRadius: '12px',
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              color: 'white'
            }}
          >
            <CameraOutlined style={{ fontSize: '32px', marginBottom: '8px' }} />
            <div style={{ fontWeight: 'bold' }}>Upload Photo</div>
            <div style={{ fontSize: '12px', opacity: 0.8 }}>AI Data Capture</div>
          </Card>
        </Col>
        <Col span={12}>
          <Card 
            hoverable
            onClick={() => navigate('/manual-entry')}
            style={{ 
              textAlign: 'center', 
              borderRadius: '12px',
              background: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
              color: 'white'
            }}
          >
            <EditOutlined style={{ fontSize: '32px', marginBottom: '8px' }} />
            <div style={{ fontWeight: 'bold' }}>Manual Entry</div>
            <div style={{ fontSize: '12px', opacity: 0.8 }}>Failsafe Input</div>
          </Card>
        </Col>
      </Row>

      {/* Secondary Actions */}
      <Row gutter={[16, 16]} style={{ marginBottom: '16px' }}>
        <Col span={24}>
          <Card 
            hoverable
            onClick={() => navigate('/instructions')}
            style={{ 
              textAlign: 'center', 
              borderRadius: '12px',
              background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
              color: 'white',
              padding: '8px 0'
            }}
          >
            <FileTextOutlined style={{ fontSize: '28px', marginBottom: '4px' }} />
            <div style={{ fontWeight: 'bold' }}>View Instructions</div>
            <div style={{ fontSize: '12px', opacity: 0.8 }}>Collection Tasks & Alerts</div>
          </Card>
        </Col>
      </Row>

      {/* Stats */}
      <Row gutter={[16, 16]} style={{ marginBottom: '16px' }}>
        <Col span={12}>
          <Card style={{ borderRadius: '12px' }}>
            <Statistic
              title="Pending Tasks"
              value={instructions.filter(i => i.status === 'pending').length}
              valueStyle={{ color: '#ff4d4f' }}
            />
          </Card>
        </Col>
        <Col span={12}>
          <Card style={{ borderRadius: '12px' }}>
            <Statistic
              title="High Priority"
              value={instructions.filter(i => i.priority === 'high').length}
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
      </Row>

      {/* Recent Instructions */}
      <Card 
        title={
          <Space>
            <BellOutlined />
            Recent Instructions
          </Space>
        }
        style={{ borderRadius: '12px' }}
      >
        <List
          dataSource={instructions.slice(0, 3)}
          renderItem={(item) => (
            <List.Item
              actions={[
                <Badge 
                  color={getPriorityColor(item.priority)} 
                  text={item.priority.toUpperCase()} 
                />
              ]}
            >
              <List.Item.Meta
                avatar={
                  <Avatar 
                    icon={<TruckOutlined />} 
                    style={{ backgroundColor: getPriorityColor(item.priority) }}
                  />
                }
                title={item.customer_name}
                description={
                  <div>
                    <div>{item.equipment_type} - Excess: {item.excess}</div>
                    <Text type="secondary" style={{ fontSize: '12px' }}>
                      {item.notes}
                    </Text>
                  </div>
                }
              />
            </List.Item>
          )}
        />
      </Card>
    </div>
  );
};

export default Dashboard;
