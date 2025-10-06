import React, { useState } from 'react';
import { Upload, Button, message, Card, Descriptions, Tag, Spin, Alert } from 'antd';
import { InboxOutlined, UploadOutlined } from '@ant-design/icons';
import axios from 'axios';

const { Dragger } = Upload;

const PhotoUpload = () => {
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState(null);
  const [driverName, setDriverName] = useState('');

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

    return false; // Prevent default upload
  };

  const uploadProps = {
    name: 'file',
    multiple: false,
    accept: 'image/*',
    beforeUpload: handleUpload,
    showUploadList: false,
  };

  return (
    <div>
      <h2>Upload Delivery Note Photo</h2>
      
      <Card style={{ marginBottom: 24 }}>
        <div style={{ marginBottom: 16 }}>
          <label style={{ display: 'block', marginBottom: 8, fontWeight: 'bold' }}>
            Driver Name (Optional):
          </label>
          <input
            type="text"
            value={driverName}
            onChange={(e) => setDriverName(e.target.value)}
            placeholder="Enter driver name"
            style={{
              width: '100%',
              padding: '8px 12px',
              border: '1px solid #d9d9d9',
              borderRadius: '6px',
              fontSize: '14px'
            }}
          />
        </div>

        <Dragger {...uploadProps} style={{ padding: '40px 20px' }}>
          <p className="ant-upload-drag-icon">
            <InboxOutlined />
          </p>
          <p className="ant-upload-text">
            Click or drag delivery note photo to this area to upload
          </p>
          <p className="ant-upload-hint">
            Support for single image upload. AI will extract equipment movement data.
          </p>
        </Dragger>
      </Card>

      {uploading && (
        <Card>
          <div style={{ textAlign: 'center', padding: '20px' }}>
            <Spin size="large" />
            <p style={{ marginTop: 16 }}>Processing image with AI...</p>
          </div>
        </Card>
      )}

      {result && (
        <Card title="Extraction Results">
          {result.success ? (
            <div>
              <Alert
                message="Success"
                description={`Extracted ${result.movements.length} movement(s) with ${(result.movements[0]?.confidence_score * 100 || 0).toFixed(0)}% confidence`}
                type="success"
                showIcon
                style={{ marginBottom: 16 }}
              />
              
              {result.movements.map((movement, index) => (
                <Card key={index} size="small" style={{ marginBottom: 16 }}>
                  <Descriptions column={2} size="small">
                    <Descriptions.Item label="Customer">
                      <strong>{movement.customer_name}</strong>
                    </Descriptions.Item>
                    <Descriptions.Item label="Equipment Type">
                      <Tag color="blue">{movement.equipment_type}</Tag>
                    </Descriptions.Item>
                    <Descriptions.Item label="Quantity">
                      {movement.quantity}
                    </Descriptions.Item>
                    <Descriptions.Item label="Direction">
                      <Tag color={movement.direction === 'in' ? 'green' : 'red'}>
                        {movement.direction === 'in' ? 'IN (To Customer)' : 'OUT (From Customer)'}
                      </Tag>
                    </Descriptions.Item>
                    <Descriptions.Item label="Confidence Score">
                      <Tag color={movement.confidence_score > 0.8 ? 'green' : movement.confidence_score > 0.6 ? 'orange' : 'red'}>
                        {(movement.confidence_score * 100).toFixed(0)}%
                      </Tag>
                    </Descriptions.Item>
                    <Descriptions.Item label="Driver">
                      {movement.driver_name || 'Not specified'}
                    </Descriptions.Item>
                    {movement.notes && (
                      <Descriptions.Item label="Notes" span={2}>
                        {movement.notes}
                      </Descriptions.Item>
                    )}
                  </Descriptions>
                </Card>
              ))}
            </div>
          ) : (
            <Alert
              message="Extraction Failed"
              description={result.error}
              type="error"
              showIcon
            />
          )}
        </Card>
      )}
    </div>
  );
};

export default PhotoUpload;

