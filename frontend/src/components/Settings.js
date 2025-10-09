import React, { useState, useEffect } from 'react';
import { Card, Form, Input, Button, Table, Tag, Modal, message, Select, InputNumber, Space, Tabs, Divider, Typography, Upload, Avatar } from 'antd';
import { SettingOutlined, PlusOutlined, EditOutlined, DeleteOutlined, SaveOutlined, UploadOutlined, UserOutlined, ToolOutlined } from '@ant-design/icons';
import axios from 'axios';
import API_BASE_URL from '../config';
import EquipmentManagement from './EquipmentManagement';

const { Option } = Select;
const { TabPane } = Tabs;
const { Title, Text } = Typography;

const Settings = () => {
  const [loading, setLoading] = useState(false);
  const [customers, setCustomers] = useState([]);
  const [thresholds, setThresholds] = useState({});
  const [modalVisible, setModalVisible] = useState(false);
  const [editingCustomer, setEditingCustomer] = useState(null);
  const [form] = Form.useForm();
  const [companyLogo, setCompanyLogo] = useState(null);
  const [logoLoading, setLogoLoading] = useState(false);
  const [equipmentSpecs, setEquipmentSpecs] = useState([]);
  const [specThresholds, setSpecThresholds] = useState({});

  // Default equipment types
  const equipmentTypes = [
    { value: 'pallet', label: 'Pallet', defaultThreshold: 50 },
    { value: 'cage', label: 'Cage', defaultThreshold: 30 },
    { value: 'dolly', label: 'Dolly', defaultThreshold: 25 },
    { value: 'stillage', label: 'Stillage', defaultThreshold: 15 }
  ];

  useEffect(() => {
    fetchCustomers();
    fetchThresholds();
    fetchCompanyLogo();
    fetchEquipmentSpecs();
  }, []);

  const fetchCustomers = async () => {
    try {
      setLoading(true);
      // Get customers from the customers endpoint (more reliable than movements)
      const response = await axios.get(`${API_BASE_URL}/customers`);
      const customersData = response.data;
      
      // Map to the format expected by the component
      const customerList = customersData.map(customer => ({
        id: customer.id,
        name: customer.customer_name,
        location: customer.city || customer.country || 'UK',
        contact: customer.contact_person || '',
        email: customer.email || '',
        phone: customer.phone || '',
        status: customer.status || 'active'
      }));
      
      setCustomers(customerList);
    } catch (error) {
      console.error('Error fetching customers:', error);
      message.error('Failed to fetch customers');
    } finally {
      setLoading(false);
    }
  };

  const fetchThresholds = async () => {
    try {
      // Get current thresholds from balances
      const response = await axios.get(`${API_BASE_URL}/balances`);
      // Handle paginated response format
      const balances = response.data.data || response.data;
      
      const thresholdMap = {};
      balances.forEach(balance => {
        const key = `${balance.customer_name}_${balance.equipment_type}`;
        thresholdMap[key] = balance.threshold;
      });
      
      setThresholds(thresholdMap);
    } catch (error) {
      console.error('Error fetching thresholds:', error);
    }
  };

  const fetchEquipmentSpecs = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/equipment-specifications?is_active=true`);
      setEquipmentSpecs(response.data);
      
      // Initialize spec thresholds with default values
      const specThresholdsData = {};
      response.data.forEach(spec => {
        const key = `${spec.equipment_type}_${spec.name}`;
        specThresholdsData[key] = spec.default_threshold;
      });
      setSpecThresholds(specThresholdsData);
    } catch (error) {
      console.error('Error fetching equipment specifications:', error);
    }
  };

  const handleAddCustomer = () => {
    setEditingCustomer(null);
    form.resetFields();
    setModalVisible(true);
  };

  const handleEditCustomer = (customer) => {
    setEditingCustomer(customer);
    form.setFieldsValue(customer);
    setModalVisible(true);
  };

  const handleSaveCustomer = async (values) => {
    try {
      if (editingCustomer) {
        // Update existing customer
        const updatedCustomers = customers.map(c => 
          c.id === editingCustomer.id ? { ...c, ...values } : c
        );
        setCustomers(updatedCustomers);
        message.success('Customer updated successfully');
      } else {
        // Add new customer
        const newCustomer = {
          id: values.name,
          ...values,
          status: 'active'
        };
        setCustomers([...customers, newCustomer]);
        message.success('Customer added successfully');
      }
      
      setModalVisible(false);
      form.resetFields();
    } catch (error) {
      message.error('Failed to save customer');
    }
  };

  const handleDeleteCustomer = (customer) => {
    Modal.confirm({
      title: 'Delete Customer',
      content: `Are you sure you want to delete ${customer.name}?`,
      onOk() {
        const updatedCustomers = customers.filter(c => c.id !== customer.id);
        setCustomers(updatedCustomers);
        message.success('Customer deleted successfully');
      }
    });
  };

  const handleThresholdChange = async (customerName, equipmentType, newThreshold) => {
    try {
      const response = await axios.put(
        `${API_BASE_URL}/customers/${encodeURIComponent(customerName)}/thresholds/${equipmentType}`,
        null,
        { params: { threshold: newThreshold } }
      );
      
      const key = `${customerName}_${equipmentType}`;
      setThresholds(prev => ({
        ...prev,
        [key]: newThreshold
      }));
      
      message.success(`Threshold updated for ${customerName} - ${equipmentType}`);
    } catch (error) {
      console.error('Error updating threshold:', error);
      message.error('Failed to update threshold');
    }
  };

  const handleSpecThresholdChange = async (specId, newThreshold) => {
    try {
      // Update the equipment specification's default threshold
      const response = await axios.put(
        `${API_BASE_URL}/equipment-specifications/${specId}`,
        { default_threshold: newThreshold }
      );
      
      // Update local state
      setEquipmentSpecs(prev => 
        prev.map(spec => 
          spec.id === specId 
            ? { ...spec, default_threshold: newThreshold }
            : spec
        )
      );
      
      setSpecThresholds(prev => ({
        ...prev,
        [specId]: newThreshold
      }));
      
      message.success(`Default threshold updated for ${response.data.name}`);
    } catch (error) {
      console.error('Error updating spec threshold:', error);
      message.error('Failed to update equipment specification threshold');
    }
  };

  // Logo management functions
  const fetchCompanyLogo = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/company/logo`);
      if (response.data.logo) {
        setCompanyLogo(response.data.logo);
      }
    } catch (error) {
      console.error('Error fetching logo:', error);
      // Logo doesn't exist yet, that's fine
    }
  };

  const handleLogoUpload = async (file) => {
    setLogoLoading(true);
    try {
      const formData = new FormData();
      formData.append('logo', file);
      
      const response = await axios.post(`${API_BASE_URL}/company/logo`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      setCompanyLogo(response.data.logo_url);
      message.success('Company logo updated successfully!');
    } catch (error) {
      console.error('Error uploading logo:', error);
      message.error('Failed to upload logo');
    } finally {
      setLogoLoading(false);
    }
    return false; // Prevent default upload
  };

  const handleLogoRemove = async () => {
    try {
      await axios.delete(`${API_BASE_URL}/company/logo`);
      setCompanyLogo(null);
      message.success('Company logo removed successfully!');
    } catch (error) {
      console.error('Error removing logo:', error);
      message.error('Failed to remove logo');
    }
  };

  const customerColumns = [
    {
      title: 'Customer Name',
      dataIndex: 'name',
      key: 'name',
      render: (text) => <strong>{text}</strong>
    },
    {
      title: 'Location',
      dataIndex: 'location',
      key: 'location'
    },
    {
      title: 'Contact',
      dataIndex: 'contact',
      key: 'contact'
    },
    {
      title: 'Email',
      dataIndex: 'email',
      key: 'email'
    },
    {
      title: 'Phone',
      dataIndex: 'phone',
      key: 'phone'
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status) => (
        <Tag color={status === 'active' ? 'green' : 'red'}>
          {status.toUpperCase()}
        </Tag>
      )
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_, record) => (
        <Space>
          <Button
            type="primary"
            size="small"
            icon={<EditOutlined />}
            onClick={() => handleEditCustomer(record)}
          >
            Edit
          </Button>
          <Button
            type="default"
            size="small"
            icon={<DeleteOutlined />}
            onClick={() => handleDeleteCustomer(record)}
            danger
          >
            Delete
          </Button>
        </Space>
      )
    }
  ];

  const thresholdColumns = [
    {
      title: 'Customer',
      dataIndex: 'customer_name',
      key: 'customer_name',
      render: (text) => <strong>{text}</strong>
    },
    {
      title: 'Equipment Type',
      dataIndex: 'equipment_type',
      key: 'equipment_type',
      render: (type) => <Tag color="blue">{type}</Tag>
    },
    {
      title: 'Current Threshold',
      dataIndex: 'threshold',
      key: 'threshold',
      render: (threshold, record) => (
        <InputNumber
          min={1}
          max={1000}
          value={threshold}
          onChange={(value) => handleThresholdChange(record.customer_name, record.equipment_type, value)}
          style={{ width: 100 }}
        />
      )
    },
    {
      title: 'Current Balance',
      dataIndex: 'current_balance',
      key: 'current_balance',
      render: (balance, record) => (
        <span style={{ 
          color: balance > record.threshold ? '#ff4d4f' : 
                 balance < 0 ? '#ff4d4f' : '#52c41a' 
        }}>
          {balance}
        </span>
      )
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status) => {
        const colors = {
          normal: 'green',
          over_threshold: 'red',
          negative: 'orange'
        };
        return <Tag color={colors[status]}>{status.replace('_', ' ').toUpperCase()}</Tag>;
      }
    }
  ];

  return (
    <div>
      <div style={{ marginBottom: '24px' }}>
        <Title level={2}>
          <SettingOutlined /> System Settings
        </Title>
        <Text type="secondary">
          Manage customers, equipment thresholds, and system configuration
        </Text>
      </div>

      <Tabs defaultActiveKey="customers">
        <TabPane tab="Customer Management" key="customers">
          <Card>
            <div style={{ marginBottom: '16px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Title level={4}>Customers</Title>
              <Button
                type="primary"
                icon={<PlusOutlined />}
                onClick={handleAddCustomer}
              >
                Add Customer
              </Button>
            </div>
            
            <Table
              columns={customerColumns}
              dataSource={customers}
              rowKey="id"
              loading={loading}
              pagination={{ pageSize: 10 }}
              scroll={{ x: 800 }}
            />
          </Card>
        </TabPane>

        <TabPane tab="Equipment Thresholds" key="thresholds">
          <Card>
            <div style={{ marginBottom: '16px' }}>
              <Title level={4}>Equipment Thresholds</Title>
              <Text type="secondary">
                Set maximum equipment quantities allowed per customer. When exceeded, collection instructions will be generated.
              </Text>
            </div>
            
            <ThresholdsTable 
              onThresholdChange={handleThresholdChange}
              equipmentTypes={equipmentTypes}
            />
          </Card>
          
          <Card style={{ marginTop: '16px' }}>
            <div style={{ marginBottom: '16px' }}>
              <Title level={4}>Equipment Specification Thresholds</Title>
              <Text type="secondary">
                Set default thresholds for specific equipment types with colors, sizes, and grades.
              </Text>
            </div>
            
            <div style={{ marginBottom: '16px' }}>
              {equipmentSpecs.length > 0 ? (
                <div>
                  {Object.entries(
                    equipmentSpecs.reduce((acc, spec) => {
                      if (!acc[spec.equipment_type]) {
                        acc[spec.equipment_type] = [];
                      }
                      acc[spec.equipment_type].push(spec);
                      return acc;
                    }, {})
                  ).map(([equipmentType, specs]) => (
                    <div key={equipmentType} style={{ marginBottom: '24px' }}>
                      <Title level={5} style={{ textTransform: 'capitalize', marginBottom: '12px' }}>
                        {equipmentType} Specifications
                      </Title>
                      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '12px' }}>
                        {specs.map(spec => (
                          <div key={spec.id} style={{ 
                            border: '1px solid #d9d9d9', 
                            borderRadius: '6px', 
                            padding: '12px',
                            backgroundColor: '#fafafa'
                          }}>
                            <div style={{ marginBottom: '8px' }}>
                              <Text strong>{spec.name}</Text>
                              <div style={{ marginTop: '4px' }}>
                                {spec.color && <Tag color="blue" size="small">{spec.color}</Tag>}
                                {spec.size && <Tag color="green" size="small">{spec.size}</Tag>}
                                {spec.grade && <Tag color="orange" size="small">{spec.grade}</Tag>}
                              </div>
                              {spec.description && (
                                <Text type="secondary" style={{ fontSize: '12px', display: 'block', marginTop: '4px' }}>
                                  {spec.description}
                                </Text>
                              )}
                            </div>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                              <Text style={{ fontSize: '12px' }}>Threshold:</Text>
                              <InputNumber
                                min={1}
                                max={1000}
                                value={spec.default_threshold}
                                onChange={(value) => handleSpecThresholdChange(spec.id, value)}
                                size="small"
                                style={{ width: '80px' }}
                              />
                              <Text type="secondary" style={{ fontSize: '12px' }}>units</Text>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div style={{ textAlign: 'center', padding: '40px' }}>
                  <Text type="secondary">No equipment specifications found. Add some in the Equipment Management tab.</Text>
                </div>
              )}
            </div>
          </Card>
        </TabPane>

        <TabPane tab="System Configuration" key="config">
          <Card>
            <Title level={4}>System Configuration</Title>
            <Divider />
            
            <div style={{ marginBottom: '24px' }}>
              <Title level={5}>Equipment Specification Summary</Title>
              <Text type="secondary">Overview of all equipment specifications and their default thresholds</Text>
              
              <div style={{ marginTop: '16px' }}>
                {equipmentSpecs.length > 0 ? (
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '12px' }}>
                    {equipmentSpecs.map(spec => (
                      <div key={spec.id} style={{ 
                        border: '1px solid #d9d9d9', 
                        borderRadius: '6px', 
                        padding: '12px',
                        backgroundColor: '#fafafa'
                      }}>
                        <div style={{ marginBottom: '8px' }}>
                          <Text strong style={{ textTransform: 'capitalize' }}>
                            {spec.equipment_type} - {spec.name}
                          </Text>
                          <div style={{ marginTop: '4px' }}>
                            {spec.color && <Tag color="blue" size="small">{spec.color}</Tag>}
                            {spec.size && <Tag color="green" size="small">{spec.size}</Tag>}
                            {spec.grade && <Tag color="orange" size="small">{spec.grade}</Tag>}
                          </div>
                        </div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <Text type="secondary" style={{ fontSize: '12px' }}>Default Threshold:</Text>
                          <Text strong style={{ color: '#1890ff' }}>{spec.default_threshold} units</Text>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div style={{ textAlign: 'center', padding: '20px' }}>
                    <Text type="secondary">No equipment specifications found. Add some in the Equipment Management tab.</Text>
                  </div>
                )}
              </div>
            </div>

            <Divider />
            
            <div style={{ marginBottom: '24px' }}>
              <Title level={5}>Alert Settings</Title>
              <Text type="secondary">Configure alert thresholds and notifications</Text>
              
              <div style={{ marginTop: '16px' }}>
                <div style={{ marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '12px' }}>
                  <Text style={{ width: '200px' }}>High Priority Multiplier:</Text>
                  <InputNumber
                    min={1}
                    max={5}
                    step={0.1}
                    defaultValue={1.5}
                    style={{ width: '120px' }}
                  />
                  <Text type="secondary">(e.g., 1.5 = 150% of threshold)</Text>
                </div>
                
                <div style={{ marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '12px' }}>
                  <Text style={{ width: '200px' }}>Alert Check Frequency:</Text>
                  <Select defaultValue="daily" style={{ width: '120px' }}>
                    <Option value="hourly">Hourly</Option>
                    <Option value="daily">Daily</Option>
                    <Option value="weekly">Weekly</Option>
                  </Select>
                </div>
              </div>
            </div>
          </Card>
        </TabPane>
        
        <TabPane tab="Equipment Management" key="equipment">
          <EquipmentManagement />
        </TabPane>
        
        <TabPane tab="Company Branding" key="branding">
          <Card>
            <div style={{ marginBottom: '24px' }}>
              <Title level={4}>
                <SettingOutlined style={{ marginRight: '8px' }} />
                Company Logo
              </Title>
              <Text type="secondary">Upload your company logo to customize the system appearance</Text>
            </div>
            
            <div style={{ marginBottom: '24px' }}>
              <Text strong style={{ display: 'block', marginBottom: '12px' }}>Current Logo:</Text>
              <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginBottom: '16px' }}>
                {companyLogo ? (
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <Avatar 
                      size={64} 
                      src={companyLogo} 
                      style={{ border: '1px solid #d9d9d9' }}
                    />
                    <div>
                      <Text strong>Logo Active</Text>
                      <br />
                      <Text type="secondary" style={{ fontSize: '12px' }}>
                        This logo will appear in the dashboard and driver portal
                      </Text>
                    </div>
                  </div>
                ) : (
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <Avatar 
                      size={64} 
                      icon={<UserOutlined />} 
                      style={{ backgroundColor: '#f5f5f5', color: '#999' }}
                    />
                    <div>
                      <Text type="secondary">No logo uploaded</Text>
                      <br />
                      <Text type="secondary" style={{ fontSize: '12px' }}>
                        Upload a logo to customize the system
                      </Text>
                    </div>
                  </div>
                )}
              </div>
            </div>
            
            <div style={{ marginBottom: '24px' }}>
              <Text strong style={{ display: 'block', marginBottom: '12px' }}>Upload New Logo:</Text>
              <Upload
                name="logo"
                accept="image/*"
                beforeUpload={handleLogoUpload}
                showUploadList={false}
                loading={logoLoading}
              >
                <Button 
                  icon={<UploadOutlined />} 
                  loading={logoLoading}
                  style={{ marginRight: '8px' }}
                >
                  {logoLoading ? 'Uploading...' : 'Choose Logo File'}
                </Button>
              </Upload>
              <Text type="secondary" style={{ display: 'block', marginTop: '8px', fontSize: '12px' }}>
                Supported formats: JPG, PNG, GIF. Recommended size: 200x200px or larger.
              </Text>
            </div>
            
            {companyLogo && (
              <div>
                <Button 
                  danger 
                  onClick={handleLogoRemove}
                  style={{ marginRight: '8px' }}
                >
                  Remove Logo
                </Button>
                <Text type="secondary" style={{ fontSize: '12px' }}>
                  This will remove the logo from both office dashboard and driver portal
                </Text>
              </div>
            )}
            
            <Divider />
            
            <div>
              <Title level={5}>Logo Usage</Title>
              <ul style={{ paddingLeft: '20px', color: '#666' }}>
                <li>Logo appears in the top-left corner of the office dashboard</li>
                <li>Logo is displayed in the driver portal login screen</li>
                <li>Logo is included in generated reports and exports</li>
                <li>Recommended logo size: 200x200px for best quality</li>
                <li>Supported formats: JPG, PNG, GIF, SVG</li>
              </ul>
            </div>
          </Card>
        </TabPane>
      </Tabs>

      <Modal
        title={editingCustomer ? 'Edit Customer' : 'Add New Customer'}
        open={modalVisible}
        onCancel={() => {
          setModalVisible(false);
          form.resetFields();
        }}
        footer={null}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSaveCustomer}
        >
          <Form.Item
            name="name"
            label="Customer Name"
            rules={[{ required: true, message: 'Please enter customer name' }]}
          >
            <Input placeholder="Enter customer name" />
          </Form.Item>
          
          <Form.Item
            name="location"
            label="Location"
            rules={[{ required: true, message: 'Please enter location' }]}
          >
            <Input placeholder="Enter location" />
          </Form.Item>
          
          <Form.Item
            name="contact"
            label="Contact Person"
          >
            <Input placeholder="Enter contact person name" />
          </Form.Item>
          
          <Form.Item
            name="email"
            label="Email"
            rules={[
              { type: 'email', message: 'Please enter a valid email' }
            ]}
          >
            <Input placeholder="Enter email address" />
          </Form.Item>
          
          <Form.Item
            name="phone"
            label="Phone"
          >
            <Input placeholder="Enter phone number" />
          </Form.Item>
          
          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                {editingCustomer ? 'Update' : 'Add'} Customer
              </Button>
              <Button onClick={() => setModalVisible(false)}>
                Cancel
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

// Separate component for thresholds table
const ThresholdsTable = ({ onThresholdChange, equipmentTypes }) => {
  const [balances, setBalances] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchBalances();
  }, []);

  const fetchBalances = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE_URL}/balances`);
      setBalances(response.data);
    } catch (error) {
      console.error('Error fetching balances:', error);
    } finally {
      setLoading(false);
    }
  };

  const columns = [
    {
      title: 'Customer',
      dataIndex: 'customer_name',
      key: 'customer_name',
      render: (text) => <strong>{text}</strong>
    },
    {
      title: 'Equipment Type',
      dataIndex: 'equipment_type',
      key: 'equipment_type',
      render: (type) => <Tag color="blue">{type}</Tag>
    },
    {
      title: 'Current Threshold',
      dataIndex: 'threshold',
      key: 'threshold',
      render: (threshold, record) => (
        <InputNumber
          min={1}
          max={1000}
          value={threshold}
          onChange={(value) => onThresholdChange(record.customer_name, record.equipment_type, value)}
          style={{ width: 100 }}
        />
      )
    },
    {
      title: 'Current Balance',
      dataIndex: 'current_balance',
      key: 'current_balance',
      render: (balance, record) => (
        <span style={{ 
          color: balance > record.threshold ? '#ff4d4f' : 
                 balance < 0 ? '#ff4d4f' : '#52c41a' 
        }}>
          {balance}
        </span>
      )
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status) => {
        const colors = {
          normal: 'green',
          over_threshold: 'red',
          negative: 'orange'
        };
        return <Tag color={colors[status]}>{status.replace('_', ' ').toUpperCase()}</Tag>;
      }
    }
  ];

  return (
    <Table
      columns={columns}
      dataSource={balances}
      rowKey={(record) => `${record.customer_name}_${record.equipment_type}`}
      loading={loading}
      pagination={{ pageSize: 10 }}
      scroll={{ x: 800 }}
    />
  );
};

export default Settings;
