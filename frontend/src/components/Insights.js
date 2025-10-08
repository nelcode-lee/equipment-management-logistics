import React, { useState, useEffect } from 'react';
import {
  Card,
  Row,
  Col,
  Statistic,
  Table,
  Tag,
  Progress,
  Alert,
  Button,
  Space,
  Typography,
  Divider,
  List,
  Avatar,
  Tooltip
} from 'antd';
import {
  RiseOutlined,
  FallOutlined,
  WarningOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  UserOutlined,
  TruckOutlined,
  ExclamationCircleOutlined,
  TrophyOutlined,
  AlertOutlined
} from '@ant-design/icons';
import axios from 'axios';
import API_BASE_URL from '../config';

const { Title, Text } = Typography;

const Insights = () => {
  const [loading, setLoading] = useState(true);
  const [insights, setInsights] = useState({
    equipmentStats: {},
    immediateActions: [],
    poorPerformers: {
      customers: [],
      drivers: []
    },
    trends: {}
  });

  useEffect(() => {
    fetchInsights();
  }, []);

  const fetchInsights = async () => {
    try {
      setLoading(true);
      
      // Fetch multiple data sources
      const [balancesResponse, movementsResponse, instructionsResponse] = await Promise.all([
        axios.get(`${API_BASE_URL}/balances`),
        axios.get(`${API_BASE_URL}/movements?limit=100`),
        axios.get(`${API_BASE_URL}/driver-instructions`)
      ]);

      const balances = balancesResponse.data;
      const movements = movementsResponse.data;
      const instructions = instructionsResponse.data;

      // Calculate equipment statistics
      const equipmentStats = calculateEquipmentStats(balances, movements);
      
      // Identify immediate actions
      const immediateActions = identifyImmediateActions(balances, instructions);
      
      // Find poor performers
      const poorPerformers = identifyPoorPerformers(balances, movements, instructions);
      
      // Calculate trends
      const trends = calculateTrends(movements);

      setInsights({
        equipmentStats,
        immediateActions,
        poorPerformers,
        trends
      });
    } catch (error) {
      console.error('Error fetching insights:', error);
    } finally {
      setLoading(false);
    }
  };

  const calculateEquipmentStats = (balances, movements) => {
    const stats = {
      totalEquipment: 0,
      overThreshold: 0,
      negativeBalances: 0,
      utilizationRate: 0,
      returnRate: 0
    };

    // Calculate totals
    balances.forEach(balance => {
      stats.totalEquipment += balance.current_balance;
      if (balance.status === 'over_threshold') stats.overThreshold++;
      if (balance.status === 'negative') stats.negativeBalances++;
    });

    // Calculate utilization rate (equipment in use vs total)
    const totalThreshold = balances.reduce((sum, b) => sum + b.threshold, 0);
    stats.utilizationRate = totalThreshold > 0 ? ((stats.totalEquipment / totalThreshold) * 100).toFixed(1) : 0;

    // Calculate return rate from movements
    const returnMovements = movements.filter(m => m.direction === 'in');
    const totalMovements = movements.length;
    stats.returnRate = totalMovements > 0 ? ((returnMovements.length / totalMovements) * 100).toFixed(1) : 0;

    return stats;
  };

  const identifyImmediateActions = (balances, instructions) => {
    const actions = [];

    // Critical over-threshold customers
    const criticalCustomers = balances.filter(b => 
      b.status === 'over_threshold' && b.current_balance > b.threshold * 1.5
    );
    criticalCustomers.forEach(customer => {
      actions.push({
        type: 'critical',
        title: `Critical: ${customer.customer_name}`,
        description: `${customer.equipment_type} balance is ${customer.current_balance} (threshold: ${customer.threshold})`,
        action: 'Immediate collection required',
        priority: 'high'
      });
    });

    // Overdue driver instructions
    const overdueInstructions = instructions.filter(i => 
      i.status === 'assigned' && 
      new Date(i.delivery_date) < new Date() &&
      new Date(i.delivery_date) < new Date(Date.now() - 24 * 60 * 60 * 1000) // 24 hours ago
    );
    overdueInstructions.forEach(instruction => {
      actions.push({
        type: 'overdue',
        title: `Overdue: ${instruction.customer_name}`,
        description: `Collection assigned to ${instruction.driver_name} on ${new Date(instruction.delivery_date).toLocaleDateString()}`,
        action: 'Follow up with driver',
        priority: 'medium'
      });
    });

    // Negative balance customers
    const negativeCustomers = balances.filter(b => b.status === 'negative');
    negativeCustomers.forEach(customer => {
      actions.push({
        type: 'negative',
        title: `Negative Balance: ${customer.customer_name}`,
        description: `${customer.equipment_type} balance is ${customer.current_balance}`,
        action: 'Investigate and resolve',
        priority: 'high'
      });
    });

    return actions.sort((a, b) => {
      const priorityOrder = { high: 3, medium: 2, low: 1 };
      return priorityOrder[b.priority] - priorityOrder[a.priority];
    });
  };

  const identifyPoorPerformers = (balances, movements, instructions) => {
    // Poor performing customers (high over-threshold rates)
    const customerPerformance = {};
    balances.forEach(balance => {
      if (!customerPerformance[balance.customer_name]) {
        customerPerformance[balance.customer_name] = {
          name: balance.customer_name,
          totalBalances: 0,
          overThreshold: 0,
          negativeBalances: 0,
          avgBalance: 0
        };
      }
      customerPerformance[balance.customer_name].totalBalances++;
      if (balance.status === 'over_threshold') customerPerformance[balance.customer_name].overThreshold++;
      if (balance.status === 'negative') customerPerformance[balance.customer_name].negativeBalances++;
      customerPerformance[balance.customer_name].avgBalance += balance.current_balance;
    });

    // Calculate performance scores
    Object.values(customerPerformance).forEach(customer => {
      customer.avgBalance = customer.avgBalance / customer.totalBalances;
      customer.overThresholdRate = (customer.overThreshold / customer.totalBalances) * 100;
      customer.performanceScore = 100 - (customer.overThresholdRate * 2) - (customer.negativeBalances * 10);
    });

    const poorCustomers = Object.values(customerPerformance)
      .filter(c => c.performanceScore < 70)
      .sort((a, b) => a.performanceScore - b.performanceScore)
      .slice(0, 5);

    // Poor performing drivers (based on instruction completion)
    const driverPerformance = {};
    instructions.forEach(instruction => {
      if (!driverPerformance[instruction.driver_name]) {
        driverPerformance[instruction.driver_name] = {
          name: instruction.driver_name,
          total: 0,
          completed: 0,
          failed: 0,
          unable: 0
        };
      }
      driverPerformance[instruction.driver_name].total++;
      if (instruction.status === 'completed') driverPerformance[instruction.driver_name].completed++;
      if (instruction.status === 'failed') driverPerformance[instruction.driver_name].failed++;
      if (instruction.status === 'unable_to_collect') driverPerformance[instruction.driver_name].unable++;
    });

    // Calculate driver performance scores
    Object.values(driverPerformance).forEach(driver => {
      driver.completionRate = (driver.completed / driver.total) * 100;
      driver.failureRate = ((driver.failed + driver.unable) / driver.total) * 100;
      driver.performanceScore = driver.completionRate - (driver.failureRate * 0.5);
    });

    const poorDrivers = Object.values(driverPerformance)
      .filter(d => d.performanceScore < 70 && d.total >= 3) // Only drivers with 3+ assignments
      .sort((a, b) => a.performanceScore - b.performanceScore)
      .slice(0, 5);

    return {
      customers: poorCustomers,
      drivers: poorDrivers
    };
  };

  const calculateTrends = (movements) => {
    const last7Days = movements.filter(m => 
      new Date(m.timestamp) > new Date(Date.now() - 7 * 24 * 60 * 60 * 1000)
    );
    const last30Days = movements.filter(m => 
      new Date(m.timestamp) > new Date(Date.now() - 30 * 24 * 60 * 60 * 1000)
    );

    return {
      movements7Days: last7Days.length,
      movements30Days: last30Days.length,
      returnRate7Days: last7Days.filter(m => m.direction === 'in').length,
      returnRate30Days: last30Days.filter(m => m.direction === 'in').length
    };
  };

  const getActionIcon = (type) => {
    switch (type) {
      case 'critical': return <ExclamationCircleOutlined style={{ color: '#ff4d4f' }} />;
      case 'overdue': return <ClockCircleOutlined style={{ color: '#faad14' }} />;
      case 'negative': return <WarningOutlined style={{ color: '#ff4d4f' }} />;
      default: return <AlertOutlined />;
    }
  };

  const getActionColor = (priority) => {
    switch (priority) {
      case 'high': return '#ff4d4f';
      case 'medium': return '#faad14';
      case 'low': return '#52c41a';
      default: return '#1890ff';
    }
  };

  const actionColumns = [
    {
      title: 'Action',
      dataIndex: 'title',
      key: 'title',
      render: (title, record) => (
        <Space>
          {getActionIcon(record.type)}
          <div>
            <Text strong>{title}</Text>
            <br />
            <Text type="secondary" style={{ fontSize: '12px' }}>
              {record.description}
            </Text>
          </div>
        </Space>
      ),
    },
    {
      title: 'Required Action',
      dataIndex: 'action',
      key: 'action',
      render: (action) => <Text>{action}</Text>,
    },
    {
      title: 'Priority',
      dataIndex: 'priority',
      key: 'priority',
      render: (priority) => (
        <Tag color={getActionColor(priority)}>
          {priority.toUpperCase()}
        </Tag>
      ),
    },
  ];

  const customerColumns = [
    {
      title: 'Customer',
      dataIndex: 'name',
      key: 'name',
      render: (name) => (
        <Space>
          <Avatar icon={<UserOutlined />} />
          <Text strong>{name}</Text>
        </Space>
      ),
    },
    {
      title: 'Performance Score',
      dataIndex: 'performanceScore',
      key: 'performanceScore',
      render: (score) => (
        <div>
          <Progress 
            percent={Math.max(0, score)} 
            size="small" 
            status={score < 50 ? 'exception' : score < 70 ? 'active' : 'success'}
          />
          <Text style={{ fontSize: '12px' }}>{score.toFixed(1)}%</Text>
        </div>
      ),
    },
    {
      title: 'Over-Threshold Rate',
      dataIndex: 'overThresholdRate',
      key: 'overThresholdRate',
      render: (rate) => (
        <Text type={rate > 50 ? 'danger' : rate > 25 ? 'warning' : 'success'}>
          {rate.toFixed(1)}%
        </Text>
      ),
    },
    {
      title: 'Avg Balance',
      dataIndex: 'avgBalance',
      key: 'avgBalance',
      render: (balance) => <Text>{balance.toFixed(1)}</Text>,
    },
  ];

  const driverColumns = [
    {
      title: 'Driver',
      dataIndex: 'name',
      key: 'name',
      render: (name) => (
        <Space>
          <Avatar icon={<TruckOutlined />} />
          <Text strong>{name}</Text>
        </Space>
      ),
    },
    {
      title: 'Performance Score',
      dataIndex: 'performanceScore',
      key: 'performanceScore',
      render: (score) => (
        <div>
          <Progress 
            percent={Math.max(0, score)} 
            size="small" 
            status={score < 50 ? 'exception' : score < 70 ? 'active' : 'success'}
          />
          <Text style={{ fontSize: '12px' }}>{score.toFixed(1)}%</Text>
        </div>
      ),
    },
    {
      title: 'Completion Rate',
      dataIndex: 'completionRate',
      key: 'completionRate',
      render: (rate) => (
        <Text type={rate > 80 ? 'success' : rate > 60 ? 'warning' : 'danger'}>
          {rate.toFixed(1)}%
        </Text>
      ),
    },
    {
      title: 'Failure Rate',
      dataIndex: 'failureRate',
      key: 'failureRate',
      render: (rate) => (
        <Text type={rate > 20 ? 'danger' : rate > 10 ? 'warning' : 'success'}>
          {rate.toFixed(1)}%
        </Text>
      ),
    },
    {
      title: 'Total Assignments',
      dataIndex: 'total',
      key: 'total',
      render: (total) => <Text>{total}</Text>,
    },
  ];

  return (
    <div style={{ padding: '24px' }}>
      <Title level={2}>
        <TrophyOutlined style={{ marginRight: '8px' }} />
        Equipment Management Insights
      </Title>
      
      {/* Equipment Statistics */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Total Equipment"
              value={insights.equipmentStats.totalEquipment}
              prefix={<RiseOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Over Threshold"
              value={insights.equipmentStats.overThreshold}
              prefix={<WarningOutlined />}
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Utilization Rate"
              value={insights.equipmentStats.utilizationRate}
              suffix="%"
              prefix={<RiseOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Return Rate"
              value={insights.equipmentStats.returnRate}
              suffix="%"
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
      </Row>

      {/* Immediate Actions */}
      <Card 
        title={
          <Space>
            <AlertOutlined />
            Immediate Actions Required
          </Space>
        }
        style={{ marginBottom: '24px' }}
        extra={
          <Button type="primary" onClick={fetchInsights}>
            Refresh
          </Button>
        }
      >
        {insights.immediateActions.length > 0 ? (
          <Table
            columns={actionColumns}
            dataSource={insights.immediateActions}
            rowKey="title"
            pagination={false}
            size="small"
          />
        ) : (
          <Alert
            message="No immediate actions required"
            description="All systems are operating normally."
            type="success"
            showIcon
          />
        )}
      </Card>

      {/* Performance Analysis */}
      <Row gutter={[16, 16]}>
        <Col xs={24} lg={12}>
          <Card 
            title={
              <Space>
                <UserOutlined />
                Poor Performing Customers
              </Space>
            }
            style={{ marginBottom: '16px' }}
          >
            {insights.poorPerformers.customers.length > 0 ? (
              <Table
                columns={customerColumns}
                dataSource={insights.poorPerformers.customers}
                rowKey="name"
                pagination={false}
                size="small"
              />
            ) : (
              <Alert
                message="All customers performing well"
                description="No customers with poor performance identified."
                type="success"
                showIcon
              />
            )}
          </Card>
        </Col>
        
        <Col xs={24} lg={12}>
          <Card 
            title={
              <Space>
                <TruckOutlined />
                Poor Performing Drivers
              </Space>
            }
            style={{ marginBottom: '16px' }}
          >
            {insights.poorPerformers.drivers.length > 0 ? (
              <Table
                columns={driverColumns}
                dataSource={insights.poorPerformers.drivers}
                rowKey="name"
                pagination={false}
                size="small"
              />
            ) : (
              <Alert
                message="All drivers performing well"
                description="No drivers with poor performance identified."
                type="success"
                showIcon
              />
            )}
          </Card>
        </Col>
      </Row>

      {/* Trends Summary */}
      <Card title="Recent Trends" style={{ marginTop: '16px' }}>
        <Row gutter={[16, 16]}>
          <Col xs={24} sm={12}>
            <Statistic
              title="Movements (Last 7 Days)"
              value={insights.trends.movements7Days}
              prefix={<RiseOutlined />}
            />
          </Col>
          <Col xs={24} sm={12}>
            <Statistic
              title="Returns (Last 7 Days)"
              value={insights.trends.returnRate7Days}
              prefix={<CheckCircleOutlined />}
            />
          </Col>
        </Row>
      </Card>
    </div>
  );
};

export default Insights;
