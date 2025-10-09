import React, { useState, useEffect } from 'react';
import { 
  Card, 
  List, 
  Badge, 
  Button, 
  Typography, 
  Space,
  Tag,
  Avatar,
  Progress,
  Empty
} from 'antd';
import axios from 'axios';
import { 
  FileTextOutlined, 
  TruckOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  ArrowLeftOutlined
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';

const { Title, Text } = Typography;

interface DriverInstruction {
  id: string;
  title: string;
  content: string;
  customer_name?: string;
  equipment_type?: string;
  equipment_quantity?: number;
  current_balance?: number;
  threshold?: number;
  excess?: number;
  priority: string;
  status: string;
  assigned_driver?: string;
  delivery_location?: string;
  contact_phone?: string;
  delivery_date?: string;
  special_instructions?: string;
  created_at: string;
  type?: 'custom' | 'auto_generated';
}

const Instructions: React.FC = () => {
  const navigate = useNavigate();
  const [instructions, setInstructions] = useState<DriverInstruction[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchInstructions();
  }, []);

  const fetchInstructions = async () => {
    try {
      const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
      
      // Fetch both custom and auto-generated instructions
      const [customResponse, autoResponse] = await Promise.all([
        axios.get(`${API_URL}/driver-instructions`),
        axios.get(`${API_URL}/driver-instructions/auto-generated`)
      ]);
      
      // Combine both types of instructions
      const combinedInstructions = [
        ...customResponse.data.map((instruction: any) => ({ ...instruction, type: 'custom' })),
        ...autoResponse.data
      ];
      
      // Sort by priority (HIGH > MEDIUM > LOW) and then by creation date
      combinedInstructions.sort((a, b) => {
        const priorityOrder: { [key: string]: number } = { 'HIGH': 3, 'MEDIUM': 2, 'LOW': 1 };
        const priorityDiff = (priorityOrder[b.priority] || 0) - (priorityOrder[a.priority] || 0);
        if (priorityDiff !== 0) return priorityDiff;
        return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
      });
      
      setInstructions(combinedInstructions);
    } catch (error) {
      console.error('Error fetching instructions:', error);
      // Fallback to empty array if API fails
      setInstructions([]);
    } finally {
      setLoading(false);
    }
  };

  const handleStatusChange = async (id: string, newStatus: string) => {
    try {
      const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
      
      // Update status via API
      await axios.patch(`${API_URL}/driver-instructions/${id}/status`, {
        status: newStatus
      }, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      // Update local state
      setInstructions(prev => 
        prev.map(instruction => 
          instruction.id === id 
            ? { ...instruction, status: newStatus }
            : instruction
        )
      );
    } catch (error) {
      console.error('Error updating instruction status:', error);
      // Still update local state for better UX
      setInstructions(prev => 
        prev.map(instruction => 
          instruction.id === id 
            ? { ...instruction, status: newStatus }
            : instruction
        )
      );
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return '#ff4d4f';
      case 'medium': return '#faad14';
      case 'low': return '#52c41a';
      default: return '#d9d9d9';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending': return 'default';
      case 'in_progress': return 'processing';
      case 'completed': return 'success';
      default: return 'default';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'pending': return <ClockCircleOutlined />;
      case 'in_progress': return <TruckOutlined />;
      case 'completed': return <CheckCircleOutlined />;
      default: return <ClockCircleOutlined />;
    }
  };

  const highPriorityCount = instructions.filter(i => i.priority === 'HIGH').length;
  const mediumPriorityCount = instructions.filter(i => i.priority === 'MEDIUM').length;
  const lowPriorityCount = instructions.filter(i => i.priority === 'LOW').length;
  const completedCount = instructions.filter(i => i.status === 'completed').length;
  const totalCount = instructions.length;
  const completionRate = totalCount > 0 ? (completedCount / totalCount) * 100 : 0;

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
            Collection Instructions
          </Title>
        </div>

        {/* Instruction Summary */}
        <div style={{ marginBottom: '16px' }}>
          <div style={{ display: 'flex', gap: '12px', marginBottom: '12px', flexWrap: 'wrap' }}>
            <Badge count={highPriorityCount} style={{ backgroundColor: '#ff4d4f' }}>
              <div style={{ 
                padding: '8px 16px', 
                border: '1px solid #ff4d4f', 
                borderRadius: '6px',
                color: '#ff4d4f',
                fontWeight: 'bold'
              }}>
                HIGH Priority
              </div>
            </Badge>
            <Badge count={mediumPriorityCount} style={{ backgroundColor: '#faad14' }}>
              <div style={{ 
                padding: '8px 16px', 
                border: '1px solid #faad14', 
                borderRadius: '6px',
                color: '#faad14',
                fontWeight: 'bold'
              }}>
                MEDIUM Priority
              </div>
            </Badge>
            <Badge count={lowPriorityCount} style={{ backgroundColor: '#52c41a' }}>
              <div style={{ 
                padding: '8px 16px', 
                border: '1px solid #52c41a', 
                borderRadius: '6px',
                color: '#52c41a',
                fontWeight: 'bold'
              }}>
                LOW Priority
              </div>
            </Badge>
          </div>
          
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
            <Text strong>Progress</Text>
            <Text>{completedCount}/{totalCount} completed</Text>
          </div>
          <Progress 
            percent={Math.round(completionRate)} 
            strokeColor={{
              '0%': '#108ee9',
              '100%': '#87d068',
            }}
          />
        </div>
      </Card>

      {/* Instructions List */}
      {instructions.length === 0 ? (
        <Card style={{ borderRadius: '12px' }}>
          <Empty
            image={Empty.PRESENTED_IMAGE_SIMPLE}
            description="No collection instructions available"
          />
        </Card>
      ) : (
        <List
          dataSource={instructions}
          renderItem={(item) => (
            <Card 
              key={item.id}
              style={{ 
                marginBottom: '12px', 
                borderRadius: '12px',
                border: item.priority === 'high' ? '2px solid #ff4d4f' : undefined
              }}
            >
              <List.Item
                actions={[
                  <Space direction="vertical" size="small">
                    <Badge 
                      color={getPriorityColor(item.priority)} 
                      text={item.priority.toUpperCase()} 
                    />
                    <Tag 
                      color={getStatusColor(item.status)}
                      icon={getStatusIcon(item.status)}
                    >
                      {item.status.replace('_', ' ').toUpperCase()}
                    </Tag>
                  </Space>
                ]}
              >
                <List.Item.Meta
                  avatar={
                    <Avatar 
                      icon={<TruckOutlined />} 
                      style={{ 
                        backgroundColor: getPriorityColor(item.priority),
                        fontSize: '16px'
                      }}
                    />
                  }
                  title={
                    <div>
                      <Text strong style={{ fontSize: '16px' }}>{item.title}</Text>
                      {item.customer_name && (
                        <div>
                          <Text type="secondary" style={{ fontSize: '14px' }}>
                            Customer: {item.customer_name}
                          </Text>
                        </div>
                      )}
                      {item.delivery_location && (
                        <div>
                          <Text type="secondary" style={{ fontSize: '12px' }}>
                            📍 {item.delivery_location}
                          </Text>
                        </div>
                      )}
                    </div>
                  }
                  description={
                    <div>
                      <div style={{ marginBottom: '8px' }}>
                        <Text strong>Content:</Text> {item.content}
                        <br />
                        {item.equipment_type && (
                          <>
                            <Text strong>Equipment:</Text> {item.equipment_type}
                            <br />
                          </>
                        )}
                        {item.equipment_quantity && (
                          <>
                            <Text strong>Quantity:</Text> {item.equipment_quantity}
                            <br />
                          </>
                        )}
                        {item.current_balance !== undefined && (
                          <>
                            <Text strong>Current Balance:</Text> {item.current_balance}
                            <br />
                            <Text strong>Threshold:</Text> {item.threshold}
                            <br />
                            <Text strong>Excess to Collect:</Text> 
                            <Text style={{ color: '#ff4d4f', fontWeight: 'bold' }}> {item.excess}</Text>
                            <br />
                          </>
                        )}
                        {item.delivery_date && (
                          <>
                            <Text strong>Delivery Date:</Text> {new Date(item.delivery_date).toLocaleDateString()}
                            <br />
                          </>
                        )}
                        {item.assigned_driver && (
                          <>
                            <Text strong>Assigned Driver:</Text> {item.assigned_driver}
                            <br />
                          </>
                        )}
                      </div>
                      
                      {item.special_instructions && (
                        <div style={{ 
                          background: '#f5f5f5', 
                          padding: '8px', 
                          borderRadius: '6px',
                          marginBottom: '12px'
                        }}>
                          <Text type="secondary" style={{ fontSize: '12px' }}>
                            📝 Special Instructions: {item.special_instructions}
                          </Text>
                        </div>
                      )}

                      {item.contact_phone && (
                        <div style={{ marginBottom: '12px' }}>
                          <Text type="secondary" style={{ fontSize: '12px' }}>
                            📞 Contact: {item.contact_phone}
                          </Text>
                        </div>
                      )}

                      <div style={{ marginTop: '12px' }}>
                        {item.status === 'pending' && (
                          <Button 
                            type="primary" 
                            size="small"
                            onClick={() => handleStatusChange(item.id, 'in_progress')}
                            style={{ marginRight: '8px' }}
                          >
                            Start Task
                          </Button>
                        )}
                        {item.status === 'in_progress' && (
                          <Button 
                            type="primary" 
                            size="small"
                            onClick={() => handleStatusChange(item.id, 'completed')}
                            style={{ marginRight: '8px' }}
                          >
                            Mark Complete
                          </Button>
                        )}
                        {item.status === 'completed' && (
                          <Button 
                            type="default" 
                            size="small"
                            disabled
                            icon={<CheckCircleOutlined />}
                          >
                            Completed
                          </Button>
                        )}
                        {item.status === 'cancelled' && (
                          <Button 
                            type="default" 
                            size="small"
                            disabled
                            style={{ color: '#999' }}
                          >
                            Cancelled
                          </Button>
                        )}
                      </div>
                    </div>
                  }
                />
              </List.Item>
            </Card>
          )}
        />
      )}
    </div>
  );
};

export default Instructions;
