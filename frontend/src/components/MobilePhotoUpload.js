import React, { useState, useRef } from 'react';
import { Card, Button, message, Alert, Spin, Input, Typography } from 'antd';
import { CameraOutlined, UploadOutlined, CheckCircleOutlined } from '@ant-design/icons';
import axios from 'axios';

const { Title, Text } = Typography;

const MobilePhotoUpload = () => {
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState(null);
  const [driverName, setDriverName] = useState('');
  const [imagePreview, setImagePreview] = useState(null);
  const fileInputRef = useRef(null);

  // Check if we're on mobile
  const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      // Create preview
      const reader = new FileReader();
      reader.onload = (e) => {
        setImagePreview(e.target.result);
      };
      reader.readAsDataURL(file);
      
      // Process the file
      handleUpload(file);
    }
  };

  const handleUpload = async (file) => {
    setUploading(true);
    setResult(null);

    try {
      const formData = new FormData();
      formData.append('file', file);
      if (driverName) {
        formData.append('driver_name', driverName);
      }

      const response = await axios.post('http://localhost:8000/upload-photo', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      const data = response.data;
      
      if (data.success) {
        setResult(data);
        message.success(`Successfully processed ${data.movements.length} movement(s)`);
      } else {
        message.error(`Processing failed: ${data.error}`);
      }
    } catch (error) {
      console.error('Upload error:', error);
      message.error('Upload failed. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  const openCamera = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  const resetUpload = () => {
    setResult(null);
    setImagePreview(null);
    setDriverName('');
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div style={{ padding: '16px', maxWidth: '500px', margin: '0 auto' }}>
      <Title level={2} style={{ textAlign: 'center', marginBottom: '24px' }}>
        📸 Equipment Photo Upload
      </Title>

      {/* Driver Name Input */}
      <Card style={{ marginBottom: '16px' }}>
        <Text strong style={{ display: 'block', marginBottom: '8px' }}>
          Driver Name:
        </Text>
        <Input
          value={driverName}
          onChange={(e) => setDriverName(e.target.value)}
          placeholder="Enter your name"
          size="large"
          style={{ marginBottom: '16px' }}
        />
      </Card>

      {/* Camera/Upload Section */}
      {!result && (
        <Card style={{ textAlign: 'center', marginBottom: '16px' }}>
          {!imagePreview ? (
            <div>
              <Title level={4}>Take Photo of Delivery Note</Title>
              <Text type="secondary" style={{ display: 'block', marginBottom: '24px' }}>
                Capture the delivery note or paperwork to automatically extract equipment information
              </Text>
              
              <Button
                type="primary"
                size="large"
                icon={<CameraOutlined />}
                onClick={openCamera}
                style={{ 
                  width: '100%', 
                  height: '60px',
                  fontSize: '18px',
                  marginBottom: '16px'
                }}
              >
                {isMobile ? 'Open Camera' : 'Select Photo'}
              </Button>
              
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                capture={isMobile ? "environment" : undefined}
                onChange={handleFileSelect}
                style={{ display: 'none' }}
              />
              
              <Text type="secondary" style={{ fontSize: '12px' }}>
                {isMobile ? 'Camera will open automatically' : 'Click to select from gallery'}
              </Text>
            </div>
          ) : (
            <div>
              <img 
                src={imagePreview} 
                alt="Preview" 
                style={{ 
                  width: '100%', 
                  maxHeight: '300px', 
                  objectFit: 'contain',
                  borderRadius: '8px',
                  marginBottom: '16px'
                }} 
              />
              <Text>Processing image...</Text>
            </div>
          )}
        </Card>
      )}

      {/* Loading State */}
      {uploading && (
        <Card style={{ textAlign: 'center', marginBottom: '16px' }}>
          <Spin size="large" />
          <div style={{ marginTop: '16px' }}>
            <Text>AI is analyzing your photo...</Text>
            <br />
            <Text type="secondary">This may take a few seconds</Text>
          </div>
        </Card>
      )}

      {/* Results */}
      {result && (
        <Card>
          <div style={{ textAlign: 'center', marginBottom: '16px' }}>
            <CheckCircleOutlined style={{ fontSize: '48px', color: '#52c41a' }} />
            <Title level={3} style={{ color: '#52c41a', marginTop: '8px' }}>
              Success!
            </Title>
          </div>

          {result.success ? (
            <div>
              <Alert
                message={`Extracted ${result.movements.length} movement(s)`}
                description={`Confidence: ${(result.movements[0]?.confidence_score * 100 || 0).toFixed(0)}%`}
                type="success"
                style={{ marginBottom: '16px' }}
              />
              
              {result.movements.map((movement, index) => (
                <Card key={index} size="small" style={{ marginBottom: '12px' }}>
                  <div style={{ marginBottom: '8px' }}>
                    <Text strong>Customer: </Text>
                    <Text>{movement.customer_name}</Text>
                  </div>
                  <div style={{ marginBottom: '8px' }}>
                    <Text strong>Equipment: </Text>
                    <Text>{movement.equipment_type} x {movement.quantity}</Text>
                  </div>
                  <div style={{ marginBottom: '8px' }}>
                    <Text strong>Direction: </Text>
                    <Text style={{ 
                      color: movement.direction === 'in' ? '#52c41a' : '#ff4d4f' 
                    }}>
                      {movement.direction === 'in' ? 'IN (To Customer)' : 'OUT (From Customer)'}
                    </Text>
                  </div>
                  {movement.notes && (
                    <div>
                      <Text strong>Notes: </Text>
                      <Text>{movement.notes}</Text>
                    </div>
                  )}
                </Card>
              ))}
              
              <Button 
                type="primary" 
                size="large" 
                onClick={resetUpload}
                style={{ width: '100%', marginTop: '16px' }}
              >
                Upload Another Photo
              </Button>
            </div>
          ) : (
            <Alert
              message="Processing Failed"
              description={result.error}
              type="error"
              action={
                <Button size="small" onClick={resetUpload}>
                  Try Again
                </Button>
              }
            />
          )}
        </Card>
      )}
    </div>
  );
};

export default MobilePhotoUpload;
