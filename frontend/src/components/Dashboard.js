import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Statistic, Table, Tag, Spin, Alert, Progress, Typography, Space, Divider } from 'antd';
import { 
  UploadOutlined, 
  AlertOutlined, 
  HistoryOutlined,
  BarChartOutlined,
  RiseOutlined,
  FallOutlined,
  CheckCircleOutlined,
  WarningOutlined,
  ClockCircleOutlined,
  TrophyOutlined,
  UserOutlined,
  TruckOutlined
} from '@ant-design/icons';
import axios from 'axios';

const { Title, Text } = Typography;

const Dashboard = () => {
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    totalMovements: 0,
    totalCustomers: 0,
    activeAlerts: 0,
    overThreshold: 0,
    monthlyTrends: {},
    equipmentBreakdown: {},
    customerPerformance: {},
    driverPerformance: {},
    utilizationMetrics: {}
  });
  const [recentMovements, setRecentMovements] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [monthlyData, setMonthlyData] = useState([]);
  const [topPerformers, setTopPerformers] = useState({ customers: [], drivers: [] });
  const [companyLogo, setCompanyLogo] = useState(null);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      
      // Fetch all data in parallel
      const [healthResponse, movementsResponse, alertsResponse, balancesResponse, instructionsResponse, logoResponse] = await Promise.all([
        axios.get('http://localhost:8000/health'),
        axios.get('http://localhost:8000/movements?limit=100'),
        axios.get('http://localhost:8000/alerts'),
        axios.get('http://localhost:8000/balances'),
        axios.get('http://localhost:8000/driver-instructions'),
        axios.get('http://localhost:8000/company/logo').catch(() => ({ data: { logo: null } }))
      ]);

      const healthData = healthResponse.data;
      const movementsData = movementsResponse.data;
      const alertsData = alertsResponse.data;
      const balancesData = balancesResponse.data;
      const instructionsData = instructionsResponse.data;

      // Calculate comprehensive metrics
      const monthlyTrends = calculateMonthlyTrends(movementsData);
      const equipmentBreakdown = calculateEquipmentBreakdown(movementsData, balancesData);
      const customerPerformance = calculateCustomerPerformance(balancesData);
      const driverPerformance = calculateDriverPerformance(instructionsData);
      const utilizationMetrics = calculateUtilizationMetrics(balancesData, movementsData);
      const topPerformers = calculateTopPerformers(balancesData, instructionsData);

      setStats({
        totalMovements: healthData.total_movements,
        totalCustomers: healthData.total_customers,
        activeAlerts: alertsData.length,
        overThreshold: balancesData.filter(b => b.status === 'over_threshold').length,
        monthlyTrends,
        equipmentBreakdown,
        customerPerformance,
        driverPerformance,
        utilizationMetrics
      });
      
      setRecentMovements(movementsData.slice(0, 5));
      setAlerts(alertsData);
      setMonthlyData(monthlyTrends);
      setTopPerformers(topPerformers);
      setCompanyLogo(logoResponse.data.logo);
      
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const calculateMonthlyTrends = (movements) => {
    const now = new Date();
    const last30Days = [];
    
    for (let i = 29; i >= 0; i--) {
      const date = new Date(now);
      date.setDate(date.getDate() - i);
      const dateStr = date.toISOString().split('T')[0];
      
      const dayMovements = movements.filter(m => 
        m.timestamp.startsWith(dateStr)
      );
      
      last30Days.push({
        date: dateStr,
        movements: dayMovements.length,
        returns: dayMovements.filter(m => m.direction === 'in').length,
        deliveries: dayMovements.filter(m => m.direction === 'out').length
      });
    }
    
    return last30Days;
  };

  const calculateEquipmentBreakdown = (movements, balances) => {
    const breakdown = {};
    
    // Equipment type distribution from movements
    movements.forEach(movement => {
      if (!breakdown[movement.equipment_type]) {
        breakdown[movement.equipment_type] = {
          totalMovements: 0,
          returns: 0,
          deliveries: 0,
          currentBalance: 0,
          threshold: 0
        };
      }
      breakdown[movement.equipment_type].totalMovements++;
      if (movement.direction === 'in') {
        breakdown[movement.equipment_type].returns++;
      } else {
        breakdown[movement.equipment_type].deliveries++;
      }
    });

    // Add current balances and thresholds
    balances.forEach(balance => {
      if (breakdown[balance.equipment_type]) {
        breakdown[balance.equipment_type].currentBalance += balance.current_balance;
        breakdown[balance.equipment_type].threshold += balance.threshold;
      }
    });

    return breakdown;
  };

  const calculateCustomerPerformance = (balances) => {
    const performance = {};
    
    balances.forEach(balance => {
      if (!performance[balance.customer_name]) {
        performance[balance.customer_name] = {
          totalBalances: 0,
          overThreshold: 0,
          negativeBalances: 0,
          avgBalance: 0,
          totalEquipment: 0
        };
      }
      
      performance[balance.customer_name].totalBalances++;
      performance[balance.customer_name].totalEquipment += balance.current_balance;
      
      if (balance.status === 'over_threshold') {
        performance[balance.customer_name].overThreshold++;
      }
      if (balance.status === 'negative') {
        performance[balance.customer_name].negativeBalances++;
      }
    });

    // Calculate performance scores
    Object.keys(performance).forEach(customer => {
      const p = performance[customer];
      p.avgBalance = p.totalEquipment / p.totalBalances;
      p.overThresholdRate = (p.overThreshold / p.totalBalances) * 100;
      p.performanceScore = 100 - (p.overThresholdRate * 2) - (p.negativeBalances * 10);
    });

    return performance;
  };

  const calculateDriverPerformance = (instructions) => {
    const performance = {};
    
    instructions.forEach(instruction => {
      if (!performance[instruction.driver_name]) {
        performance[instruction.driver_name] = {
          total: 0,
          completed: 0,
          failed: 0,
          unable: 0
        };
      }
      
      performance[instruction.driver_name].total++;
      if (instruction.status === 'completed') {
        performance[instruction.driver_name].completed++;
      } else if (instruction.status === 'failed') {
        performance[instruction.driver_name].failed++;
      } else if (instruction.status === 'unable_to_collect') {
        performance[instruction.driver_name].unable++;
      }
    });

    // Calculate performance scores
    Object.keys(performance).forEach(driver => {
      const p = performance[driver];
      p.completionRate = (p.completed / p.total) * 100;
      p.failureRate = ((p.failed + p.unable) / p.total) * 100;
      p.performanceScore = p.completionRate - (p.failureRate * 0.5);
    });

    return performance;
  };

  const calculateUtilizationMetrics = (balances, movements) => {
    const totalEquipment = balances.reduce((sum, b) => sum + b.current_balance, 0);
    const totalThreshold = balances.reduce((sum, b) => sum + b.threshold, 0);
    const returnMovements = movements.filter(m => m.direction === 'in').length;
    const totalMovements = movements.length;
    
    return {
      utilizationRate: totalThreshold > 0 ? (totalEquipment / totalThreshold) * 100 : 0,
      returnRate: totalMovements > 0 ? (returnMovements / totalMovements) * 100 : 0,
      totalEquipment,
      totalThreshold,
      activeCustomers: new Set(balances.map(b => b.customer_name)).size
    };
  };

  const calculateTopPerformers = (balances, instructions) => {
    const customerPerformance = calculateCustomerPerformance(balances);
    const driverPerformance = calculateDriverPerformance(instructions);
    
    const topCustomers = Object.entries(customerPerformance)
      .filter(([_, p]) => p.totalBalances >= 2)
      .sort(([_, a], [__, b]) => b.performanceScore - a.performanceScore)
      .slice(0, 3)
      .map(([name, perf]) => ({ name, ...perf }));

    const topDrivers = Object.entries(driverPerformance)
      .filter(([_, p]) => p.total >= 3)
      .sort(([_, a], [__, b]) => b.performanceScore - a.performanceScore)
      .slice(0, 3)
      .map(([name, perf]) => ({ name, ...perf }));

    return { customers: topCustomers, drivers: topDrivers };
  };

  const movementColumns = [
    {
      title: 'Customer',
      dataIndex: 'customer_name',
      key: 'customer_name',
    },
    {
      title: 'Equipment',
      dataIndex: 'equipment_type',
      key: 'equipment_type',
      render: (type) => <Tag color="blue">{type}</Tag>
    },
    {
      title: 'Quantity',
      dataIndex: 'quantity',
      key: 'quantity',
    },
    {
      title: 'Direction',
      dataIndex: 'direction',
      key: 'direction',
      render: (direction) => (
        <Tag color={direction === 'in' ? 'green' : 'red'}>
          {direction === 'in' ? 'IN' : 'OUT'}
        </Tag>
      )
    },
    {
      title: 'Confidence',
      dataIndex: 'confidence_score',
      key: 'confidence_score',
      render: (score) => (
        <Tag color={score > 0.8 ? 'green' : score > 0.6 ? 'orange' : 'red'}>
          {(score * 100).toFixed(0)}%
        </Tag>
      )
    },
    {
      title: 'Time',
      dataIndex: 'timestamp',
      key: 'timestamp',
      render: (timestamp) => new Date(timestamp).toLocaleString()
    }
  ];

  const alertColumns = [
    {
      title: 'Customer',
      dataIndex: 'customer_name',
      key: 'customer_name',
    },
    {
      title: 'Equipment',
      dataIndex: 'equipment_type',
      key: 'equipment_type',
      render: (type) => <Tag color="blue">{type}</Tag>
    },
    {
      title: 'Current Balance',
      dataIndex: 'current_balance',
      key: 'current_balance',
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
      render: (excess) => <Tag color="red">+{excess}</Tag>
    },
    {
      title: 'Priority',
      dataIndex: 'priority',
      key: 'priority',
      render: (priority) => (
        <Tag color={priority === 'high' ? 'red' : 'orange'}>
          {priority.toUpperCase()}
        </Tag>
      )
    }
  ];

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <Spin size="large" />
        <p>Loading dashboard data...</p>
      </div>
    );
  }

  return (
    <div style={{ padding: '24px' }}>
      <Title level={2}>
        <TrophyOutlined style={{ marginRight: '8px' }} />
        Dashboard Overview
      </Title>
      
      {/* Key Metrics Row */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Total Movements"
              value={stats.totalMovements}
              prefix={<HistoryOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Active Customers"
              value={stats.totalCustomers}
              prefix={<UserOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Active Alerts"
              value={stats.activeAlerts}
              prefix={<AlertOutlined />}
              valueStyle={{ color: stats.activeAlerts > 0 ? '#cf1322' : '#3f8600' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Over Threshold"
              value={stats.overThreshold}
              prefix={<WarningOutlined />}
              valueStyle={{ color: stats.overThreshold > 0 ? '#cf1322' : '#3f8600' }}
            />
          </Card>
        </Col>
      </Row>

      {/* Performance Metrics Row */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Utilization Rate"
              value={stats.utilizationMetrics.utilizationRate?.toFixed(1) || 0}
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
              value={stats.utilizationMetrics.returnRate?.toFixed(1) || 0}
              suffix="%"
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Total Equipment"
              value={stats.utilizationMetrics.totalEquipment || 0}
              prefix={<BarChartOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Active Customers"
              value={stats.utilizationMetrics.activeCustomers || 0}
              prefix={<UserOutlined />}
              valueStyle={{ color: '#722ed1' }}
            />
          </Card>
        </Col>
      </Row>

      {/* Equipment Breakdown */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col xs={24} lg={12}>
          <Card title="Equipment Type Breakdown" size="small">
            {Object.entries(stats.equipmentBreakdown).map(([type, data]) => (
              <div key={type} style={{ marginBottom: '16px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                  <Text strong>{type}</Text>
                  <Text>{data.totalMovements} movements</Text>
                </div>
                <Progress 
                  percent={(data.returns / data.totalMovements) * 100} 
                  size="small"
                  format={() => `${data.returns} returns / ${data.deliveries} deliveries`}
                />
                <div style={{ marginTop: '4px', fontSize: '12px', color: '#666' }}>
                  Current: {data.currentBalance} | Threshold: {data.threshold}
                </div>
              </div>
            ))}
          </Card>
        </Col>
        
        <Col xs={24} lg={12}>
          <Card title="Top Performers" size="small">
            <div style={{ marginBottom: '16px' }}>
              <Title level={5}>🏆 Best Customers</Title>
              {topPerformers.customers.map((customer, index) => (
                <div key={customer.name} style={{ marginBottom: '8px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Text>{index + 1}. {customer.name}</Text>
                    <Text type="success">{customer.performanceScore.toFixed(1)}%</Text>
                  </div>
                  <Progress 
                    percent={Math.max(0, customer.performanceScore)} 
                    size="small" 
                    showInfo={false}
                  />
                </div>
              ))}
            </div>
            
            <Divider />
            
            <div>
              <Title level={5}>🚛 Best Drivers</Title>
              {topPerformers.drivers.map((driver, index) => (
                <div key={driver.name} style={{ marginBottom: '8px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Text>{index + 1}. {driver.name}</Text>
                    <Text type="success">{driver.performanceScore.toFixed(1)}%</Text>
                  </div>
                  <Progress 
                    percent={Math.max(0, driver.performanceScore)} 
                    size="small" 
                    showInfo={false}
                  />
                </div>
              ))}
            </div>
          </Card>
        </Col>
      </Row>

      {/* Monthly Trends */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col span={24}>
          <Card title="30-Day Movement Trends" size="small">
            <Row gutter={[8, 8]}>
              {monthlyData.slice(-7).map((day, index) => (
                <Col xs={24} sm={12} md={8} lg={3} key={day.date}>
                  <Card size="small" style={{ textAlign: 'center' }}>
                    <Text style={{ fontSize: '12px' }}>
                      {new Date(day.date).toLocaleDateString('en-GB', { 
                        month: 'short', 
                        day: 'numeric' 
                      })}
                    </Text>
                    <div style={{ marginTop: '8px' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px' }}>
                        <Text type="success">↗ {day.returns}</Text>
                        <Text type="danger">↘ {day.deliveries}</Text>
                      </div>
                      <Progress 
                        percent={(day.returns / Math.max(day.movements, 1)) * 100} 
                        size="small" 
                        showInfo={false}
                        strokeColor="#52c41a"
                      />
                    </div>
                  </Card>
                </Col>
              ))}
            </Row>
          </Card>
        </Col>
      </Row>

      {/* Recent Activity */}
      <Row gutter={[16, 16]}>
        <Col xs={24} lg={12}>
          <Card title="Recent Movements" size="small">
            <Table
              dataSource={recentMovements}
              columns={movementColumns}
              pagination={false}
              size="small"
              rowKey="movement_id"
            />
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card title="Active Alerts" size="small">
            {alerts.length === 0 ? (
              <Alert
                message="No active alerts"
                description="All customers are within their equipment thresholds."
                type="success"
                showIcon
              />
            ) : (
              <Table
                dataSource={alerts}
                columns={alertColumns}
                pagination={false}
                size="small"
                rowKey="customer_name"
              />
            )}
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Dashboard;

