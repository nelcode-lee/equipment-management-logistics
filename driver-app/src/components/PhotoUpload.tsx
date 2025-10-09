import React, { useState, useRef } from 'react';
import { 
  Card, 
  Button, 
  Upload, 
  message, 
  Typography, 
  Space,
  Progress,
  Result,
  Steps
} from 'antd';
import { 
  CameraOutlined, 
  UploadOutlined, 
  CheckCircleOutlined,
  ArrowLeftOutlined,
  EditOutlined
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const { Title, Text } = Typography;
const { Step } = Steps;

const PhotoUpload: React.FC = () => {
  const navigate = useNavigate();
  const { token } = useAuth();
  const [fileList, setFileList] = useState<any[]>([]);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadResult, setUploadResult] = useState<any>(null);
  const [currentStep, setCurrentStep] = useState(0);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleUpload = async (file: File) => {
    setUploading(true);
    setUploadProgress(0);
    setCurrentStep(1);

    try {
      // Create FormData for file upload (no manual form data needed)
      const uploadData = new FormData();
      uploadData.append('file', file);

      // Simulate upload progress
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 70) {
            clearInterval(progressInterval);
            return 70;
          }
          return prev + 10;
        });
      }, 200);

      // Upload to API
      const headers: any = {};
      
      // Add authentication header if token exists
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
      // Note: Do NOT set Content-Type for FormData - axios sets it automatically with boundary
      
      const response = await axios.post(`${API_URL}/upload-photo`, uploadData, {
        headers,
      });
      
      clearInterval(progressInterval);
      setUploadProgress(100);
      setCurrentStep(2);

      console.log('📸 Upload response:', response.data); // Debug logging

      // Simulate AI processing
      await new Promise(resolve => setTimeout(resolve, 1500));
      setCurrentStep(3);

      if (response.data.success) {
        // Handle both local API and serverless API response formats
        const movements = response.data.movements || [response.data.movement];
        const hasMovements = movements && movements.length > 0;
        
        setUploadResult({
          success: true,
          movements: movements,
          message: hasMovements 
            ? `Photo uploaded and AI data extraction completed! Found ${movements.length} movement(s).`
            : 'Photo uploaded but no equipment data could be extracted. Please try a clearer image.',
          ai_extraction: response.data.ai_extraction || {
            extracted_text: response.data.raw_text,
            processing_notes: 'AI analysis completed'
          }
        });
        
        if (hasMovements) {
          message.success(`Successfully processed ${movements.length} movement(s)!`);
        } else {
          message.warning('Upload successful but no data extracted. Try a clearer delivery note image.');
        }
      } else {
        throw new Error(response.data.error || 'Upload failed');
      }
    } catch (error: any) {
      message.error(error.response?.data?.error || 'Upload failed. Please try again.');
      setCurrentStep(0);
    } finally {
      setUploading(false);
    }
  };

  const handleFileChange = (info: any) => {
    console.log('📁 File change event:', info);
    
    const file = info.file.originFileObj || info.file;
    
    if (file && file instanceof File) {
      const uploadFile = {
        ...file,
        uid: info.file.uid || '1',
        name: file.name,
        status: 'done',
        url: URL.createObjectURL(file)
      };
      setFileList([uploadFile]);
      
      // Trigger upload immediately
      handleUpload(file);
    }
  };

  const handleCameraCapture = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const uploadFile = {
        ...file,
        uid: '1',
        name: file.name,
        status: 'done',
        url: URL.createObjectURL(file)
      };
      setFileList([uploadFile]);
      // Start upload immediately - no form needed
      handleUpload(file);
    }
  };

  const resetUpload = () => {
    setFileList([]);
    setUploadProgress(0);
    setUploadResult(null);
    setCurrentStep(0);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div style={{ padding: '16px', maxWidth: '600px', margin: '0 auto' }}>
      {/* Header */}
      <Card style={{ marginBottom: '16px', borderRadius: '12px' }}>
        <div style={{ display: 'flex', alignItems: 'center', marginBottom: '16px' }}>
          <Button 
            type="text" 
            icon={<ArrowLeftOutlined />} 
            onClick={() => navigate('/')}
            style={{ marginRight: '8px' }}
          />
          <Title level={4} style={{ margin: 0, color: '#1890ff' }}>
            Upload Delivery Note
          </Title>
        </div>

        <Steps current={currentStep} style={{ marginBottom: '24px' }}>
          <Step title="Take Photo" />
          <Step title="Uploading" />
          <Step title="AI Analysis" />
          <Step title="Complete" />
        </Steps>
      </Card>

      {!uploadResult ? (
        <Card style={{ borderRadius: '12px' }}>
          <div style={{ textAlign: 'center', padding: '32px 16px' }}>
            <CameraOutlined style={{ fontSize: '64px', color: '#1890ff', marginBottom: '16px' }} />
            <Title level={4}>Capture or Select Photo</Title>
            <Text type="secondary" style={{ display: 'block', marginBottom: '24px' }}>
              Take a photo of the delivery note and AI will automatically extract equipment data
            </Text>

            <Space direction="vertical" size="large" style={{ width: '100%' }}>
              <Button
                type="primary"
                size="large"
                icon={<CameraOutlined />}
                onClick={handleCameraCapture}
                loading={uploading}
                style={{ 
                  height: '56px',
                  borderRadius: '12px',
                  fontSize: '16px',
                  fontWeight: 'bold'
                }}
                block
              >
                Take Photo
              </Button>

              <Upload
                accept="image/*"
                fileList={fileList}
                onChange={handleFileChange}
                beforeUpload={() => false}
                showUploadList={false}
              >
                <Button
                  size="large"
                  icon={<UploadOutlined />}
                  loading={uploading}
                  style={{ 
                    height: '56px',
                    borderRadius: '12px',
                    fontSize: '16px'
                  }}
                  block
                >
                  Select from Gallery
                </Button>
              </Upload>

              <Button
                size="large"
                icon={<EditOutlined />}
                onClick={() => navigate('/manual-entry')}
                style={{ 
                  height: '48px',
                  borderRadius: '12px',
                  fontSize: '14px',
                  borderStyle: 'dashed'
                }}
                block
              >
                Use Manual Entry Instead
              </Button>
            </Space>

            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              capture="environment"
              style={{ display: 'none' }}
              onChange={handleFileSelect}
            />

            {uploading && (
              <div style={{ marginTop: '24px' }}>
                <Progress 
                  percent={uploadProgress} 
                  status={uploadProgress === 100 ? 'success' : 'active'}
                  strokeColor={{
                    '0%': '#108ee9',
                    '100%': '#87d068',
                  }}
                />
                <Text type="secondary" style={{ display: 'block', marginTop: '8px' }}>
                  {currentStep === 1 && 'Uploading photo...'}
                  {currentStep === 2 && 'AI analyzing delivery note...'}
                  {currentStep === 3 && 'Extracting equipment data...'}
                </Text>
              </div>
            )}
          </div>
        </Card>
      ) : (
        <Card style={{ borderRadius: '12px' }}>
          <Result
            icon={<CheckCircleOutlined style={{ color: '#52c41a' }} />}
            title="Upload Successful!"
            subTitle={uploadResult.message}
            extra={[
              <Button type="primary" onClick={resetUpload} key="upload">
                Upload Another
              </Button>,
              <Button onClick={() => navigate('/manual-entry')} key="manual" icon={<EditOutlined />}>
                Manual Entry
              </Button>,
              <Button onClick={() => navigate('/')} key="home">
                Back to Dashboard
              </Button>
            ]}
          />

          {uploadResult.movements && (
            <div style={{ marginTop: '24px' }}>
              <Title level={5}>AI Extracted Equipment Data:</Title>
              {uploadResult.movements.map((movement: any, index: number) => (
                <Card key={index} size="small" style={{ marginBottom: '8px' }}>
                  <div>
                    <strong>{movement.customer_name}</strong>
                    <br />
                    {movement.quantity} {movement.equipment_type}(s) - {movement.direction.toUpperCase()}
                    <br />
                    <Text type="secondary">AI Confidence: {(movement.confidence * 100).toFixed(1)}%</Text>
                    {!movement.verified && (
                      <>
                        <br />
                        <Text type="warning">⚠️ Requires verification</Text>
                      </>
                    )}
                  </div>
                </Card>
              ))}
              
              {uploadResult.ai_extraction && (
                <Card size="small" style={{ marginTop: '8px', backgroundColor: '#f6ffed' }}>
                  <div>
                    <Text strong>AI Analysis:</Text>
                    <br />
                    <Text type="secondary">{uploadResult.ai_extraction.extracted_text}</Text>
                    <br />
                    <Text type="secondary" style={{ fontSize: '12px' }}>
                      {uploadResult.ai_extraction.processing_notes}
                    </Text>
                  </div>
                </Card>
              )}
            </div>
          )}
        </Card>
      )}
    </div>
  );
};

export default PhotoUpload;