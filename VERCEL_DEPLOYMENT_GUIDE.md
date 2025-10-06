# Vercel Deployment Guide
## Equipment Management Logistics System

## 🚀 **Deployment Overview**

This guide will help you deploy your Equipment Management Logistics system to Vercel with separate driver and office access.

## 📁 **Project Structure**

```
equipment_management_logistics/
├── api/                          # Backend API (Vercel Functions)
│   └── index.py
├── office-dashboard/             # Office Management App
│   ├── src/
│   ├── vercel.json
│   └── package.json
├── driver-app/                   # Mobile Driver App
│   ├── src/
│   ├── vercel.json
│   └── package.json
├── vercel.json                   # Main API configuration
└── main.py                       # FastAPI backend
```

## 🔧 **Step 1: Deploy Backend API**

### **1.1 Prepare API for Vercel**

1. **Install Vercel CLI:**
   ```bash
   npm i -g vercel
   ```

2. **Login to Vercel:**
   ```bash
   vercel login
   ```

3. **Deploy API:**
   ```bash
   cd /Users/admin/equipment_management_logistics
   vercel --prod
   ```

### **1.2 Configure Environment Variables**

In Vercel Dashboard → Project Settings → Environment Variables:

```env
# Database
DATABASE_URL=postgresql://neondb_owner:npg_Asb4ahlrFHg5@ep-calm-union-ab7g1jas-pooler.eu-west-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require

# API Keys
ANTHROPIC_API_KEY=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

# Security
SECRET_KEY=your_secure_secret_key_here
JWT_EXPIRATION_HOURS=24

# CORS (will be updated after frontend deployment)
CORS_ORIGINS=https://equipment-office.vercel.app,https://equipment-driver.vercel.app

# Application
DEBUG=False
HOST=0.0.0.0
PORT=8000
```

### **1.3 Test API Deployment**

Your API will be available at: `https://equipment-api.vercel.app`

Test endpoints:
- Health: `https://equipment-api.vercel.app/health`
- Docs: `https://equipment-api.vercel.app/docs`

## 🖥️ **Step 2: Deploy Office Dashboard**

### **2.1 Prepare Office Dashboard**

1. **Navigate to office dashboard:**
   ```bash
   cd office-dashboard
   ```

2. **Install dependencies:**
   ```bash
   npm install antd @ant-design/icons axios react-router-dom
   ```

3. **Create office-specific components** (copy from existing frontend)

### **2.2 Deploy to Vercel**

1. **Initialize Vercel project:**
   ```bash
   vercel
   ```

2. **Configure environment variables:**
   ```env
   REACT_APP_API_URL=https://equipment-api.vercel.app
   REACT_APP_APP_TYPE=office
   ```

3. **Deploy:**
   ```bash
   vercel --prod
   ```

### **2.3 Office Dashboard Features**

- Full management interface
- User management
- Equipment specifications
- Analytics and reporting
- Admin controls

## 📱 **Step 3: Deploy Driver App**

### **3.1 Prepare Driver App**

1. **Navigate to driver app:**
   ```bash
   cd driver-app
   ```

2. **Install dependencies:**
   ```bash
   npm install antd @ant-design/icons axios react-router-dom
   ```

3. **The mobile-optimized components are already created**

### **3.2 Deploy to Vercel**

1. **Initialize Vercel project:**
   ```bash
   vercel
   ```

2. **Configure environment variables:**
   ```env
   REACT_APP_API_URL=https://equipment-api.vercel.app
   REACT_APP_APP_TYPE=driver
   ```

3. **Deploy:**
   ```bash
   vercel --prod
   ```

### **3.3 Driver App Features**

- Mobile-optimized interface
- Photo upload with camera
- Collection instructions
- Simple task management
- Touch-friendly controls

## 🌐 **Step 4: Configure Domains**

### **4.1 Custom Domains (Optional)**

