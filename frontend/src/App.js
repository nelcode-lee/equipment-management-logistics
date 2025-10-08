import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Layout, Menu, theme } from 'antd';
import { 
  DashboardOutlined, 
  UploadOutlined, 
  AlertOutlined, 
  HistoryOutlined,
  BarChartOutlined,
  TruckOutlined,
  SettingOutlined,
  TrophyOutlined,
  CarOutlined
} from '@ant-design/icons';
import axios from 'axios';
import API_BASE_URL from './config';
import Dashboard from './components/Dashboard';
import PhotoUpload from './components/PhotoUpload';
import Alerts from './components/Alerts';
import Movements from './components/Movements';
import Balances from './components/Balances';
import DriverInstructions from './components/DriverInstructions';
import FleetManagement from './components/FleetManagement';
import MobilePhotoUpload from './components/MobilePhotoUpload';
import MobileDriverInstructions from './components/MobileDriverInstructions';
import Settings from './components/Settings';
import Insights from './components/Insights';
import DriverApp from './components/DriverApp';
import './App.css';

const { Header, Sider, Content } = Layout;

function App() {
  const {
    token: { colorBgContainer, borderRadiusLG },
  } = theme.useToken();

  const menuItems = [
    {
      key: 'dashboard',
      icon: <DashboardOutlined />,
      label: 'Dashboard',
    },
    {
      key: 'upload',
      icon: <UploadOutlined />,
      label: 'Upload Photo',
    },
    {
      key: 'instructions',
      icon: <TruckOutlined />,
      label: 'Driver Instructions',
    },
    {
      key: 'fleet',
      icon: <CarOutlined />,
      label: 'Fleet Management',
    },
    {
      key: 'alerts',
      icon: <AlertOutlined />,
      label: 'Alerts',
    },
    {
      key: 'movements',
      icon: <HistoryOutlined />,
      label: 'Movement History',
    },
    {
      key: 'balances',
      icon: <BarChartOutlined />,
      label: 'Customer Balances',
    },
    {
      key: 'settings',
      icon: <SettingOutlined />,
      label: 'Settings',
    },
    {
      key: 'insights',
      icon: <TrophyOutlined />,
      label: 'Insights',
    },
  ];

  const [selectedKey, setSelectedKey] = React.useState('dashboard');
  const [companyLogo, setCompanyLogo] = React.useState(null);
  
  // Check if we're on mobile
  const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
  
  // Check if this is a driver URL (e.g., /driver or ?mode=driver)
  const isDriverMode = window.location.pathname.includes('/driver') || 
                      window.location.search.includes('mode=driver') ||
                      window.location.search.includes('app=driver');

  // Fetch company logo on component mount
  React.useEffect(() => {
    const fetchLogo = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/company/logo`);
        if (response.data.logo) {
          setCompanyLogo(response.data.logo);
        }
      } catch (error) {
        console.error('Error fetching logo:', error);
      }
    };
    fetchLogo();
  }, []);

  const renderContent = () => {
    switch (selectedKey) {
      case 'dashboard':
        return <Dashboard />;
      case 'upload':
        return isMobile ? <MobilePhotoUpload /> : <PhotoUpload />;
      case 'instructions':
        return isMobile ? <MobileDriverInstructions /> : <DriverInstructions />;
      case 'fleet':
        return <FleetManagement />;
      case 'alerts':
        return <Alerts />;
      case 'movements':
        return <Movements />;
      case 'balances':
        return <Balances />;
      case 'settings':
        return <Settings />;
      case 'insights':
        return <Insights />;
      default:
        return <Dashboard />;
    }
  };

  // If in driver mode, render the dedicated driver app
  if (isDriverMode) {
    return <DriverApp />;
  }

  return (
    <Router>
      <Layout style={{ minHeight: '100vh' }}>
        <Sider
          breakpoint="lg"
          collapsedWidth="0"
          style={{
            background: colorBgContainer,
          }}
        >
          <div style={{ 
            height: 32, 
            margin: 16, 
            background: 'rgba(0,0,0,0.1)',
            borderRadius: 6,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontWeight: 'bold',
            gap: '8px'
          }}>
            {companyLogo ? (
              <>
                <img 
                  src={`${API_BASE_URL}${companyLogo}`} 
                  alt="Company Logo" 
                  style={{ height: '24px', objectFit: 'contain' }} 
                />
                <span>Equipment Tracker</span>
              </>
            ) : (
              'Equipment Tracker'
            )}
          </div>
          <Menu
            mode="inline"
            selectedKeys={[selectedKey]}
            items={menuItems}
            onClick={({ key }) => setSelectedKey(key)}
          />
        </Sider>
        <Layout>
          <Header
            style={{
              padding: 0,
              background: colorBgContainer,
              display: 'flex',
              alignItems: 'center',
              paddingLeft: 24,
              fontSize: 18,
              fontWeight: 'bold'
            }}
          >
            AI-Powered Equipment Tracking System
          </Header>
          <Content
            style={{
              margin: '24px 16px',
              padding: 24,
              minHeight: 280,
              background: colorBgContainer,
              borderRadius: borderRadiusLG,
            }}
          >
            {renderContent()}
          </Content>
        </Layout>
      </Layout>
    </Router>
  );
}

export default App;

