import React, { useState, useEffect } from 'react';
import { Card, Button, message, Alert, List, Tag, Modal, Select, Input } from 'antd';
import { TruckOutlined, CheckCircleOutlined, ExclamationCircleOutlined } from '@ant-design/icons';
import axios from 'axios';
import API_BASE_URL from '../config';

const { Option } = Select;

const MobileDriverInstructions = () => {
  const [instructions, setInstructions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedInstruction, setSelectedInstruction] = useState(null);
  const [modalVisible, setModalVisible] = useState(false);

  // Mock driver name - in real app this would come from login
  const driverName = "John Smith";

  const fetchDriverInstructions = async () => {
    setLoading(true);
    try {
      // In real app, this would call the API with driver name
      const response = await axios.get(`http://localhost:8000/driver-instructions?driver_name=${driverName}&status=assigned`);
      setInstructions(response.data);
    } catch (error) {
      console.error('Error fetching instructions:', error);
      message.error('Failed to load instructions');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDriverInstructions();
  }, []);

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

  return (
    <div style={{ padding: '16px', maxWidth: '500px', margin: '0 auto' }}>
      <div style={{ textAlign: 'center', marginBottom: '24px' }}>
        <TruckOutlined style={{ fontSize: '48px', color: '#1890ff', marginBottom: '16px' }} />
        <h2>My Collection Instructions</h2>
        <p style={{ color: '#666' }}>Driver: {driverName}</p>
      </div>

      {loading ? (
        <Card>
          <div style={{ textAlign: 'center', padding: '40px' }}>
            <p>Loading your collection instructions...</p>
          </div>
        </Card>
      ) : instructions.length === 0 ? (
        <Card>
          <div style={{ textAlign: 'center', padding: '40px' }}>
            <CheckCircleOutlined style={{ fontSize: '48px', color: '#52c41a', marginBottom: '16px' }} />
            <h3>No Collection Instructions</h3>
            <p>You have no assigned collection tasks at the moment.</p>
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
                    <h4 style={{ margin: 0 }}>{instruction.customer_name}</h4>
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
                  // Store the reason temporarily
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

export default MobileDriverInstructions;
