import React, { useState } from 'react';
import { Form, Input, Button, Card, Typography, message, Space, Divider } from 'antd';
import { UserOutlined, LockOutlined, MailOutlined, PhoneOutlined, IdcardOutlined, TruckOutlined } from '@ant-design/icons';
import { useAuth } from '../contexts/AuthContext';
import Footer from './Footer';
import API_BASE_URL from '../config';

const { Title, Text } = Typography;

interface RegisterProps {
  onSuccess: () => void;
}

const Register: React.FC<RegisterProps> = ({ onSuccess }) => {
  const [loading, setLoading] = useState(false);

  const onFinish = async (values: {
    username: string;
    email: string;
    password: string;
    confirmPassword: string;
    full_name: string;
    driver_license?: string;
    phone_number?: string;
    company?: string;
  }) => {
    setLoading(true);
    try {
      // Validate password confirmation
      if (values.password !== values.confirmPassword) {
        message.error('Passwords do not match');
        setLoading(false);
        return;
      }

      // Prepare registration data
      const registrationData = {
        username: values.username,
        email: values.email,
        password: values.password,
        full_name: values.full_name,
        driver_license: values.driver_license,
        phone_number: values.phone_number,
        company: values.company
      };

      // Call registration API
      const response = await fetch(`${API_BASE_URL}/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(registrationData),
      });

      if (response.ok) {
        message.success('Registration successful! You can now login.');
        onSuccess();
      } else {
        const errorData = await response.json();
        message.error(errorData.detail || 'Registration failed');
      }
    } catch (error: any) {
      message.error(error.message || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ 
      minHeight: '100vh', 
      display: 'flex', 
      flexDirection: 'column',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      padding: '20px'
    }}>
      <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <Card 
          style={{ 
            width: '100%', 
            maxWidth: 500, 
            boxShadow: '0 8px 32px rgba(0,0,0,0.1)',
            borderRadius: '16px'
          }}
        >
        <div style={{ textAlign: 'center', marginBottom: '32px' }}>
          <TruckOutlined style={{ fontSize: '48px', color: '#1890ff', marginBottom: '16px' }} />
          <Title level={2} style={{ margin: 0, color: '#1890ff' }}>
            Driver Registration
          </Title>
          <Text type="secondary">
            Join Equipment Management Logistics
          </Text>
        </div>

        <Form
          name="register"
          onFinish={onFinish}
          layout="vertical"
          size="large"
        >
          <Form.Item
            name="full_name"
            rules={[{ required: true, message: 'Please enter your full name!' }]}
          >
            <Input
              prefix={<UserOutlined />}
              placeholder="Full Name"
              style={{ borderRadius: '8px' }}
            />
          </Form.Item>

          <Form.Item
            name="username"
            rules={[{ required: true, message: 'Please enter your username!' }]}
          >
            <Input
              prefix={<UserOutlined />}
              placeholder="Username"
              style={{ borderRadius: '8px' }}
            />
          </Form.Item>

          <Form.Item
            name="email"
            rules={[
              { required: true, message: 'Please enter your email!' },
              { type: 'email', message: 'Please enter a valid email!' }
            ]}
          >
            <Input
              prefix={<MailOutlined />}
              placeholder="Email"
              style={{ borderRadius: '8px' }}
            />
          </Form.Item>

          <Form.Item
            name="driver_license"
            rules={[{ required: true, message: 'Please enter your driver license number!' }]}
          >
            <Input
              prefix={<IdcardOutlined />}
              placeholder="Driver License Number"
              style={{ borderRadius: '8px' }}
            />
          </Form.Item>

          <Form.Item
            name="phone_number"
            rules={[{ required: true, message: 'Please enter your phone number!' }]}
          >
            <Input
              prefix={<PhoneOutlined />}
              placeholder="Phone Number"
              style={{ borderRadius: '8px' }}
            />
          </Form.Item>

          <Form.Item
            name="company"
          >
            <Input
              prefix={<TruckOutlined />}
              placeholder="Company (Optional)"
              style={{ borderRadius: '8px' }}
            />
          </Form.Item>

          <Form.Item
            name="password"
            rules={[{ required: true, message: 'Please enter your password!' }]}
          >
            <Input.Password
              prefix={<LockOutlined />}
              placeholder="Password"
              style={{ borderRadius: '8px' }}
            />
          </Form.Item>

          <Form.Item
            name="confirmPassword"
            rules={[{ required: true, message: 'Please confirm your password!' }]}
          >
            <Input.Password
              prefix={<LockOutlined />}
              placeholder="Confirm Password"
              style={{ borderRadius: '8px' }}
            />
          </Form.Item>

          <Form.Item style={{ marginBottom: 0 }}>
            <Button
              type="primary"
              htmlType="submit"
              loading={loading}
              block
              style={{ 
                height: '48px',
                borderRadius: '8px',
                fontSize: '16px',
                fontWeight: 'bold'
              }}
            >
              Register
            </Button>
          </Form.Item>
        </Form>

        <Divider />

        <div style={{ textAlign: 'center' }}>
          <Text type="secondary">
            Already have an account?{' '}
            <Button 
              type="link" 
              onClick={onSuccess}
              style={{ padding: 0, fontWeight: 'bold' }}
            >
              Login here
            </Button>
          </Text>
        </div>
        </Card>
      </div>
      <Footer />
    </div>
  );
};

export default Register;
