# Deployment Guide - Render.com

This guide covers deploying OnboardIQ to Render.com.

## Prerequisites

- A Render.com account (free tier available)
- Git repository (GitHub, GitLab, or Bitbucket)
- Project code pushed to the repository

## Backend Deployment

### 1. Prepare Your Repository

Ensure your repository includes:
- `Procfile` (already created)
- `requirements.txt` (already updated)
- `render.yaml` (already created)
- `.gitignore` (already created)

### 2. Deploy Backend on Render

#### Option A: Using render.yaml (Recommended)

1. Push your code to your Git repository
2. Go to [Render.com](https://render.com) and click "New +"
3. Select "Blueprint" and connect your repository
4. Render will automatically detect `render.yaml` and create:
   - A PostgreSQL database
   - A web service for the FastAPI backend
5. Click "Apply" to deploy

#### Option B: Manual Deployment

1. **Create PostgreSQL Database**
   - Go to Render Dashboard → New + → PostgreSQL
   - Name: `onboardiq-db`
   - Database: `onboardiq`
   - User: `onboardiq_user`
   - Select Free tier
   - Click "Create Database"

2. **Create Web Service**
   - Go to Render Dashboard → New + → Web Service
   - Connect your repository
   - Configure:
     - **Name**: `onboardiq-api`
     - **Region**: Choose nearest region
     - **Branch**: `main`
     - **Runtime**: Python 3
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Environment Variables**:
     - `DATABASE_URL`: (from PostgreSQL database connection string)
     - `AUTH_SECRET`: (generate a secure random string)
     - `CORS_ORIGINS`: `https://your-frontend-domain.onrender.com`
   - Click "Create Web Service"

### 3. Configure Environment Variables

After deployment, set these environment variables in Render:

```bash
# Database (automatically set if using render.yaml)
DATABASE_URL=postgresql://user:password@host:port/database

# Authentication (generate a secure secret)
AUTH_SECRET=your-secure-random-secret-here

# CORS (update with your frontend URL)
CORS_ORIGINS=https://your-frontend.onrender.com

# Environment
ENVIRONMENT=production
```

### 4. Verify Deployment

- Check the Render dashboard for deployment status
- Visit `https://your-api.onrender.com/health` to verify health check
- Visit `https://your-api.onrender.com/` to see API status

## Frontend Deployment

### Option A: Deploy as Static Site on Render

1. **Build the Frontend Locally**
   ```bash
   cd frontend
   npm install
   npm run build
   ```

2. **Deploy to Render**
   - Go to Render Dashboard → New + → Static Site
   - Connect your repository
   - Configure:
     - **Name**: `onboardiq-frontend`
     - **Branch**: `main`
     - **Build Command**: `cd frontend && npm install && npm run build`
     - **Publish Directory**: `frontend/build`
     - **Environment Variables**:
       - `REACT_APP_API_URL`: `https://your-api.onrender.com`
   - Click "Create Static Site"

### Option B: Deploy to Netlify/Vercel

1. **Build the Frontend**
   ```bash
   cd frontend
   npm install
   npm run build
   ```

2. **Deploy to Netlify**
   - Drag and drop the `frontend/build` folder to Netlify
   - Or connect your Git repository to Netlify

3. **Deploy to Vercel**
   - Connect your Git repository to Vercel
   - Configure build settings:
     - **Framework**: React
     - **Build Command**: `cd frontend && npm install && npm run build`
     - **Output Directory**: `frontend/build`

### Update CORS Configuration

After deploying the frontend, update the backend CORS:

1. Go to your backend web service on Render
2. Navigate to Environment section
3. Update `CORS_ORIGINS` to include your frontend URL:
   ```
   https://your-frontend.onrender.com
   ```

## Post-Deployment Steps

### 1. Test Authentication

- Create a test account via `/auth/signup`
- Login via `/auth/login` to get a JWT token
- Verify protected endpoints work with the token

### 2. Test File Upload

- Upload a CSV/XLSX file via `/upload`
- Verify data is stored in PostgreSQL
- Check dashboard analytics display correctly

### 3. Monitor Logs

- Check Render logs for any errors
- Monitor database connections
- Verify health check endpoint responds

## Troubleshooting

### Database Connection Issues

- Verify `DATABASE_URL` is correctly set
- Check PostgreSQL database is running
- Ensure database schema is created (auto-created on first run)

### CORS Errors

- Verify `CORS_ORIGINS` includes your frontend URL
- Check frontend API URL is correct
- Ensure authentication tokens are being sent

### Build Failures

- Check `requirements.txt` has all dependencies
- Verify Python version compatibility (3.9+)
- Check for syntax errors in Python files

### Authentication Issues

- Verify `AUTH_SECRET` is set and secure
- Check JWT token expiration (30 minutes default)
- Ensure tokens are sent in `Authorization: Bearer <token>` header

## Security Best Practices

1. **Never commit `.env` files** - Use `.env.example` as template
2. **Use strong secrets** - Generate secure `AUTH_SECRET`
3. **Enable HTTPS** - Render provides free SSL certificates
4. **Regular updates** - Keep dependencies updated
5. **Monitor logs** - Watch for suspicious activity

## Scaling Considerations

For production use:

1. **Upgrade Database** - Move from free PostgreSQL to paid tier for more resources
2. **Add Redis** - For caching and session management
3. **Load Balancing** - Render automatically scales web services
4. **CDN** - Use CDN for static assets
5. **Monitoring** - Add error tracking (Sentry, etc.)

## Local Development vs Production

| Feature | Local | Production |
|---------|-------|------------|
| Database | SQLite | PostgreSQL |
| API URL | http://localhost:8001 | https://api.onrender.com |
| Frontend URL | http://localhost:3000 | https://app.onrender.com |
| CORS | localhost URLs | Production URLs |
| Auth Secret | Development | Secure random string |

## Support

For issues:
- Check Render status page: https://status.render.com
- Review Render documentation: https://render.com/docs
- Check application logs in Render dashboard
