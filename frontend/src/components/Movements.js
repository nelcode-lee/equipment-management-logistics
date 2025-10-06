import React, { useState, useEffect } from 'react';
import { Table, Tag, Input, Select, Button, Card, Space, message, Spin } from 'antd';
import { SearchOutlined, ReloadOutlined } from '@ant-design/icons';
import axios from 'axios';

const { Option } = Select;

const Movements = () => {
  const [movements, setMovements] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    customer_name: '',
    equipment_type: '',
  });

  useEffect(() => {
    fetchMovements();
  }, []);

  const fetchMovements = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      
      if (filters.customer_name) {
        params.append('customer_name', filters.customer_name);
      }
      if (filters.equipment_type) {
        params.append('equipment_type', filters.equipment_type);
      }
      
      const response = await axios.get(`http://localhost:8000/movements?${params.toString()}`);
      setMovements(response.data);
    } catch (error) {
      console.error('Error fetching movements:', error);
      message.error('Failed to fetch movements');
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  const handleSearch = () => {
    fetchMovements();
  };

  const handleReset = () => {
    setFilters({ customer_name: '', equipment_type: '' });
    fetchMovements();
  };

  const columns = [
    {
      title: 'Movement ID',
      dataIndex: 'movement_id',
      key: 'movement_id',
      width: 200,
      render: (id) => <code>{id.substring(0, 8)}...</code>,
    },
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
      title: 'Quantity',
      dataIndex: 'quantity',
      key: 'quantity',
      sorter: (a, b) => a.quantity - b.quantity,
    },
    {
      title: 'Direction',
      dataIndex: 'direction',
      key: 'direction',
      render: (direction) => (
        <Tag color={direction === 'in' ? 'green' : 'red'}>
          {direction === 'in' ? 'IN (To Customer)' : 'OUT (From Customer)'}
        </Tag>
      ),
      filters: [
        { text: 'IN (To Customer)', value: 'in' },
        { text: 'OUT (From Customer)', value: 'out' },
      ],
      onFilter: (value, record) => record.direction === value,
    },
    {
      title: 'Driver',
      dataIndex: 'driver_name',
      key: 'driver_name',
      render: (name) => name || 'Not specified',
    },
    {
      title: 'Confidence',
      dataIndex: 'confidence_score',
      key: 'confidence_score',
      render: (score) => (
        <Tag color={score > 0.8 ? 'green' : score > 0.6 ? 'orange' : 'red'}>
          {(score * 100).toFixed(0)}%
        </Tag>
      ),
      sorter: (a, b) => a.confidence_score - b.confidence_score,
    },
    {
      title: 'Verified',
      dataIndex: 'verified',
      key: 'verified',
      render: (verified) => (
        <Tag color={verified ? 'green' : 'default'}>
          {verified ? 'Yes' : 'No'}
        </Tag>
      ),
      filters: [
        { text: 'Verified', value: true },
        { text: 'Unverified', value: false },
      ],
      onFilter: (value, record) => record.verified === value,
    },
    {
      title: 'Timestamp',
      dataIndex: 'timestamp',
      key: 'timestamp',
      render: (timestamp) => new Date(timestamp).toLocaleString(),
      sorter: (a, b) => new Date(a.timestamp) - new Date(b.timestamp),
      defaultSortOrder: 'descend',
    },
  ];

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <Spin size="large" />
        <p>Loading movements...</p>
      </div>
    );
  }

  return (
    <div>
      <h2>Equipment Movement History</h2>
      
      <Card style={{ marginBottom: 16 }}>
        <Space wrap>
          <Input
            placeholder="Search by customer name"
            value={filters.customer_name}
            onChange={(e) => handleFilterChange('customer_name', e.target.value)}
            style={{ width: 200 }}
            prefix={<SearchOutlined />}
          />
          <Select
            placeholder="Filter by equipment type"
            value={filters.equipment_type}
            onChange={(value) => handleFilterChange('equipment_type', value)}
            style={{ width: 200 }}
            allowClear
          >
            <Option value="pallet">Pallet</Option>
            <Option value="cage">Cage</Option>
            <Option value="dolly">Dolly</Option>
            <Option value="stillage">Stillage</Option>
            <Option value="other">Other</Option>
          </Select>
          <Button type="primary" onClick={handleSearch}>
            Search
          </Button>
          <Button onClick={handleReset}>
            Reset
          </Button>
          <Button icon={<ReloadOutlined />} onClick={fetchMovements}>
            Refresh
          </Button>
        </Space>
      </Card>

      <Card>
        <Table
          dataSource={movements}
          columns={columns}
          rowKey="movement_id"
          pagination={{
            pageSize: 20,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total, range) => `${range[0]}-${range[1]} of ${total} movements`,
          }}
          scroll={{ x: 1200 }}
        />
      </Card>
    </div>
  );
};

export default Movements;

