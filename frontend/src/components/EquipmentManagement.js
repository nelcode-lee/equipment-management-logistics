import React, { useState, useEffect } from 'react';
import { 
  Card, 
  Table, 
  Button, 
  Modal, 
  Form, 
  Input, 
  Select, 
  InputNumber, 
  Switch, 
  Tag, 
  Space, 
  message, 
  Popconfirm,
  Typography,
  Divider,
  Row,
  Col
} from 'antd';
import { 
  PlusOutlined, 
  EditOutlined, 
  DeleteOutlined, 
  SettingOutlined,
  ToolOutlined
} from '@ant-design/icons';
import axios from 'axios';

const { Option } = Select;
const { Title, Text } = Typography;

const EquipmentManagement = () => {
  const [equipmentSpecs, setEquipmentSpecs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingSpec, setEditingSpec] = useState(null);
  const [form] = Form.useForm();

  // Equipment types
  const equipmentTypes = [
    { value: 'pallet', label: 'Pallet' },
    { value: 'cage', label: 'Cage' },
    { value: 'dolly', label: 'Dolly' },
    { value: 'stillage', label: 'Stillage' },
    { value: 'other', label: 'Other' }
  ];

  // Common colors for equipment
  const commonColors = [
    'Blue', 'Red', 'Green', 'Yellow', 'White', 'Black', 'Orange', 'Purple', 'Brown', 'Grey'
  ];

  // Common sizes for different equipment types
  const commonSizes = {
    pallet: ['1200x800', '1000x600', '800x600', '600x400', 'Standard', 'Half Pallet'],
    cage: ['Standard', 'Large', 'Small', '1200x800', '1000x600'],
    dolly: ['Standard', 'Heavy Duty', 'Light Duty', '4 Wheel', '2 Wheel'],
    stillage: ['Standard', 'Large', 'Small', '1200x800', '1000x600'],
    other: ['Standard', 'Custom', 'Various']
  };

  // Common grades
  const commonGrades = [
    'A', 'B', 'C', 'Food Grade', 'Export Grade', 'Standard', 'Premium', 'Economy'
  ];

  useEffect(() => {
    fetchEquipmentSpecs();
  }, []);

  const fetchEquipmentSpecs = async () => {
    try {
      setLoading(true);
      const response = await axios.get('http://localhost:8000/equipment-specifications');
      setEquipmentSpecs(response.data);
    } catch (error) {
      console.error('Error fetching equipment specifications:', error);
      message.error('Failed to fetch equipment specifications');
    } finally {
      setLoading(false);
    }
  };

  const handleSaveSpec = async (values) => {
    try {
      if (editingSpec) {
        // Update existing spec
        await axios.put(`http://localhost:8000/equipment-specifications/${editingSpec.id}`, values);
        message.success('Equipment specification updated successfully');
      } else {
        // Create new spec
        await axios.post('http://localhost:8000/equipment-specifications', values);
        message.success('Equipment specification created successfully');
      }
      
      setModalVisible(false);
      form.resetFields();
      setEditingSpec(null);
      fetchEquipmentSpecs();
    } catch (error) {
      console.error('Error saving equipment specification:', error);
      message.error('Failed to save equipment specification');
    }
  };

  const handleEdit = (spec) => {
    setEditingSpec(spec);
    form.setFieldsValue({
      equipment_type: spec.equipment_type,
      name: spec.name,
      color: spec.color,
      size: spec.size,
      grade: spec.grade,
      description: spec.description,
      default_threshold: spec.default_threshold,
      is_active: spec.is_active
    });
    setModalVisible(true);
  };

  const handleDelete = async (specId) => {
    try {
      await axios.delete(`http://localhost:8000/equipment-specifications/${specId}`);
      message.success('Equipment specification deactivated successfully');
      fetchEquipmentSpecs();
    } catch (error) {
      console.error('Error deleting equipment specification:', error);
      message.error('Failed to delete equipment specification');
    }
  };

  const handleAddNew = () => {
    setEditingSpec(null);
    form.resetFields();
    setModalVisible(true);
  };

  const columns = [
    {
      title: 'Equipment Type',
      dataIndex: 'equipment_type',
      key: 'equipment_type',
      render: (type) => <Tag color="blue">{type.toUpperCase()}</Tag>,
      filters: equipmentTypes.map(t => ({ text: t.label, value: t.value })),
      onFilter: (value, record) => record.equipment_type === value,
    },
    {
      title: 'Name',
      dataIndex: 'name',
      key: 'name',
      render: (name, record) => (
        <div>
          <Text strong>{name}</Text>
          {record.color && (
            <div>
              <Tag color="default" size="small">{record.color}</Tag>
            </div>
          )}
        </div>
      ),
    },
    {
      title: 'Specifications',
      key: 'specifications',
      render: (_, record) => (
        <div>
          {record.size && <Tag size="small">Size: {record.size}</Tag>}
          {record.grade && <Tag size="small">Grade: {record.grade}</Tag>}
        </div>
      ),
    },
    {
      title: 'Threshold',
      dataIndex: 'default_threshold',
      key: 'default_threshold',
      render: (threshold) => <Text strong>{threshold}</Text>,
      sorter: (a, b) => a.default_threshold - b.default_threshold,
    },
    {
      title: 'Status',
      dataIndex: 'is_active',
      key: 'is_active',
      render: (isActive) => (
        <Tag color={isActive ? 'green' : 'red'}>
          {isActive ? 'Active' : 'Inactive'}
        </Tag>
      ),
      filters: [
        { text: 'Active', value: true },
        { text: 'Inactive', value: false },
      ],
      onFilter: (value, record) => record.is_active === value,
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
            onClick={() => handleEdit(record)}
          >
            Edit
          </Button>
          <Popconfirm
            title="Are you sure you want to deactivate this equipment specification?"
            onConfirm={() => handleDelete(record.id)}
            okText="Yes"
            cancelText="No"
          >
            <Button
              danger
              size="small"
              icon={<DeleteOutlined />}
            >
              Deactivate
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <Card>
        <div style={{ marginBottom: '24px' }}>
          <Title level={4}>
            <ToolOutlined style={{ marginRight: '8px' }} />
            Equipment Specifications
          </Title>
          <Text type="secondary">
            Manage detailed equipment specifications including colors, sizes, and grades
          </Text>
        </div>

        <div style={{ marginBottom: '16px' }}>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={handleAddNew}
          >
            Add Equipment Specification
          </Button>
        </div>

        <Table
          columns={columns}
          dataSource={equipmentSpecs}
          rowKey="id"
          loading={loading}
          pagination={{ pageSize: 10 }}
          scroll={{ x: 800 }}
        />
      </Card>

      <Modal
        title={editingSpec ? 'Edit Equipment Specification' : 'Add Equipment Specification'}
        open={modalVisible}
        onCancel={() => {
          setModalVisible(false);
          form.resetFields();
          setEditingSpec(null);
        }}
        footer={null}
        width={600}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSaveSpec}
        >
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="equipment_type"
                label="Equipment Type"
                rules={[{ required: true, message: 'Please select equipment type' }]}
              >
                <Select placeholder="Select equipment type">
                  {equipmentTypes.map(type => (
                    <Option key={type.value} value={type.value}>
                      {type.label}
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="name"
                label="Equipment Name"
                rules={[{ required: true, message: 'Please enter equipment name' }]}
              >
                <Input placeholder="e.g., Euro Pallet, Blue Cage" />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={8}>
              <Form.Item
                name="color"
                label="Color"
              >
                <Select placeholder="Select color" allowClear>
                  {commonColors.map(color => (
                    <Option key={color} value={color}>
                      {color}
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                name="size"
                label="Size"
              >
                <Select placeholder="Select size" allowClear>
                  {Object.keys(commonSizes).map(type => (
                    <Option key={type} value={type} disabled>
                      {type.toUpperCase()}
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                name="grade"
                label="Grade"
              >
                <Select placeholder="Select grade" allowClear>
                  {commonGrades.map(grade => (
                    <Option key={grade} value={grade}>
                      {grade}
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Form.Item
            name="description"
            label="Description"
          >
            <Input.TextArea 
              placeholder="Additional details about this equipment specification"
              rows={3}
            />
          </Form.Item>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="default_threshold"
                label="Default Threshold"
                rules={[{ required: true, message: 'Please enter default threshold' }]}
              >
                <InputNumber
                  min={1}
                  max={1000}
                  placeholder="Default threshold"
                  style={{ width: '100%' }}
                />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="is_active"
                label="Active"
                valuePropName="checked"
              >
                <Switch />
              </Form.Item>
            </Col>
          </Row>

          <Divider />

          <div style={{ textAlign: 'right' }}>
            <Space>
              <Button onClick={() => setModalVisible(false)}>
                Cancel
              </Button>
              <Button type="primary" htmlType="submit">
                {editingSpec ? 'Update' : 'Create'} Specification
              </Button>
            </Space>
          </div>
        </Form>
      </Modal>
    </div>
  );
};

export default EquipmentManagement;