1. **Office Dashboard:**
   - Domain: `office.equipment-logistics.com`
   - Configure in Vercel Dashboard

2. **Driver App:**
   - Domain: `driver.equipment-logistics.com`
   - Configure in Vercel Dashboard

3. **API:**
   - Domain: `api.equipment-logistics.com`
   - Configure in Vercel Dashboard

### **4.2 Update CORS Settings**

After deploying frontend apps, update API CORS:

```env
CORS_ORIGINS=https://equipment-office.vercel.app,https://equipment-driver.vercel.app
```

## 🔐 **Step 5: Security Configuration**

### **5.1 Production Security**

1. **Update CORS origins** to production URLs
2. **Set DEBUG=False** in production
3. **Configure proper CORS headers**
4. **Enable HTTPS redirect**

### **5.2 Environment-Specific Settings**

**Development:**
```env
DEBUG=True
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
```

**Production:**
```env
DEBUG=False
CORS_ORIGINS=https://equipment-office.vercel.app,https://equipment-driver.vercel.app
```

## 📊 **Step 6: Testing Deployment**

### **6.1 Test Office Dashboard**

1. Visit: `https://equipment-office.vercel.app`
2. Login with admin credentials
3. Test all management features
4. Verify user management works

### **6.2 Test Driver App**

1. Visit: `https://equipment-driver.vercel.app`
2. Login with driver credentials
3. Test photo upload
4. Test mobile responsiveness

### **6.3 Test API**

1. Test authentication endpoints
2. Test photo upload processing
3. Test role-based access control
4. Verify CORS settings

## 🚀 **Step 7: Go Live**

### **7.1 Final Checklist**

- [ ] API deployed and accessible
- [ ] Office dashboard deployed
- [ ] Driver app deployed
- [ ] Environment variables configured
- [ ] CORS settings updated
- [ ] Security settings applied
- [ ] All endpoints tested
- [ ] Mobile responsiveness verified

### **7.2 User Access**

**Office Users:**
- URL: `https://equipment-office.vercel.app`
- Roles: Admin, Manager, Viewer
- Features: Full management interface

**Driver Users:**
- URL: `https://equipment-driver.vercel.app`
- Roles: Driver
- Features: Mobile-optimized interface

## 📱 **Mobile Optimization**

### **Driver App Features**

1. **Touch-Friendly Interface**
   - Large buttons and touch targets
   - Swipe gestures
   - Mobile-optimized forms

2. **Camera Integration**
   - Direct camera access
   - Photo preview
   - Image compression

3. **Offline Capability**
   - Cache instructions
   - Queue uploads
   - Sync when online

4. **Push Notifications**
   - New instructions
   - Task reminders
   - System updates

## 🔄 **Step 8: Maintenance**

### **8.1 Regular Updates**

1. **Monitor performance**
2. **Update dependencies**
3. **Security patches**
4. **Feature updates**

### **8.2 Monitoring**

1. **Vercel Analytics**
2. **Error tracking**
3. **Performance metrics**
4. **User feedback**

## 🎯 **Expected URLs**

After deployment, you'll have:

- **API**: `https://equipment-api.vercel.app`
- **Office**: `https://equipment-office.vercel.app`
- **Driver**: `https://equipment-driver.vercel.app`

## 🆘 **Troubleshooting**

### **Common Issues**

1. **CORS Errors**
   - Check CORS_ORIGINS environment variable
   - Verify frontend URLs are correct

2. **Authentication Issues**
   - Check JWT_SECRET_KEY
   - Verify token expiration settings

3. **Database Connection**
   - Check DATABASE_URL
   - Verify Neon database is accessible

4. **Build Errors**
   - Check Node.js version
   - Verify all dependencies installed

## 📞 **Support**

If you encounter issues:

1. Check Vercel deployment logs
2. Verify environment variables
3. Test API endpoints directly
4. Check browser console for errors

Your Equipment Management Logistics system will be live and accessible to both office staff and drivers! 🎉
