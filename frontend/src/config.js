// API Configuration
const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? 'https://equipmentmanagementlogistics-goeiwxy8b.vercel.app'
  : 'http://localhost:8000';

export default API_BASE_URL;
