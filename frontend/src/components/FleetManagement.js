import React, { useState, useEffect } from 'react';
import { Card, Table, Tag, Button, Modal, Form, Input, Select, message, Space, DatePicker, InputNumber, Tabs, Popconfirm } from 'antd';
import { CarOutlined, UserOutlined, PlusOutlined, EditOutlined, DeleteOutlined, WarningOutlined } from '@ant-design/icons';
import axios from 'axios';
import API_BASE_URL from '../config';
import dayjs from 'dayjs';

const { Option } = Select;
const { TabPane } = Tabs;

const FleetManagement = () => {
  // Drivers state
  const [drivers, setDrivers] = useState([]);
  const [driversLoading, setDriversLoading] = useState(false);
  const [driverModalVisible, setDriverModalVisible] = useState(false);
  const [editingDriver, setEditingDriver] = useState(null);
  const [driverForm] = Form.useForm();

  // Vehicles state
  const [vehicles, setVehicles] = useState([]);
  const [vehiclesLoading, setVehiclesLoading] = useState(false);
  const [vehicleModalVisible, setVehicleModalVisible] = useState(false);
  const [editingVehicle, setEditingVehicle] = useState(null);
  const [vehicleForm] = Form.useForm();

  // ==================== DRIVERS FUNCTIONS ====================

  const fetchDrivers = async () => {
    setDriversLoading(true);
    try {
      const response = await axios.get(`${API_BASE_URL}/drivers`);
      setDrivers(response.data);
    } catch (error) {
      console.error('Error fetching drivers:', error);
      message.error('Failed to load drivers');
    } finally {
      setDriversLoading(false);
    }
  };

  const createDriver = async (values) => {
    try {
      const driverData = {
        driver_name: values.driver_name,
        employee_id: values.employee_id,
        email: values.email,
        phone: values.phone,
        license_number: values.license_number,
        license_expiry: values.license_expiry ? values.license_expiry.toISOString() : null,
        status: values.status || 'active',
        assigned_vehicle_id: values.assigned_vehicle_id,
        notes: values.notes
      };

      await axios.post(`${API_BASE_URL}/drivers`, driverData);
      message.success('Driver created successfully');
      setDriverModalVisible(false);
      driverForm.resetFields();
      fetchDrivers();
    } catch (error) {
      console.error('Error creating driver:', error);
      message.error(error.response?.data?.detail || 'Failed to create driver');
    }
  };

  const updateDriver = async (values) => {
    try {
      const driverData = {
        driver_name: values.driver_name,
        employee_id: values.employee_id,
        email: values.email,
        phone: values.phone,
        license_number: values.license_number,
        license_expiry: values.license_expiry ? values.license_expiry.toISOString() : null,
        status: values.status,
        assigned_vehicle_id: values.assigned_vehicle_id,
        notes: values.notes
      };

      await axios.put(`http://localhost:8000/drivers/${editingDriver.id}`, driverData);
      message.success('Driver updated successfully');
      setDriverModalVisible(false);
      setEditingDriver(null);
      driverForm.resetFields();
      fetchDrivers();
    } catch (error) {
      console.error('Error updating driver:', error);
      message.error(error.response?.data?.detail || 'Failed to update driver');
    }
  };

  const deleteDriver = async (driverId) => {
    try {
      await axios.delete(`http://localhost:8000/drivers/${driverId}`);
      message.success('Driver deleted successfully');
      fetchDrivers();
    } catch (error) {
      console.error('Error deleting driver:', error);
      message.error('Failed to delete driver');
    }
  };

  const handleEditDriver = (driver) => {
    setEditingDriver(driver);
    driverForm.setFieldsValue({
      driver_name: driver.driver_name,
      employee_id: driver.employee_id,
      email: driver.email,
      phone: driver.phone,
      license_number: driver.license_number,
      license_expiry: driver.license_expiry ? dayjs(driver.license_expiry) : null,
      status: driver.status,
      assigned_vehicle_id: driver.assigned_vehicle_id,
      notes: driver.notes
    });
    setDriverModalVisible(true);
  };

  // ==================== VEHICLES FUNCTIONS ====================

  const fetchVehicles = async () => {
    setVehiclesLoading(true);
    try {
      const response = await axios.get(`${API_BASE_URL}/vehicles`);
      setVehicles(response.data);
    } catch (error) {
      console.error('Error fetching vehicles:', error);
      message.error('Failed to load vehicles');
    } finally {
      setVehiclesLoading(false);
    }
  };

  const createVehicle = async (values) => {
    try {
      const vehicleData = {
        fleet_number: values.fleet_number,
        registration: values.registration,
        make: values.make,
        model: values.model,
        year: values.year,
        vehicle_type: values.vehicle_type,
        capacity: values.capacity,
        status: values.status || 'available',
        mot_expiry: values.mot_expiry ? values.mot_expiry.toISOString() : null,
        insurance_expiry: values.insurance_expiry ? values.insurance_expiry.toISOString() : null,
        last_service_date: values.last_service_date ? values.last_service_date.toISOString() : null,
        next_service_due: values.next_service_due ? values.next_service_due.toISOString() : null,
        mileage: values.mileage,
        notes: values.notes
      };

      await axios.post(`${API_BASE_URL}/vehicles`, vehicleData);
      message.success('Vehicle created successfully');
      setVehicleModalVisible(false);
      vehicleForm.resetFields();
      fetchVehicles();
    } catch (error) {
      console.error('Error creating vehicle:', error);
      message.error(error.response?.data?.detail || 'Failed to create vehicle');
    }
  };

  const updateVehicle = async (values) => {
    try {
      const vehicleData = {
        fleet_number: values.fleet_number,
        registration: values.registration,
        make: values.make,
        model: values.model,
        year: values.year,
        vehicle_type: values.vehicle_type,
        capacity: values.capacity,
        status: values.status,
        mot_expiry: values.mot_expiry ? values.mot_expiry.toISOString() : null,
        insurance_expiry: values.insurance_expiry ? values.insurance_expiry.toISOString() : null,
        last_service_date: values.last_service_date ? values.last_service_date.toISOString() : null,
        next_service_due: values.next_service_due ? values.next_service_due.toISOString() : null,
        mileage: values.mileage,
        notes: values.notes
      };

      await axios.put(`http://localhost:8000/vehicles/${editingVehicle.id}`, vehicleData);
      message.success('Vehicle updated successfully');
      setVehicleModalVisible(false);
      setEditingVehicle(null);
      vehicleForm.resetFields();
      fetchVehicles();
    } catch (error) {
      console.error('Error updating vehicle:', error);
      message.error(error.response?.data?.detail || 'Failed to update vehicle');
    }
  };

  const deleteVehicle = async (vehicleId) => {
    try {
      await axios.delete(`http://localhost:8000/vehicles/${vehicleId}`);
      message.success('Vehicle deleted successfully');
      fetchVehicles();
    } catch (error) {
      console.error('Error deleting vehicle:', error);
      message.error('Failed to delete vehicle');
    }
  };

  const handleEditVehicle = (vehicle) => {
    setEditingVehicle(vehicle);
    vehicleForm.setFieldsValue({
      fleet_number: vehicle.fleet_number,
      registration: vehicle.registration,
      make: vehicle.make,
      model: vehicle.model,
      year: vehicle.year,
      vehicle_type: vehicle.vehicle_type,
      capacity: vehicle.capacity,
      status: vehicle.status,
      mot_expiry: vehicle.mot_expiry ? dayjs(vehicle.mot_expiry) : null,
      insurance_expiry: vehicle.insurance_expiry ? dayjs(vehicle.insurance_expiry) : null,
      last_service_date: vehicle.last_service_date ? dayjs(vehicle.last_service_date) : null,
      next_service_due: vehicle.next_service_due ? dayjs(vehicle.next_service_due) : null,
      mileage: vehicle.mileage,
      notes: vehicle.notes
    });
    setVehicleModalVisible(true);
  };

  useEffect(() => {
    fetchDrivers();
    fetchVehicles();
  }, []);

  // Check for expiring documents
  const getExpiryWarnings = () => {
    const warnings = [];
    const now = dayjs();
    const thirtyDaysFromNow = now.add(30, 'day');

    // Check driver licenses
    drivers.forEach(driver => {
      if (driver.license_expiry && driver.is_active) {
        const expiry = dayjs(driver.license_expiry);
        if (expiry.isBefore(now)) {
          warnings.push({ type: 'error', message: `${driver.driver_name}'s license has expired!` });
        } else if (expiry.isBefore(thirtyDaysFromNow)) {
          warnings.push({ type: 'warning', message: `${driver.driver_name}'s license expires soon (${expiry.format('DD/MM/YYYY')})` });
        }
      }
    });

    // Check vehicle MOT and insurance
    vehicles.forEach(vehicle => {
      if (vehicle.mot_expiry && vehicle.is_active) {
        const expiry = dayjs(vehicle.mot_expiry);
        if (expiry.isBefore(now)) {
          warnings.push({ type: 'error', message: `Vehicle ${vehicle.fleet_number} MOT has expired!` });
        } else if (expiry.isBefore(thirtyDaysFromNow)) {
          warnings.push({ type: 'warning', message: `Vehicle ${vehicle.fleet_number} MOT expires soon (${expiry.format('DD/MM/YYYY')})` });
        }
      }
      if (vehicle.insurance_expiry && vehicle.is_active) {
        const expiry = dayjs(vehicle.insurance_expiry);
        if (expiry.isBefore(now)) {
          warnings.push({ type: 'error', message: `Vehicle ${vehicle.fleet_number} insurance has expired!` });
        } else if (expiry.isBefore(thirtyDaysFromNow)) {
          warnings.push({ type: 'warning', message: `Vehicle ${vehicle.fleet_number} insurance expires soon (${expiry.format('DD/MM/YYYY')})` });
        }
      }
    });

    return warnings;
  };

  const warnings = getExpiryWarnings();

  // ==================== DRIVERS TABLE COLUMNS ====================

  const driverColumns = [
    {
      title: 'Driver Name',
      dataIndex: 'driver_name',
      key: 'driver_name',
      sorter: (a, b) => a.driver_name.localeCompare(b.driver_name),
    },
    {
      title: 'Employee ID',
      dataIndex: 'employee_id',
      key: 'employee_id',
      render: (id) => id || '-'
    },
    {
      title: 'Contact',
      key: 'contact',
      render: (_, record) => (
        <div>
          {record.phone && <div>📞 {record.phone}</div>}
          {record.email && <div>✉️ {record.email}</div>}
        </div>
      )
    },
    {
      title: 'License',
      key: 'license',
      render: (_, record) => {
        if (!record.license_number) return '-';
        const expiry = record.license_expiry ? dayjs(record.license_expiry) : null;
        const isExpired = expiry && expiry.isBefore(dayjs());
        const expiringSoon = expiry && expiry.isBefore(dayjs().add(30, 'day'));
        
        return (
          <div>
            <div>{record.license_number}</div>
            {expiry && (
              <Tag color={isExpired ? 'red' : expiringSoon ? 'orange' : 'green'}>
                Exp: {expiry.format('DD/MM/YYYY')}
              </Tag>
            )}
          </div>
        );
      }
    },
    {
      title: 'Assigned Vehicle',
      dataIndex: 'assigned_vehicle_id',
      key: 'assigned_vehicle_id',
      render: (vehicleId) => {
        if (!vehicleId) return '-';
        const vehicle = vehicles.find(v => v.id === vehicleId);
        return vehicle ? `${vehicle.fleet_number} (${vehicle.registration})` : vehicleId;
      }
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status) => {
        const colors = {
          active: 'green',
          inactive: 'red',
          on_leave: 'orange'
        };
        return <Tag color={colors[status] || 'default'}>{status.toUpperCase()}</Tag>;
      }
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_, record) => (
        <Space>
          <Button 
            type="link" 
            icon={<EditOutlined />}
            onClick={() => handleEditDriver(record)}
          >
            Edit
          </Button>
          <Popconfirm
            title="Are you sure you want to delete this driver?"
            onConfirm={() => deleteDriver(record.id)}
            okText="Yes"
            cancelText="No"
          >
            <Button type="link" danger icon={<DeleteOutlined />}>
              Delete
            </Button>
          </Popconfirm>
        </Space>
      )
    }
  ];

  // ==================== VEHICLES TABLE COLUMNS ====================

  const vehicleColumns = [
    {
      title: 'Fleet Number',
      dataIndex: 'fleet_number',
      key: 'fleet_number',
      sorter: (a, b) => a.fleet_number.localeCompare(b.fleet_number),
    },
    {
      title: 'Registration',
      dataIndex: 'registration',
      key: 'registration',
    },
    {
      title: 'Vehicle',
      key: 'vehicle',
      render: (_, record) => (
        <div>
          <div><strong>{record.make} {record.model}</strong></div>
          {record.year && <div style={{ fontSize: '12px', color: '#888' }}>{record.year}</div>}
        </div>
      )
    },
    {
      title: 'Type / Capacity',
      key: 'type_capacity',
      render: (_, record) => (
        <div>
          {record.vehicle_type && <div>{record.vehicle_type}</div>}
          {record.capacity && <div style={{ fontSize: '12px', color: '#888' }}>{record.capacity}</div>}
        </div>
      )
    },
    {
      title: 'MOT',
      dataIndex: 'mot_expiry',
      key: 'mot_expiry',
      render: (date) => {
        if (!date) return '-';
        const expiry = dayjs(date);
        const isExpired = expiry.isBefore(dayjs());
        const expiringSoon = expiry.isBefore(dayjs().add(30, 'day'));
        
        return (
          <Tag color={isExpired ? 'red' : expiringSoon ? 'orange' : 'green'}>
            {expiry.format('DD/MM/YYYY')}
          </Tag>
        );
      }
    },
    {
      title: 'Insurance',
      dataIndex: 'insurance_expiry',
      key: 'insurance_expiry',
      render: (date) => {
        if (!date) return '-';
        const expiry = dayjs(date);
        const isExpired = expiry.isBefore(dayjs());
        const expiringSoon = expiry.isBefore(dayjs().add(30, 'day'));
        
        return (
          <Tag color={isExpired ? 'red' : expiringSoon ? 'orange' : 'green'}>
            {expiry.format('DD/MM/YYYY')}
          </Tag>
        );
      }
    },
    {
      title: 'Mileage',
      dataIndex: 'mileage',
      key: 'mileage',
      render: (mileage) => mileage ? `${mileage.toLocaleString()} miles` : '-'
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status) => {
        const colors = {
          available: 'green',
          in_use: 'blue',
          maintenance: 'orange',
          out_of_service: 'red'
        };
        return <Tag color={colors[status] || 'default'}>{status.toUpperCase().replace('_', ' ')}</Tag>;
      }
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_, record) => (
        <Space>
          <Button 
            type="link" 
            icon={<EditOutlined />}
            onClick={() => handleEditVehicle(record)}
          >
            Edit
          </Button>
          <Popconfirm
            title="Are you sure you want to delete this vehicle?"
            onConfirm={() => deleteVehicle(record.id)}
            okText="Yes"
            cancelText="No"
          >
            <Button type="link" danger icon={<DeleteOutlined />}>
              Delete
            </Button>
          </Popconfirm>
        </Space>
      )
    }
  ];

  return (
    <div style={{ padding: '24px' }}>
      <h1 style={{ marginBottom: '24px' }}>
        <CarOutlined /> Fleet Management
      </h1>

      {/* Warnings */}
      {warnings.length > 0 && (
        <Card style={{ marginBottom: '24px', borderColor: '#ff4d4f' }}>
          <Space direction="vertical" style={{ width: '100%' }}>
            {warnings.map((warning, index) => (
              <div key={index} style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <WarningOutlined style={{ color: warning.type === 'error' ? '#ff4d4f' : '#faad14', fontSize: '16px' }} />
                <span style={{ color: warning.type === 'error' ? '#ff4d4f' : '#faad14' }}>
                  {warning.message}
                </span>
              </div>
            ))}
          </Space>
        </Card>
      )}

      <Tabs defaultActiveKey="drivers">
        {/* DRIVERS TAB */}
        <TabPane 
          tab={
            <span>
              <UserOutlined />
              Drivers ({drivers.filter(d => d.is_active).length})
            </span>
          } 
          key="drivers"
        >
          <Card>
            <div style={{ marginBottom: '16px', display: 'flex', justifyContent: 'space-between' }}>
              <h2>Drivers</h2>
              <Button 
                type="primary" 
                icon={<PlusOutlined />}
                onClick={() => {
                  setEditingDriver(null);
                  driverForm.resetFields();
                  setDriverModalVisible(true);
                }}
              >
                Add New Driver
              </Button>
            </div>
            
            <Table 
              columns={driverColumns}
              dataSource={drivers.filter(d => d.is_active)}
              rowKey="id"
              loading={driversLoading}
              pagination={{ pageSize: 10 }}
            />
          </Card>
        </TabPane>

        {/* VEHICLES TAB */}
        <TabPane 
          tab={
            <span>
              <CarOutlined />
              Vehicles ({vehicles.filter(v => v.is_active).length})
            </span>
          } 
          key="vehicles"
        >
          <Card>
            <div style={{ marginBottom: '16px', display: 'flex', justifyContent: 'space-between' }}>
              <h2>Vehicles</h2>
              <Button 
                type="primary" 
                icon={<PlusOutlined />}
                onClick={() => {
                  setEditingVehicle(null);
                  vehicleForm.resetFields();
                  setVehicleModalVisible(true);
                }}
              >
                Add New Vehicle
              </Button>
            </div>
            
            <Table 
              columns={vehicleColumns}
              dataSource={vehicles.filter(v => v.is_active)}
              rowKey="id"
              loading={vehiclesLoading}
              pagination={{ pageSize: 10 }}
            />
          </Card>
        </TabPane>
      </Tabs>

      {/* Driver Modal */}
      <Modal
        title={editingDriver ? 'Edit Driver' : 'Add New Driver'}
        open={driverModalVisible}
        onCancel={() => {
          setDriverModalVisible(false);
          setEditingDriver(null);
          driverForm.resetFields();
        }}
        footer={null}
        width={700}
      >
        <Form
          form={driverForm}
          layout="vertical"
          onFinish={editingDriver ? updateDriver : createDriver}
        >
          <Form.Item
            name="driver_name"
            label="Driver Name"
            rules={[{ required: true, message: 'Please enter driver name' }]}
          >
            <Input placeholder="Full name" />
          </Form.Item>

          <Form.Item
            name="employee_id"
            label="Employee ID"
          >
            <Input placeholder="Employee ID (optional)" />
          </Form.Item>

          <Form.Item
            name="email"
            label="Email"
            rules={[{ type: 'email', message: 'Please enter a valid email' }]}
          >
            <Input placeholder="email@example.com" />
          </Form.Item>

          <Form.Item
            name="phone"
            label="Phone Number"
          >
            <Input placeholder="Phone number" />
          </Form.Item>

          <Form.Item
            name="license_number"
            label="License Number"
          >
            <Input placeholder="Driving license number" />
          </Form.Item>

          <Form.Item
            name="license_expiry"
            label="License Expiry Date"
          >
            <DatePicker style={{ width: '100%' }} format="DD/MM/YYYY" />
          </Form.Item>

          <Form.Item
            name="status"
            label="Status"
            rules={[{ required: true, message: 'Please select status' }]}
            initialValue="active"
          >
            <Select>
              <Option value="active">Active</Option>
              <Option value="inactive">Inactive</Option>
              <Option value="on_leave">On Leave</Option>
            </Select>
          </Form.Item>

          <Form.Item
            name="assigned_vehicle_id"
            label="Assigned Vehicle"
          >
            <Select placeholder="Select vehicle (optional)" allowClear showSearch optionFilterProp="children">
              {vehicles.filter(v => v.is_active).map(vehicle => (
                <Option key={vehicle.id} value={vehicle.id}>
                  {vehicle.fleet_number} - {vehicle.registration} ({vehicle.make} {vehicle.model})
                </Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item
            name="notes"
            label="Notes"
          >
            <Input.TextArea rows={2} placeholder="Additional notes..." />
          </Form.Item>

          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                {editingDriver ? 'Update Driver' : 'Create Driver'}
              </Button>
              <Button onClick={() => {
                setDriverModalVisible(false);
                setEditingDriver(null);
                driverForm.resetFields();
              }}>
                Cancel
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      {/* Vehicle Modal */}
      <Modal
        title={editingVehicle ? 'Edit Vehicle' : 'Add New Vehicle'}
        open={vehicleModalVisible}
        onCancel={() => {
          setVehicleModalVisible(false);
          setEditingVehicle(null);
          vehicleForm.resetFields();
        }}
        footer={null}
        width={800}
      >
        <Form
          form={vehicleForm}
          layout="vertical"
          onFinish={editingVehicle ? updateVehicle : createVehicle}
        >
          <Form.Item
            name="fleet_number"
            label="Fleet Number"
            rules={[{ required: true, message: 'Please enter fleet number' }]}
          >
            <Input placeholder="e.g., VAN-001" />
          </Form.Item>

          <Form.Item
            name="registration"
            label="Registration"
            rules={[{ required: true, message: 'Please enter registration' }]}
          >
            <Input placeholder="e.g., AB12 CDE" />
          </Form.Item>

          <Space style={{ width: '100%' }} size="large">
            <Form.Item
              name="make"
              label="Make"
              style={{ width: '200px' }}
            >
              <Input placeholder="e.g., Mercedes" />
            </Form.Item>

            <Form.Item
              name="model"
              label="Model"
              style={{ width: '200px' }}
            >
              <Input placeholder="e.g., Sprinter" />
            </Form.Item>

            <Form.Item
              name="year"
              label="Year"
              style={{ width: '120px' }}
            >
              <InputNumber min={1990} max={2030} style={{ width: '100%' }} placeholder="2020" />
            </Form.Item>
          </Space>

          <Space style={{ width: '100%' }} size="large">
            <Form.Item
              name="vehicle_type"
              label="Vehicle Type"
              style={{ width: '200px' }}
            >
              <Select placeholder="Select type">
                <Option value="Van">Van</Option>
                <Option value="Truck">Truck</Option>
                <Option value="Lorry">Lorry</Option>
                <Option value="Flatbed">Flatbed</Option>
                <Option value="Box Truck">Box Truck</Option>
              </Select>
            </Form.Item>

            <Form.Item
              name="capacity"
              label="Capacity"
              style={{ width: '200px' }}
            >
              <Input placeholder="e.g., 3.5 tonne" />
            </Form.Item>

            <Form.Item
              name="status"
              label="Status"
              rules={[{ required: true, message: 'Please select status' }]}
              initialValue="available"
              style={{ width: '200px' }}
            >
              <Select>
                <Option value="available">Available</Option>
                <Option value="in_use">In Use</Option>
                <Option value="maintenance">Maintenance</Option>
                <Option value="out_of_service">Out of Service</Option>
              </Select>
            </Form.Item>
          </Space>

          <Space style={{ width: '100%' }} size="large">
            <Form.Item
              name="mot_expiry"
              label="MOT Expiry"
              style={{ width: '200px' }}
            >
              <DatePicker style={{ width: '100%' }} format="DD/MM/YYYY" />
            </Form.Item>

            <Form.Item
              name="insurance_expiry"
              label="Insurance Expiry"
              style={{ width: '200px' }}
            >
              <DatePicker style={{ width: '100%' }} format="DD/MM/YYYY" />
            </Form.Item>
          </Space>

          <Space style={{ width: '100%' }} size="large">
            <Form.Item
              name="last_service_date"
              label="Last Service Date"
              style={{ width: '200px' }}
            >
              <DatePicker style={{ width: '100%' }} format="DD/MM/YYYY" />
            </Form.Item>

            <Form.Item
              name="next_service_due"
              label="Next Service Due"
              style={{ width: '200px' }}
            >
              <DatePicker style={{ width: '100%' }} format="DD/MM/YYYY" />
            </Form.Item>

            <Form.Item
              name="mileage"
              label="Current Mileage"
              style={{ width: '200px' }}
            >
              <InputNumber min={0} style={{ width: '100%' }} placeholder="Miles" />
            </Form.Item>
          </Space>

          <Form.Item
            name="notes"
            label="Notes"
          >
            <Input.TextArea rows={2} placeholder="Additional notes..." />
          </Form.Item>

          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                {editingVehicle ? 'Update Vehicle' : 'Create Vehicle'}
              </Button>
              <Button onClick={() => {
                setVehicleModalVisible(false);
                setEditingVehicle(null);
                vehicleForm.resetFields();
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

export default FleetManagement;
