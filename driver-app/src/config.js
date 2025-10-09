// API Configuration for Driver App
const API_BASE_URL = process.env.REACT_APP_API_URL || (process.env.NODE_ENV === 'production' 
  ? 'https://equipmentmanagementlogistics-84alu2mr5.vercel.app'
  : 'http://localhost:8000');

export default API_BASE_URL;
