import React, { useState, useEffect } from 'react';
import { Card, Button, message, Alert, List, Tag, Modal, Select, Input, Typography, Space, Divider } from 'antd';
import { 
  CameraOutlined, 
  TruckOutlined, 
  CheckCircleOutlined, 
  ExclamationCircleOutlined,
  UserOutlined,
  LogoutOutlined,
  ReloadOutlined,
  FileTextOutlined
} from '@ant-design/icons';
import axios from 'axios';
import API_BASE_URL from '../config';

const { Title, Text } = Typography;
const { Option } = Select;

const DriverApp = () => {
  const [currentView, setCurrentView] = useState('instructions'); // 'instructions', 'photo', 'profile'
  const [driverName, setDriverName] = useState('');
  const [instructions, setInstructions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedInstruction, setSelectedInstruction] = useState(null);
  const [modalVisible, setModalVisible] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [companyLogo, setCompanyLogo] = useState(null);

  // Check if we're on mobile
  const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);

  useEffect(() => {
    // Check if driver is already logged in (from localStorage)
    const savedDriver = localStorage.getItem('driverName');
    if (savedDriver) {
      setDriverName(savedDriver);
      setIsLoggedIn(true);
      fetchDriverInstructions();
    }
    fetchCompanyLogo();
  }, []);

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

  const handleLogin = () => {
    if (!driverName.trim()) {
      message.error('Please enter your name');
      return;
    }
    localStorage.setItem('driverName', driverName);
    setIsLoggedIn(true);
    fetchDriverInstructions();
    message.success(`Welcome, ${driverName}!`);
  };

  const handleLogout = () => {
    localStorage.removeItem('driverName');
    setDriverName('');
    setIsLoggedIn(false);
    setInstructions([]);
    setCurrentView('instructions');
    message.info('Logged out successfully');
  };

  const fetchDriverInstructions = async () => {
    if (!driverName) return;
    
    setLoading(true);
    try {
      const response = await axios.get(`${API_BASE_URL}/driver-instructions?driver_name=${encodeURIComponent(driverName)}&status=assigned`);
      setInstructions(response.data);
    } catch (error) {
      console.error('Error fetching instructions:', error);
      message.error('Failed to load instructions');
    } finally {
      setLoading(false);
    }
  };

  const handleComplete = (instruction) => {
    Modal.confirm({
      title: 'Mark Collection Complete',
      content: `Confirm that you have successfully collected ${instruction.excess} ${instruction.equipment_type}(s) from ${instruction.customer_name}?`,
      onOk() {
        setInstructions(prev => 
          prev.map(i => i.id === instruction.id ? { ...i, status: 'completed' } : i)
        );
        message.success('Collection marked as complete!');
      }
    });
  };

  const handleUnableToCollect = (instruction) => {
    setSelectedInstruction(instruction);
    setModalVisible(true);
  };

  const submitUnableReason = (reason, notes) => {
    if (!reason) {
      message.error('Please select a reason');
      return;
    }

    setInstructions(prev => 
      prev.map(i => i.id === selectedInstruction.id ? { 
        ...i, 
        status: 'unable_to_collect',
        unable_reason: reason,
        unable_notes: notes,
        unable_date: new Date().toISOString()
      } : i)
    );
    
    message.warning(`Collection marked as unable - ${reason}`);
    setModalVisible(false);
    setSelectedInstruction(null);
  };

  const getStatusColor = (status) => {
    const colors = {
      pending: 'default',
      assigned: 'processing',
      completed: 'success',
      unable_to_collect: 'warning',
      failed: 'error'
    };
    return colors[status] || 'default';
  };

  const getPriorityColor = (priority) => {
    return priority === 'high' ? 'red' : 'orange';
  };

  // Login Screen
  if (!isLoggedIn) {
    return (
      <div style={{ 
        padding: '20px', 
        maxWidth: '400px', 
        margin: '0 auto',
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center'
      }}>
        <Card style={{ textAlign: 'center' }}>
          {companyLogo ? (
            <img 
              src={`${API_BASE_URL}${companyLogo}`} 
              alt="Company Logo" 
              style={{ 
                height: '80px', 
                marginBottom: '24px',
                objectFit: 'contain'
              }} 
            />
          ) : (
            <TruckOutlined style={{ fontSize: '64px', color: '#1890ff', marginBottom: '24px' }} />
          )}
          <Title level={2}>Driver Portal</Title>
          <Text type="secondary" style={{ display: 'block', marginBottom: '32px' }}>
            Equipment Collection & Photo Upload
          </Text>
          
          <div style={{ marginBottom: '24px' }}>
            <Text strong style={{ display: 'block', marginBottom: '8px', textAlign: 'left' }}>
              Enter Your Name:
            </Text>
            <Input
              value={driverName}
              onChange={(e) => setDriverName(e.target.value)}
              placeholder="Your full name"
              size="large"
              onPressEnter={handleLogin}
              style={{ marginBottom: '16px' }}
            />
            <Button 
              type="primary" 
              size="large" 
              onClick={handleLogin}
              style={{ width: '100%' }}
            >
              Login
            </Button>
          </div>
          
          <Alert
            message="Mobile Optimized"
            description="This app is designed for mobile devices and works best on phones and tablets."
            type="info"
            showIcon
          />
        </Card>
      </div>
    );
  }

  // Main App Navigation
  const renderNavigation = () => (
    <Card style={{ marginBottom: '16px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <Text strong>Welcome, {driverName}</Text>
          <br />
          <Text type="secondary" style={{ fontSize: '12px' }}>
            {instructions.length} active collection(s)
          </Text>
        </div>
        <Button 
          icon={<LogoutOutlined />} 
          size="small" 
          onClick={handleLogout}
        >
          Logout
        </Button>
      </div>
      
      <Divider style={{ margin: '12px 0' }} />
      
      <div style={{ display: 'flex', gap: '8px' }}>
        <Button
          type={currentView === 'instructions' ? 'primary' : 'default'}
          size="small"
          icon={<TruckOutlined />}
          onClick={() => setCurrentView('instructions')}
          style={{ flex: 1 }}
        >
          Collections
        </Button>
        <Button
          type={currentView === 'photo' ? 'primary' : 'default'}
          size="small"
          icon={<CameraOutlined />}
          onClick={() => setCurrentView('photo')}
          style={{ flex: 1 }}
        >
          Photo Upload
        </Button>
        <Button
          type={currentView === 'profile' ? 'primary' : 'default'}
          size="small"
          icon={<UserOutlined />}
          onClick={() => setCurrentView('profile')}
          style={{ flex: 1 }}
        >
          Profile
        </Button>
      </div>
    </Card>
  );

  // Instructions View
  const renderInstructions = () => (
    <div>
      <Card style={{ marginBottom: '16px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Title level={4} style={{ margin: 0 }}>
            <TruckOutlined style={{ marginRight: '8px' }} />
            Collection Instructions
          </Title>
          <Button 
            icon={<ReloadOutlined />} 
            size="small" 
            onClick={fetchDriverInstructions}
            loading={loading}
          >
            Refresh
          </Button>
        </div>
      </Card>

      {loading ? (
        <Card>
          <div style={{ textAlign: 'center', padding: '40px' }}>
            <Text>Loading your collection instructions...</Text>
          </div>
        </Card>
      ) : instructions.length === 0 ? (
        <Card>
          <div style={{ textAlign: 'center', padding: '40px' }}>
            <CheckCircleOutlined style={{ fontSize: '48px', color: '#52c41a', marginBottom: '16px' }} />
            <Title level={4}>No Collection Instructions</Title>
            <Text type="secondary">You have no assigned collection tasks at the moment.</Text>
          </div>
        </Card>
      ) : (
        <List
          dataSource={instructions}
          renderItem={(instruction) => (
            <List.Item style={{ padding: '16px 0' }}>
              <Card style={{ width: '100%' }}>
                <div style={{ marginBottom: '12px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                    <Title level={5} style={{ margin: 0 }}>{instruction.customer_name}</Title>
                    <Tag color={getPriorityColor(instruction.priority)}>
                      {instruction.priority.toUpperCase()}
                    </Tag>
                  </div>
                  
                  <div style={{ marginBottom: '8px' }}>
                    <Tag color="blue">{instruction.equipment_type}</Tag>
                    <span style={{ marginLeft: '8px' }}>
                      Collect <strong>{instruction.excess}</strong> items
                    </span>
                  </div>
                  
                  <div style={{ fontSize: '14px', color: '#666', marginBottom: '12px' }}>
                    Current balance: {instruction.current_balance} | Threshold: {instruction.threshold}
                  </div>
                  
                  {instruction.notes && (
                    <Alert
                      message={instruction.notes}
                      type="info"
                      size="small"
                      style={{ marginBottom: '12px' }}
                    />
                  )}
                </div>
                
                <div style={{ display: 'flex', gap: '8px' }}>
                  <Button
                    type="primary"
                    size="small"
                    icon={<CheckCircleOutlined />}
                    onClick={() => handleComplete(instruction)}
                    style={{ flex: 1 }}
                  >
                    Mark Complete
                  </Button>
                  <Button
                    size="small"
                    icon={<ExclamationCircleOutlined />}
                    onClick={() => handleUnableToCollect(instruction)}
                    style={{ flex: 1 }}
                  >
                    Unable to Collect
                  </Button>
                </div>
              </Card>
            </List.Item>
          )}
        />
      )}
    </div>
  );

  // Photo Upload View
  const renderPhotoUpload = () => {
    const handleCameraClick = () => {
      // Create file input for camera access
      const input = document.createElement('input');
      input.type = 'file';
      input.accept = 'image/*';
      input.capture = isMobile ? 'environment' : undefined; // Use back camera on mobile
      
      input.onchange = (e) => {
        const file = e.target.files[0];
        if (file) {
          // Create preview
          const reader = new FileReader();
          reader.onload = (event) => {
            // Show preview and process
            message.success('Photo captured! Processing...');
            // Here you would call the photo upload API
            console.log('Photo file:', file);
          };
          reader.readAsDataURL(file);
        }
      };
      
      input.click();
    };

    return (
      <div>
        <Card style={{ marginBottom: '16px' }}>
          <Title level={4} style={{ margin: 0 }}>
            <CameraOutlined style={{ marginRight: '8px' }} />
            Photo Upload
          </Title>
          <Text type="secondary">
            Take photos of delivery notes to automatically extract equipment information
          </Text>
        </Card>
        
        <Card>
          <div style={{ textAlign: 'center' }}>
            <CameraOutlined style={{ fontSize: '64px', color: '#1890ff', marginBottom: '24px' }} />
            <Title level={4}>Capture Delivery Note</Title>
            <Text type="secondary" style={{ display: 'block', marginBottom: '24px' }}>
              Use your camera to photograph delivery notes, PODs, or equipment return documents
            </Text>
            
            <Button
              type="primary"
              size="large"
              icon={<CameraOutlined />}
              style={{ 
                width: '100%', 
                height: '60px',
                fontSize: '18px',
                marginBottom: '16px'
              }}
              onClick={handleCameraClick}
            >
              {isMobile ? 'Open Camera' : 'Select Photo'}
            </Button>
            
            <div style={{ marginBottom: '16px' }}>
              <Text type="secondary" style={{ fontSize: '12px' }}>
                {isMobile ? 'Camera will open automatically' : 'Click to select from gallery'}
              </Text>
            </div>
            
            <Alert
              message="Camera Access Available"
              description={
                isMobile 
                  ? "Your mobile device supports direct camera access. No app store required!"
                  : "Select photos from your device or use a mobile device for camera access."
              }
              type="success"
              showIcon
            />
            
            <Alert
              message="AI-Powered Processing"
              description="Your photos will be automatically processed to extract equipment movement data."
              type="info"
              showIcon
              style={{ marginTop: '12px' }}
            />
          </div>
        </Card>
      </div>
    );
  };

  // Profile View
  const renderProfile = () => (
    <div>
      <Card style={{ marginBottom: '16px' }}>
        <Title level={4} style={{ margin: 0 }}>
          <UserOutlined style={{ marginRight: '8px' }} />
          Driver Profile
        </Title>
      </Card>
      
      <Card>
        <div style={{ marginBottom: '16px' }}>
          <Text strong style={{ display: 'block', marginBottom: '8px' }}>Driver Name:</Text>
          <Text>{driverName}</Text>
        </div>
        
        <div style={{ marginBottom: '16px' }}>
          <Text strong style={{ display: 'block', marginBottom: '8px' }}>Active Collections:</Text>
          <Text>{instructions.length}</Text>
        </div>
        
        <div style={{ marginBottom: '16px' }}>
          <Text strong style={{ display: 'block', marginBottom: '8px' }}>Device:</Text>
          <Text>{isMobile ? 'Mobile Device' : 'Desktop/Tablet'}</Text>
        </div>
        
        <Alert
          message="Driver Portal"
          description="This is your dedicated mobile interface for equipment collection and photo upload tasks."
          type="info"
          showIcon
        />
      </Card>
    </div>
  );

  return (
    <div style={{ 
      padding: '16px', 
      maxWidth: '500px', 
      margin: '0 auto',
      minHeight: '100vh',
      backgroundColor: '#f5f5f5'
    }}>
      {renderNavigation()}
      
      {currentView === 'instructions' && renderInstructions()}
      {currentView === 'photo' && renderPhotoUpload()}
      {currentView === 'profile' && renderProfile()}

      {/* Unable to Collect Modal */}
      <Modal
        title="Unable to Collect Equipment"
        open={modalVisible}
        onCancel={() => {
          setModalVisible(false);
          setSelectedInstruction(null);
        }}
        footer={null}
      >
        {selectedInstruction && (
          <div>
            <p><strong>Customer:</strong> {selectedInstruction.customer_name}</p>
            <p><strong>Equipment:</strong> {selectedInstruction.equipment_type} x {selectedInstruction.excess}</p>
            
            <div style={{ marginTop: '16px' }}>
              <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>
                Reason for unable to collect:
              </label>
              <Select
                placeholder="Select reason"
                style={{ width: '100%', marginBottom: '16px' }}
                onChange={(value) => {
                  setSelectedInstruction(prev => ({ ...prev, tempReason: value }));
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
                <Option value="other">Other</Option>
              </Select>
              
              <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>
                Additional notes (optional):
              </label>
              <Input.TextArea
                rows={3}
                placeholder="Any additional details..."
                onChange={(e) => {
                  setSelectedInstruction(prev => ({ ...prev, tempNotes: e.target.value }));
                }}
              />
              
              <div style={{ marginTop: '16px', display: 'flex', gap: '8px' }}>
                <Button
                  type="primary"
                  onClick={() => submitUnableReason(selectedInstruction.tempReason, selectedInstruction.tempNotes)}
                  style={{ flex: 1 }}
                >
                  Submit
                </Button>
                <Button
                  onClick={() => {
                    setModalVisible(false);
                    setSelectedInstruction(null);
                  }}
                  style={{ flex: 1 }}
                >
                  Cancel
                </Button>
              </div>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default DriverApp;
