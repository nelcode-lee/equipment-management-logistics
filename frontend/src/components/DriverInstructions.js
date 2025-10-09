import React, { useState, useEffect } from 'react';
import { Card, Table, Tag, Button, Modal, Form, Input, Select, message, Alert, Space, DatePicker, InputNumber, Tabs } from 'antd';
import { ExclamationCircleOutlined, CheckCircleOutlined, TruckOutlined, PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons';
import axios from 'axios';
import API_BASE_URL from '../config';
import dayjs from 'dayjs';

const { Option } = Select;

const DriverInstructions = () => {
  const [instructions, setInstructions] = useState([]);
  const [customInstructions, setCustomInstructions] = useState([]);
  const [filteredInstructions, setFilteredInstructions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [createModalVisible, setCreateModalVisible] = useState(false);
  const [editModalVisible, setEditModalVisible] = useState(false);
  const [editingInstruction, setEditingInstruction] = useState(null);
  const [statusFilter, setStatusFilter] = useState('all');
  const [form] = Form.useForm();
  const [createForm] = Form.useForm();
  const [editForm] = Form.useForm();
  const [drivers, setDrivers] = useState([]);
  const [vehicles, setVehicles] = useState([]);

  // Fetch outstanding balances that need collection
  const fetchOutstandingBalances = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API_BASE_URL}/balances?status=over_threshold`);
      // Handle paginated response format
      const balances = response.data.data || response.data;
      
      // Convert balances to driver instructions
      const instructions = balances.map(balance => ({
        id: `${balance.customer_name}_${balance.equipment_type}`,
        customer_name: balance.customer_name,
        equipment_type: balance.equipment_type,
        current_balance: balance.current_balance,
        threshold: balance.threshold,
        excess: balance.current_balance - balance.threshold,
        priority: balance.current_balance > (balance.threshold * 1.5) ? 'high' : 'medium',
        status: 'pending',
        created_at: new Date().toISOString(),
        driver_name: null,
        delivery_date: null,
        notes: `Collect ${balance.excess} ${balance.equipment_type}(s) - Customer has ${balance.current_balance} but threshold is ${balance.threshold}`
      }));
      
      setInstructions(instructions);
      setFilteredInstructions(instructions);
    } catch (error) {
      console.error('Error fetching balances:', error);
      message.error('Failed to load outstanding balances');
    } finally {
      setLoading(false);
    }
  };

  // Filter instructions based on status
  useEffect(() => {
    if (statusFilter === 'all') {
      setFilteredInstructions(instructions);
    } else {
      setFilteredInstructions(instructions.filter(i => i.status === statusFilter));
    }
  }, [instructions, statusFilter]);

  // Fetch custom driver instructions
  const fetchCustomInstructions = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/driver-instructions`);
      setCustomInstructions(response.data);
    } catch (error) {
      console.error('Error fetching custom instructions:', error);
      message.error('Failed to load custom instructions');
    }
  };

  // Fetch drivers list
  const fetchDrivers = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/drivers?is_active=true`);
      setDrivers(response.data);
    } catch (error) {
      console.error('Error fetching drivers:', error);
    }
  };

  // Fetch vehicles list
  const fetchVehicles = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/vehicles?is_active=true`);
      setVehicles(response.data);
    } catch (error) {
      console.error('Error fetching vehicles:', error);
    }
  };

  useEffect(() => {
    fetchOutstandingBalances();
    fetchCustomInstructions();
    fetchDrivers();
    fetchVehicles();
  }, []);

  // Create new custom instruction
  const createCustomInstruction = async (values) => {
    try {
      const instructionData = {
        title: values.title,
        content: values.content,
        priority: values.priority,
        assigned_driver: values.assigned_driver,
        customer_name: values.customer_name,
        delivery_location: values.delivery_location,
        contact_phone: values.contact_phone,
        delivery_date: values.delivery_date ? values.delivery_date.format('YYYY-MM-DD HH:mm:ss') : null,
        equipment_type: values.equipment_type,
        equipment_quantity: values.equipment_quantity,
        special_instructions: values.special_instructions
      };

      const response = await axios.post(`${API_BASE_URL}/driver-instructions`, instructionData);
      message.success('Custom instruction created successfully!');
      setCreateModalVisible(false);
      createForm.resetFields();
      fetchCustomInstructions();
    } catch (error) {
      console.error('Error creating instruction:', error);
      message.error('Failed to create instruction');
    }
  };

  // Update custom instruction
  const updateCustomInstruction = async (values) => {
    try {
      const instructionData = {
        title: values.title,
        content: values.content,
        priority: values.priority,
        assigned_driver: values.assigned_driver,
        customer_name: values.customer_name,
        delivery_location: values.delivery_location,
        contact_phone: values.contact_phone,
        delivery_date: values.delivery_date ? values.delivery_date.format('YYYY-MM-DD HH:mm:ss') : null,
        equipment_type: values.equipment_type,
        equipment_quantity: values.equipment_quantity,
        special_instructions: values.special_instructions
      };

      await axios.put(`${API_BASE_URL}/driver-instructions/${editingInstruction.id}`, instructionData);
      message.success('Instruction updated successfully!');
      setEditModalVisible(false);
      setEditingInstruction(null);
      editForm.resetFields();
      fetchCustomInstructions();
    } catch (error) {
      console.error('Error updating instruction:', error);
      message.error('Failed to update instruction');
    }
  };

  // Delete custom instruction
  const deleteCustomInstruction = async (instructionId) => {
    Modal.confirm({
      title: 'Delete Instruction',
      content: 'Are you sure you want to delete this instruction?',
      onOk: async () => {
        try {
          await axios.delete(`${API_BASE_URL}/driver-instructions/${instructionId}`);
          message.success('Instruction deleted successfully!');
          fetchCustomInstructions();
        } catch (error) {
          console.error('Error deleting instruction:', error);
          message.error('Failed to delete instruction');
        }
      }
    });
  };

  // Edit instruction handler
  const handleEditInstruction = (instruction) => {
    setEditingInstruction(instruction);
    editForm.setFieldsValue({
      title: instruction.title,
      content: instruction.content,
      priority: instruction.priority,
      assigned_driver: instruction.assigned_driver,
      customer_name: instruction.customer_name,
      delivery_location: instruction.delivery_location,
      contact_phone: instruction.contact_phone,
      delivery_date: instruction.delivery_date ? dayjs(instruction.delivery_date) : null,
      equipment_type: instruction.equipment_type,
      equipment_quantity: instruction.equipment_quantity,
      special_instructions: instruction.special_instructions
    });
    setEditModalVisible(true);
  };

  // Assign instruction to driver
  const assignToDriver = async (instructionId, values) => {
    try {
      const instruction = instructions.find(i => i.id === instructionId);
      const updatedInstruction = {
        ...instruction,
        driver_name: values.driver_name,
        delivery_date: values.delivery_date,
        status: 'assigned',
        assigned_at: new Date().toISOString()
      };

      // Update instruction (in real app, this would call API)
      setInstructions(prev => 
        prev.map(i => i.id === instructionId ? updatedInstruction : i)
      );

      message.success(`Instruction assigned to ${values.driver_name}`);
      setModalVisible(false);
      form.resetFields();
    } catch (error) {
      message.error('Failed to assign instruction');
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
      title: 'Equipment',
      dataIndex: 'equipment_type',
      key: 'equipment_type',
      render: (type) => <Tag color="blue">{type}</Tag>
    },
    {
      title: 'Current Balance',
      dataIndex: 'current_balance',
      key: 'current_balance',
      render: (balance, record) => (
        <span style={{ color: balance > record.threshold ? '#ff4d4f' : '#52c41a' }}>
          {balance}
        </span>
      )
    },
    {
      title: 'Threshold',
      dataIndex: 'threshold',
      key: 'threshold'
    },
    {
      title: 'Excess',
      dataIndex: 'excess',
      key: 'excess',
      render: (excess) => (
        <Tag color={excess > 10 ? 'red' : 'orange'}>
          +{excess}
        </Tag>
      )
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
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status, record) => {
        const colors = {
          pending: 'default',
          assigned: 'processing',
          completed: 'success',
          unable_to_collect: 'warning',
          failed: 'error'
        };
        return (
          <div>
            <Tag color={colors[status]}>{status.replace('_', ' ').toUpperCase()}</Tag>
            {status === 'unable_to_collect' && record.unable_reason && (
              <div style={{ fontSize: '11px', color: '#666', marginTop: '2px' }}>
                Reason: {record.unable_reason.replace('_', ' ')}
              </div>
            )}
          </div>
        );
      }
    },
    {
      title: 'Driver',
      dataIndex: 'driver_name',
      key: 'driver_name',
      render: (driver) => driver || '-'
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_, record) => (
        <Space>
          {record.status === 'pending' && (
            <Button
              type="primary"
              size="small"
              icon={<TruckOutlined />}
              onClick={() => {
                form.setFieldsValue({ instruction_id: record.id });
                setModalVisible(true);
              }}
            >
              Assign Driver
            </Button>
          )}
          {record.status === 'assigned' && (
            <Space>
              <Button
                type="primary"
                size="small"
                onClick={() => {
                  // Mark as completed when driver uploads photo
                  setInstructions(prev => 
                    prev.map(i => i.id === record.id ? { ...i, status: 'completed' } : i)
                  );
                  message.success('Collection completed!');
                }}
              >
                Mark Complete
              </Button>
              <Button
                type="default"
                size="small"
                onClick={() => {
                  // Show reason modal for unable to collect
                  Modal.confirm({
                    title: 'Unable to Collect Equipment',
                    content: (
                      <div>
                        <p>Please select the reason why equipment could not be collected:</p>
                        <Select
                          placeholder="Select reason"
                          style={{ width: '100%', marginTop: '8px' }}
                          onChange={(value) => {
                            setInstructions(prev => 
                              prev.map(i => i.id === record.id ? { 
                                ...i, 
                                status: 'unable_to_collect',
                                unable_reason: value,
                                unable_date: new Date().toISOString()
                              } : i)
                            );
                            message.warning(`Collection marked as unable - ${value}`);
                          }}
                        >
                          <Option value="no_equipment_available">No equipment available for collection</Option>
                          <Option value="trailer_not_returning">Trailer not returning to base</Option>
                          <Option value="mot_service">MOT/Service required</Option>
                          <Option value="customer_refused">Customer refused to release equipment</Option>
                          <Option value="access_issues">Access issues (gate locked, etc.)</Option>
                          <Option value="equipment_damaged">Equipment damaged/unusable</Option>
                          <Option value="weather_conditions">Weather conditions</Option>
                          <Option value="driver_illness">Driver illness/emergency</Option>
                          <Option value="other">Other (specify in notes)</Option>
                        </Select>
                      </div>
                    ),
                    onOk() {
                      // Modal will handle the state update via onChange
                    },
                    okText: 'Confirm',
                    cancelText: 'Cancel'
                  });
                }}
              >
                Unable to Collect
              </Button>
            </Space>
          )}
          {record.status === 'unable_to_collect' && (
            <Space>
              <Button
                type="primary"
                size="small"
                onClick={() => {
                  // Reschedule the collection
                  setInstructions(prev => 
                    prev.map(i => i.id === record.id ? { 
                      ...i, 
                      status: 'pending',
                      driver_name: null,
                      delivery_date: null,
                      unable_reason: null,
                      unable_date: null
                    } : i)
                  );
                  message.info('Collection rescheduled - ready for reassignment');
                }}
              >
                Reschedule
              </Button>
              <Button
                type="default"
                size="small"
                onClick={() => {
                  // Mark as permanently failed
                  setInstructions(prev => 
                    prev.map(i => i.id === record.id ? { ...i, status: 'failed' } : i)
                  );
                  message.error('Collection marked as failed');
                }}
              >
                Mark Failed
              </Button>
            </Space>
          )}
        </Space>
      )
    }
  ];

  const getPriorityCounts = () => {
    const high = instructions.filter(i => i.priority === 'high').length;
    const medium = instructions.filter(i => i.priority === 'medium').length;
    const unable = instructions.filter(i => i.status === 'unable_to_collect').length;
    const pending = instructions.filter(i => i.status === 'pending').length;
    return { high, medium, unable, pending };
  };

  const { high, medium, unable, pending } = getPriorityCounts();

  const tabItems = [
    {
      key: 'auto-generated',
      label: `Auto-Generated (${instructions.length})`,
      children: (
        <div>
          <Space wrap style={{ marginBottom: 16 }}>
            <Alert
              message={`${high} High Priority Collections`}
              type="error"
              icon={<ExclamationCircleOutlined />}
            />
            <Alert
              message={`${medium} Medium Priority Collections`}
              type="warning"
              icon={<ExclamationCircleOutlined />}
            />
            <Alert
              message={`${unable} Unable to Collect`}
              type="warning"
              icon={<ExclamationCircleOutlined />}
            />
            <Alert
              message={`${pending} Pending Assignment`}
              type="info"
              icon={<ExclamationCircleOutlined />}
            />
          </Space>

          <Card>
            <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <h3>Outstanding Equipment Collections</h3>
              <Space>
                <Select
                  value={statusFilter}
                  onChange={setStatusFilter}
                  style={{ width: 150 }}
                >
                  <Option value="all">All Status</Option>
                  <Option value="pending">Pending</Option>
                  <Option value="assigned">Assigned</Option>
                  <Option value="completed">Completed</Option>
                  <Option value="unable_to_collect">Unable to Collect</Option>
                  <Option value="failed">Failed</Option>
                </Select>
                <Button onClick={fetchOutstandingBalances} loading={loading}>
                  Refresh
                </Button>
              </Space>
            </div>
            
            <Table
              columns={columns}
              dataSource={filteredInstructions}
              rowKey="id"
              loading={loading}
              pagination={{ pageSize: 10 }}
              scroll={{ x: 800 }}
            />
          </Card>
        </div>
      )
    },
    {
      key: 'custom',
      label: `Custom Instructions (${customInstructions.length})`,
      children: (
        <div>
          <Card>
            <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <h3>Custom Driver Instructions</h3>
              <Space>
                <Button 
                  type="primary" 
                  icon={<PlusOutlined />}
                  onClick={() => setCreateModalVisible(true)}
                >
                  Create New Instruction
                </Button>
                <Button onClick={fetchCustomInstructions} loading={loading}>
                  Refresh
                </Button>
              </Space>
            </div>
            
            <Table
              columns={[
                {
                  title: 'Title',
                  dataIndex: 'title',
                  key: 'title',
                  render: (text) => <strong>{text}</strong>
                },
                {
                  title: 'Content',
                  dataIndex: 'content',
                  key: 'content',
                  ellipsis: true
                },
                {
                  title: 'Priority',
                  dataIndex: 'priority',
                  key: 'priority',
                  render: (priority) => (
                    <Tag color={priority === 'HIGH' ? 'red' : priority === 'MEDIUM' ? 'orange' : 'green'}>
                      {priority}
                    </Tag>
                  )
                },
                {
                  title: 'Status',
                  dataIndex: 'status',
                  key: 'status',
                  render: (status) => (
                    <Tag color={status === 'pending' ? 'default' : status === 'in_progress' ? 'processing' : 'success'}>
                      {status.replace('_', ' ').toUpperCase()}
                    </Tag>
                  )
                },
                {
                  title: 'Driver',
                  dataIndex: 'assigned_driver',
                  key: 'assigned_driver',
                  render: (driver) => driver || '-'
                },
                {
                  title: 'Customer',
                  dataIndex: 'customer_name',
                  key: 'customer_name',
                  render: (customer) => customer || '-'
                },
                {
                  title: 'Created',
                  dataIndex: 'created_at',
                  key: 'created_at',
                  render: (date) => new Date(date).toLocaleDateString()
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
                        onClick={() => handleEditInstruction(record)}
                      >
                        Edit
                      </Button>
                      <Button
                        type="primary"
                        danger
                        size="small"
                        icon={<DeleteOutlined />}
                        onClick={() => deleteCustomInstruction(record.id)}
                      >
                        Delete
                      </Button>
                    </Space>
                  )
                }
              ]}
              dataSource={customInstructions}
              rowKey="id"
              loading={loading}
              pagination={{ pageSize: 10 }}
              scroll={{ x: 800 }}
            />
          </Card>
        </div>
      )
    }
  ];

  return (
    <div>
      <h2>Driver Instructions Management</h2>
      
      <Tabs defaultActiveKey="auto-generated" items={tabItems} />

      <Modal
        title="Assign Collection to Driver"
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
          onFinish={(values) => assignToDriver(values.instruction_id, values)}
        >
          <Form.Item name="instruction_id" hidden>
            <Input />
          </Form.Item>
          
          <Form.Item
            name="driver_name"
            label="Driver Name"
            rules={[{ required: true, message: 'Please select a driver' }]}
          >
            <Select placeholder="Select driver">
              <Option value="John Smith">John Smith</Option>
              <Option value="Sarah Johnson">Sarah Johnson</Option>
              <Option value="Mike Wilson">Mike Wilson</Option>
              <Option value="Lisa Brown">Lisa Brown</Option>
            </Select>
          </Form.Item>
          
          <Form.Item
            name="delivery_date"
            label="Expected Delivery Date"
            rules={[{ required: true, message: 'Please select delivery date' }]}
          >
            <Input type="date" />
          </Form.Item>
          
          <Form.Item
            name="notes"
            label="Additional Instructions"
          >
            <Input.TextArea rows={3} placeholder="Any specific instructions for the driver..." />
          </Form.Item>
          
          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                Assign Instruction
              </Button>
              <Button onClick={() => setModalVisible(false)}>
                Cancel
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      {/* Create Custom Instruction Modal */}
      <Modal
        title="Create New Driver Instruction"
        open={createModalVisible}
        onCancel={() => {
          setCreateModalVisible(false);
          createForm.resetFields();
        }}
        footer={null}
        width={800}
      >
        <Form
          form={createForm}
          layout="vertical"
          onFinish={createCustomInstruction}
        >
          <Form.Item
            name="title"
            label="Instruction Title"
            rules={[{ required: true, message: 'Please enter a title' }]}
          >
            <Input placeholder="e.g., Deliver Equipment to ABC Company" />
          </Form.Item>
          
          <Form.Item
            name="content"
            label="Instruction Content"
            rules={[{ required: true, message: 'Please enter instruction content' }]}
          >
            <Input.TextArea rows={3} placeholder="Describe what the driver needs to do..." />
          </Form.Item>
          
          <Form.Item
            name="priority"
            label="Priority"
            rules={[{ required: true, message: 'Please select priority' }]}
          >
            <Select placeholder="Select priority">
              <Option value="HIGH">HIGH</Option>
              <Option value="MEDIUM">MEDIUM</Option>
              <Option value="LOW">LOW</Option>
            </Select>
          </Form.Item>
          
          <Form.Item
            name="assigned_driver"
            label="Assigned Driver"
          >
            <Select placeholder="Select driver (optional)" showSearch optionFilterProp="children" allowClear>
              {drivers.map(driver => (
                <Option key={driver.id} value={driver.driver_name}>
                  {driver.driver_name} {driver.employee_id ? `(${driver.employee_id})` : ''}
                </Option>
              ))}
            </Select>
          </Form.Item>
          
          <Form.Item
            name="customer_name"
            label="Customer Name"
          >
            <Input placeholder="Customer name (optional)" />
          </Form.Item>
          
          <Form.Item
            name="delivery_location"
            label="Delivery Location"
          >
            <Input placeholder="Full delivery address (optional)" />
          </Form.Item>
          
          <Form.Item
            name="contact_phone"
            label="Contact Phone"
          >
            <Input placeholder="Contact number (optional)" />
          </Form.Item>
          
          <Form.Item
            name="delivery_date"
            label="Delivery Date"
          >
            <DatePicker 
              showTime 
              style={{ width: '100%' }} 
              placeholder="Select delivery date and time (optional)"
            />
          </Form.Item>
          
          <Form.Item
            name="equipment_type"
            label="Equipment Type"
          >
            <Select placeholder="Select equipment type (optional)">
              <Option value="pallet">Pallet</Option>
              <Option value="cage">Cage</Option>
              <Option value="dolly">Dolly</Option>
              <Option value="stillage">Stillage</Option>
              <Option value="container">Container</Option>
              <Option value="other">Other</Option>
            </Select>
          </Form.Item>
          
          <Form.Item
            name="equipment_quantity"
            label="Equipment Quantity"
          >
            <InputNumber 
              min={1} 
              style={{ width: '100%' }} 
              placeholder="Quantity (optional)"
            />
          </Form.Item>
          
          <Form.Item
            name="special_instructions"
            label="Special Instructions"
          >
            <Input.TextArea rows={2} placeholder="Any special notes or instructions..." />
          </Form.Item>
          
          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                Create Instruction
              </Button>
              <Button onClick={() => setCreateModalVisible(false)}>
                Cancel
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      {/* Edit Custom Instruction Modal */}
      <Modal
        title="Edit Driver Instruction"
        open={editModalVisible}
        onCancel={() => {
          setEditModalVisible(false);
          setEditingInstruction(null);
          editForm.resetFields();
        }}
        footer={null}
        width={800}
      >
        <Form
          form={editForm}
          layout="vertical"
          onFinish={updateCustomInstruction}
        >
          <Form.Item
            name="title"
            label="Instruction Title"
            rules={[{ required: true, message: 'Please enter a title' }]}
          >
            <Input placeholder="e.g., Deliver Equipment to ABC Company" />
          </Form.Item>
          
          <Form.Item
            name="content"
            label="Instruction Content"
            rules={[{ required: true, message: 'Please enter instruction content' }]}
          >
            <Input.TextArea rows={3} placeholder="Describe what the driver needs to do..." />
          </Form.Item>
          
          <Form.Item
            name="priority"
            label="Priority"
            rules={[{ required: true, message: 'Please select priority' }]}
          >
            <Select placeholder="Select priority">
              <Option value="HIGH">HIGH</Option>
              <Option value="MEDIUM">MEDIUM</Option>
              <Option value="LOW">LOW</Option>
            </Select>
          </Form.Item>
          
          <Form.Item
            name="assigned_driver"
            label="Assigned Driver"
          >
            <Select placeholder="Select driver (optional)" showSearch optionFilterProp="children" allowClear>
              {drivers.map(driver => (
                <Option key={driver.id} value={driver.driver_name}>
                  {driver.driver_name} {driver.employee_id ? `(${driver.employee_id})` : ''}
                </Option>
              ))}
            </Select>
          </Form.Item>
          
          <Form.Item
            name="customer_name"
            label="Customer Name"
          >
            <Input placeholder="Customer name (optional)" />
          </Form.Item>
          
          <Form.Item
            name="delivery_location"
            label="Delivery Location"
          >
            <Input placeholder="Full delivery address (optional)" />
          </Form.Item>
          
          <Form.Item
            name="contact_phone"
            label="Contact Phone"
          >
            <Input placeholder="Contact number (optional)" />
          </Form.Item>
          
          <Form.Item
            name="delivery_date"
            label="Delivery Date"
          >
            <DatePicker 
              showTime 
              style={{ width: '100%' }} 
              placeholder="Select delivery date and time (optional)"
            />
          </Form.Item>
          
          <Form.Item
            name="equipment_type"
            label="Equipment Type"
          >
            <Select placeholder="Select equipment type (optional)">
              <Option value="pallet">Pallet</Option>
              <Option value="cage">Cage</Option>
              <Option value="dolly">Dolly</Option>
              <Option value="stillage">Stillage</Option>
              <Option value="container">Container</Option>
              <Option value="other">Other</Option>
            </Select>
          </Form.Item>
          
          <Form.Item
            name="equipment_quantity"
            label="Equipment Quantity"
          >
            <InputNumber 
              min={1} 
              style={{ width: '100%' }} 
              placeholder="Quantity (optional)"
            />
          </Form.Item>
          
          <Form.Item
            name="special_instructions"
            label="Special Instructions"
          >
            <Input.TextArea rows={2} placeholder="Any special notes or instructions..." />
          </Form.Item>
          
          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                Update Instruction
              </Button>
              <Button onClick={() => {
                setEditModalVisible(false);
                setEditingInstruction(null);
                editForm.resetFields();
              }}>
                Cancel
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default DriverInstructions;
