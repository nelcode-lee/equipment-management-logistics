import React, { useState, useEffect } from 'react';
import { Table, Tag, Input, Select, Button, Card, Space, message, Spin, Statistic, Row, Col } from 'antd';
import { SearchOutlined, ReloadOutlined, BarChartOutlined } from '@ant-design/icons';
import axios from 'axios';
import API_BASE_URL from '../config';

const { Option } = Select;

const Balances = () => {
  const [balances, setBalances] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('');

  useEffect(() => {
    fetchBalances();
  }, [statusFilter]);

  const fetchBalances = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      
      if (statusFilter) {
        params.append('status', statusFilter);
      }
      
      const response = await axios.get(`${API_BASE_URL}/balances?${params.toString()}`);
      
      // Handle paginated response
      if (response.data.data) {
        setBalances(response.data.data);
        setTotal(response.data.total);
      } else {
        // Fallback for old API format
        setBalances(response.data);
        setTotal(response.data.length);
      }
    } catch (error) {
      console.error('Error fetching balances:', error);
      message.error('Failed to fetch balances');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'normal':
        return 'green';
      case 'over_threshold':
        return 'orange';
      case 'negative':
        return 'red';
      default:
        return 'default';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'normal':
        return 'Normal';
      case 'over_threshold':
        return 'Over Threshold';
      case 'negative':
        return 'Negative Balance';
      default:
        return status;
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
      render: (balance) => (
        <span style={{ 
          color: balance < 0 ? '#ff4d4f' : balance > 0 ? '#52c41a' : '#000000',
          fontWeight: 'bold'
        }}>
          {balance}
        </span>
      ),
    },
    {
      title: 'Threshold',
      dataIndex: 'threshold',
      key: 'threshold',
      sorter: (a, b) => a.threshold - b.threshold,
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status) => (
        <Tag color={getStatusColor(status)}>
          {getStatusText(status)}
        </Tag>
      ),
      filters: [
        { text: 'Normal', value: 'normal' },
        { text: 'Over Threshold', value: 'over_threshold' },
        { text: 'Negative Balance', value: 'negative' },
      ],
      onFilter: (value, record) => record.status === value,
    },
    {
      title: 'Last Movement',
      dataIndex: 'last_movement',
      key: 'last_movement',
      render: (timestamp) => new Date(timestamp).toLocaleString(),
      sorter: (a, b) => new Date(a.last_movement) - new Date(b.last_movement),
    },
  ];

  const normalBalances = balances.filter(b => b.status === 'normal');
  const overThresholdBalances = balances.filter(b => b.status === 'over_threshold');
  const negativeBalances = balances.filter(b => b.status === 'negative');
  const totalCustomers = new Set(balances.map(b => b.customer_name)).size;
  const displayTotal = total || balances.length;

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <Spin size="large" />
        <p>Loading balances...</p>
      </div>
    );
  }

  return (
    <div>
      <h2>Customer Equipment Balances</h2>
      
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="Total Customers"
              value={totalCustomers}
              prefix={<BarChartOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Normal Status"
              value={normalBalances.length}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Over Threshold"
              value={overThresholdBalances.length}
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Negative Balance"
              value={negativeBalances.length}
              valueStyle={{ color: '#ff4d4f' }}
            />
          </Card>
        </Col>
      </Row>

      <Card style={{ marginBottom: 16 }}>
        <Space wrap>
          <Select
            placeholder="Filter by status"
            value={statusFilter}
            onChange={setStatusFilter}
            style={{ width: 200 }}
            allowClear
          >
            <Option value="normal">Normal</Option>
            <Option value="over_threshold">Over Threshold</Option>
            <Option value="negative">Negative Balance</Option>
          </Select>
          <Button icon={<ReloadOutlined />} onClick={fetchBalances}>
            Refresh
          </Button>
        </Space>
      </Card>

      <Card>
        <Table
          dataSource={balances}
          columns={columns}
          rowKey={(record) => `${record.customer_name}-${record.equipment_type}`}
          loading={loading}
          pagination={{
            pageSize: 50,
            showSizeChanger: true,
            showQuickJumper: true,
            pageSizeOptions: ['20', '50', '100'],
            showTotal: (total, range) => `${range[0]}-${range[1]} of ${displayTotal} balances`,
          }}
          scroll={{ x: 800 }}
        />
      </Card>
    </div>
  );
};

export default Balances;

