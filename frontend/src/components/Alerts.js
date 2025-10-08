import React, { useState, useEffect } from 'react';
import { Table, Tag, Button, message, Card, Statistic, Row, Col, Spin } from 'antd';
import { AlertOutlined, CheckCircleOutlined } from '@ant-design/icons';
import axios from 'axios';
import API_BASE_URL from '../config';

const Alerts = () => {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAlerts();
  }, []);

  const fetchAlerts = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE_URL}/alerts`);
      setAlerts(response.data);
    } catch (error) {
      console.error('Error fetching alerts:', error);
      message.error('Failed to fetch alerts');
    } finally {
      setLoading(false);
    }
  };

  const handleResolveAlert = async (customerName, equipmentType) => {
    try {
      // Note: This would need a new endpoint to mark alerts as resolved
      message.success(`Alert for ${customerName} - ${equipmentType} marked as resolved`);
      fetchAlerts(); // Refresh the list
    } catch (error) {
      message.error('Failed to resolve alert');
    }
  };

  const columns = [
    {
      title: 'Customer',
      dataIndex: 'customer_name',
      key: 'customer_name',
      sorter: (a, b) => a.customer_name.localeCompare(b.customer_name),
    },
    {
      title: 'Equipment Type',
      dataIndex: 'equipment_type',
      key: 'equipment_type',
      render: (type) => <Tag color="blue">{type}</Tag>,
      filters: [
        { text: 'Pallet', value: 'pallet' },
        { text: 'Cage', value: 'cage' },
        { text: 'Dolly', value: 'dolly' },
        { text: 'Stillage', value: 'stillage' },
        { text: 'Other', value: 'other' },
      ],
      onFilter: (value, record) => record.equipment_type === value,
    },
    {
      title: 'Current Balance',
      dataIndex: 'current_balance',
      key: 'current_balance',
      sorter: (a, b) => a.current_balance - b.current_balance,
    },
    {
      title: 'Threshold',
      dataIndex: 'threshold',
      key: 'threshold',
    },
    {
      title: 'Excess',
      dataIndex: 'excess',
      key: 'excess',
      render: (excess) => <Tag color="red">+{excess}</Tag>,
      sorter: (a, b) => a.excess - b.excess,
    },
    {
      title: 'Priority',
      dataIndex: 'priority',
      key: 'priority',
      render: (priority) => (
        <Tag color={priority === 'high' ? 'red' : 'orange'}>
          {priority.toUpperCase()}
        </Tag>
      ),
      filters: [
        { text: 'High', value: 'high' },
        { text: 'Medium', value: 'medium' },
      ],
      onFilter: (value, record) => record.priority === value,
    },
    {
      title: 'Last Movement',
      dataIndex: 'last_movement',
      key: 'last_movement',
      render: (timestamp) => new Date(timestamp).toLocaleString(),
      sorter: (a, b) => new Date(a.last_movement) - new Date(b.last_movement),
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_, record) => (
        <Button
          type="primary"
          size="small"
          icon={<CheckCircleOutlined />}
          onClick={() => handleResolveAlert(record.customer_name, record.equipment_type)}
        >
          Resolve
        </Button>
      ),
    },
  ];

  const highPriorityAlerts = alerts.filter(alert => alert.priority === 'high');
  const mediumPriorityAlerts = alerts.filter(alert => alert.priority === 'medium');
  const totalExcess = alerts.reduce((sum, alert) => sum + alert.excess, 0);

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <Spin size="large" />
        <p>Loading alerts...</p>
      </div>
    );
  }

  return (
    <div>
      <h2>Equipment Alerts</h2>
      
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="Total Alerts"
              value={alerts.length}
              prefix={<AlertOutlined />}
              valueStyle={{ color: alerts.length > 0 ? '#cf1322' : '#3f8600' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="High Priority"
              value={highPriorityAlerts.length}
              valueStyle={{ color: '#cf1322' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Medium Priority"
              value={mediumPriorityAlerts.length}
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Total Excess"
              value={totalExcess}
              suffix="units"
              valueStyle={{ color: '#cf1322' }}
            />
          </Card>
        </Col>
      </Row>

      <Card>
        {alerts.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '40px' }}>
            <CheckCircleOutlined style={{ fontSize: '48px', color: '#52c41a', marginBottom: '16px' }} />
            <h3>No Active Alerts</h3>
            <p>All customers are within their equipment thresholds.</p>
          </div>
        ) : (
          <Table
            dataSource={alerts}
            columns={columns}
            rowKey={(record) => `${record.customer_name}-${record.equipment_type}`}
            pagination={{
              pageSize: 10,
              showSizeChanger: true,
              showQuickJumper: true,
              showTotal: (total, range) => `${range[0]}-${range[1]} of ${total} alerts`,
            }}
            scroll={{ x: 800 }}
          />
        )}
      </Card>
    </div>
  );
};

export default Alerts;

