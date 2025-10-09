import React, { useState, useEffect } from 'react';
import { 
  Card, 
  Button, 
  Form,
  Input,
  Select,
  DatePicker,
  InputNumber,
  Typography, 
  Space,
  message,
  Result,
  Divider
} from 'antd';
import { 
  ArrowLeftOutlined,
  SaveOutlined,
  CheckCircleOutlined,
  PlusOutlined,
  MinusCircleOutlined
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';
import dayjs, { Dayjs } from 'dayjs';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const { Title, Text } = Typography;
const { Option } = Select;

interface ManualEntryFormData {
  customer_name: string;
  equipment_type: string;
  quantity: number;
  direction: 'in' | 'out';
  date: Dayjs;
  notes?: string;
}

const EQUIPMENT_TYPES = [
  { value: 'pallet', label: 'Pallet' },
  { value: 'cage', label: 'Cage' },
  { value: 'dolly', label: 'Dolly' },
  { value: 'stillage', label: 'Stillage' },
  { value: 'container', label: 'Container' },
  { value: 'other', label: 'Other' }
];

const ManualEntry: React.FC = () => {
  const navigate = useNavigate();
  const { token, user } = useAuth();
  const [form] = Form.useForm();
  const [submitting, setSubmitting] = useState(false);
  const [submitSuccess, setSubmitSuccess] = useState(false);
  const [submitResult, setSubmitResult] = useState<any>(null);
  const [entries, setEntries] = useState<ManualEntryFormData[]>([]);

  const handleSubmit = async (values: any) => {
    setSubmitting(true);

    try {
      // Prepare movement data
      const movementData = {
        customer_name: values.customer_name.trim(),
        equipment_type: values.equipment_type,
        quantity: values.quantity,
        direction: values.direction,
        timestamp: values.date.toISOString(),
        driver_name: user?.full_name || user?.username || 'Manual Entry',
        confidence_score: 1.0, // Manual entries have 100% confidence
        notes: values.notes ? `Manual Entry: ${values.notes}` : 'Manual Entry',
        verified: true, // Manual entries are pre-verified
        source_image_url: null
      };

      // Submit to API
      const headers: any = {
        'Content-Type': 'application/json'
      };
      
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const response = await axios.post(`${API_URL}/manual-entry`, movementData, { headers });

      if (response.data.success || response.data.movement_id) {
        setSubmitSuccess(true);
        setSubmitResult({
          ...movementData,
          movement_id: response.data.movement_id
        });
        message.success('Equipment movement recorded successfully!');
        form.resetFields();
        // Reset date to today
        form.setFieldsValue({ date: dayjs() });
      } else {
        throw new Error(response.data.error || 'Failed to record movement');
      }
    } catch (error: any) {
      console.error('Manual entry error:', error);
      message.error(error.response?.data?.error || 'Failed to record movement. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleAddAnother = () => {
    setSubmitSuccess(false);
    setSubmitResult(null);
    form.resetFields();
    form.setFieldsValue({ date: dayjs() });
  };

  const handleBatchAdd = () => {
    const values = form.getFieldsValue();
    if (values.customer_name && values.equipment_type && values.quantity && values.direction) {
      setEntries([...entries, { ...values, date: values.date || dayjs() }]);
      form.resetFields(['equipment_type', 'quantity', 'direction', 'notes']);
      message.success('Entry added to batch. Add more or submit all.');
    } else {
      message.warning('Please fill in all required fields before adding to batch.');
    }
  };

  const handleRemoveEntry = (index: number) => {
    setEntries(entries.filter((_, i) => i !== index));
    message.info('Entry removed from batch.');
  };

  const handleSubmitBatch = async () => {
    if (entries.length === 0) {
      message.warning('No entries to submit. Add at least one entry.');
      return;
    }

    setSubmitting(true);

    try {
      const headers: any = {
        'Content-Type': 'application/json'
      };
      
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      // Submit all entries
      const promises = entries.map(entry => {
        const movementData = {
          customer_name: entry.customer_name.trim(),
          equipment_type: entry.equipment_type,
          quantity: entry.quantity,
          direction: entry.direction,
          timestamp: entry.date.toISOString(),
          driver_name: user?.full_name || user?.username || 'Manual Entry',
          confidence_score: 1.0,
          notes: entry.notes ? `Manual Entry: ${entry.notes}` : 'Manual Entry',
          verified: true,
          source_image_url: null
        };

        return axios.post(`${API_URL}/manual-entry`, movementData, { headers });
      });

      const results = await Promise.all(promises);
      const successCount = results.filter(r => r.data.success || r.data.movement_id).length;

      setSubmitSuccess(true);
      setSubmitResult({
        batch: true,
        count: successCount,
        total: entries.length
      });
      message.success(`Successfully recorded ${successCount} of ${entries.length} movements!`);
      setEntries([]);
      form.resetFields();
      form.setFieldsValue({ date: dayjs() });
    } catch (error: any) {
      console.error('Batch entry error:', error);
      message.error('Failed to record some movements. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  useEffect(() => {
    // Set default date to today
    form.setFieldsValue({ 
      date: dayjs(),
      quantity: 1
    });
  }, [form]);

  if (submitSuccess) {
    return (
      <div style={{ padding: '16px', maxWidth: '600px', margin: '0 auto' }}>
        <Card style={{ borderRadius: '12px' }}>
          <Result
            icon={<CheckCircleOutlined style={{ color: '#52c41a' }} />}
            title="Movement Recorded!"
            subTitle={
              submitResult?.batch 
                ? `Successfully recorded ${submitResult.count} equipment movements.`
                : `Equipment movement has been recorded successfully with 100% confidence.`
            }
            extra={[
              <Button type="primary" onClick={handleAddAnother} key="another">
                Add Another Entry
              </Button>,
              <Button onClick={() => navigate('/')} key="home">
                Back to Dashboard
              </Button>
            ]}
          />

          {submitResult && !submitResult.batch && (
            <div style={{ marginTop: '24px' }}>
              <Title level={5}>Movement Details:</Title>
              <Card size="small" style={{ backgroundColor: '#f6ffed' }}>
                <div>
                  <strong>{submitResult.customer_name}</strong>
                  <br />
                  {submitResult.quantity} {submitResult.equipment_type}(s) - {submitResult.direction.toUpperCase()}
                  <br />
                  <Text type="secondary">
                    {dayjs(submitResult.timestamp).format('DD/MM/YYYY HH:mm')}
                  </Text>
                  <br />
                  <Text type="success">✓ Verified Manual Entry</Text>
                </div>
              </Card>
            </div>
          )}
        </Card>
      </div>
    );
  }

  return (
    <div style={{ padding: '16px', maxWidth: '600px', margin: '0 auto' }}>
      {/* Header */}
      <Card style={{ marginBottom: '16px', borderRadius: '12px' }}>
        <div style={{ display: 'flex', alignItems: 'center' }}>
          <Button 
            type="text" 
            icon={<ArrowLeftOutlined />} 
            onClick={() => navigate('/')}
            style={{ marginRight: '8px' }}
          />
          <div>
            <Title level={4} style={{ margin: 0, color: '#1890ff' }}>
              Manual Entry
            </Title>
            <Text type="secondary" style={{ fontSize: '12px' }}>
              Failsafe data capture for equipment movements
            </Text>
          </div>
        </div>
      </Card>

      {/* Info Card */}
      <Card 
        size="small" 
        style={{ 
          marginBottom: '16px', 
          borderRadius: '8px',
          backgroundColor: '#e6f7ff',
          borderColor: '#91d5ff'
        }}
      >
        <Text style={{ fontSize: '12px' }}>
          💡 <strong>Tip:</strong> Use this form when AI photo capture fails or for quick manual entries. 
          All manual entries are marked as verified with 100% confidence.
        </Text>
      </Card>

      {/* Manual Entry Form */}
      <Card style={{ borderRadius: '12px' }}>
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
          initialValues={{
            date: dayjs(),
            quantity: 1
          }}
        >
          <Form.Item
            label="Customer Name"
            name="customer_name"
            rules={[
              { required: true, message: 'Please enter customer name' },
              { min: 2, message: 'Customer name must be at least 2 characters' }
            ]}
          >
            <Input 
              placeholder="e.g., Tesco, Sainsbury's, Costa Coffee" 
              size="large"
              autoComplete="off"
            />
          </Form.Item>

          <Form.Item
            label="Equipment Type"
            name="equipment_type"
            rules={[{ required: true, message: 'Please select equipment type' }]}
          >
            <Select 
              placeholder="Select equipment type" 
              size="large"
              showSearch
            >
              {EQUIPMENT_TYPES.map(type => (
                <Option key={type.value} value={type.value}>
                  {type.label}
                </Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item
            label="Quantity"
            name="quantity"
            rules={[
              { required: true, message: 'Please enter quantity' },
              { type: 'number', min: 1, message: 'Quantity must be at least 1' }
            ]}
          >
            <InputNumber 
              min={1} 
              placeholder="Enter quantity" 
              size="large"
              style={{ width: '100%' }}
            />
          </Form.Item>

          <Form.Item
            label="Direction"
            name="direction"
            rules={[{ required: true, message: 'Please select direction' }]}
          >
            <Select placeholder="Select direction" size="large">
              <Option value="in">
                <div>
                  <strong>IN</strong> - Equipment going TO customer
                  <br />
                  <Text type="secondary" style={{ fontSize: '12px' }}>
                    Delivery / Equipment out from warehouse
                  </Text>
                </div>
              </Option>
              <Option value="out">
                <div>
                  <strong>OUT</strong> - Equipment coming FROM customer
                  <br />
                  <Text type="secondary" style={{ fontSize: '12px' }}>
                    Collection / Returns to warehouse
                  </Text>
                </div>
              </Option>
            </Select>
          </Form.Item>

          <Form.Item
            label="Date & Time"
            name="date"
            rules={[{ required: true, message: 'Please select date and time' }]}
          >
            <DatePicker 
              showTime 
              format="DD/MM/YYYY HH:mm"
              size="large"
              style={{ width: '100%' }}
              placeholder="Select date and time"
            />
          </Form.Item>

          <Form.Item
            label="Notes (Optional)"
            name="notes"
          >
            <Input.TextArea 
              placeholder="Add any additional notes or observations..."
              rows={3}
              showCount
              maxLength={500}
            />
          </Form.Item>

          <Divider style={{ margin: '16px 0' }} />

          <Form.Item style={{ marginBottom: 0 }}>
            <Space direction="vertical" style={{ width: '100%' }} size="middle">
              <Button
                type="primary"
                htmlType="submit"
                icon={<SaveOutlined />}
                loading={submitting}
                size="large"
                block
                style={{ 
                  height: '48px',
                  borderRadius: '8px',
                  fontSize: '16px',
                  fontWeight: 'bold'
                }}
              >
                Submit Entry
              </Button>

              <Button
                icon={<PlusOutlined />}
                onClick={handleBatchAdd}
                size="large"
                block
                style={{ 
                  height: '44px',
                  borderRadius: '8px'
                }}
              >
                Add to Batch ({entries.length})
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Card>

      {/* Batch Entries */}
      {entries.length > 0 && (
        <Card 
          title={`Batch Entries (${entries.length})`}
          style={{ marginTop: '16px', borderRadius: '12px' }}
          extra={
            <Button 
              type="primary" 
              onClick={handleSubmitBatch}
              loading={submitting}
              icon={<SaveOutlined />}
            >
              Submit All
            </Button>
          }
        >
          <Space direction="vertical" style={{ width: '100%' }} size="small">
            {entries.map((entry, index) => (
              <Card 
                key={index} 
                size="small" 
                style={{ backgroundColor: '#fafafa' }}
                extra={
                  <Button 
                    type="text" 
                    danger 
                    size="small"
                    icon={<MinusCircleOutlined />}
                    onClick={() => handleRemoveEntry(index)}
                  >
                    Remove
                  </Button>
                }
              >
                <div>
                  <strong>{entry.customer_name}</strong>
                  <br />
                  {entry.quantity} {entry.equipment_type}(s) - {entry.direction.toUpperCase()}
                  <br />
                  <Text type="secondary" style={{ fontSize: '12px' }}>
                    {entry.date.format('DD/MM/YYYY HH:mm')}
                  </Text>
                  {entry.notes && (
                    <>
                      <br />
                      <Text type="secondary" style={{ fontSize: '12px' }}>
                        Note: {entry.notes}
                      </Text>
                    </>
                  )}
                </div>
              </Card>
            ))}
          </Space>
        </Card>
      )}
    </div>
  );
};

export default ManualEntry;

