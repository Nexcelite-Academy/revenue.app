# 🚀 Deployment Guide - Revenue.app

## 🌐 **Vercel Deployment (Recommended)**

Vercel provides the easiest deployment path for our full-stack application.

### **Step 1: Prepare for Production**

1. **Database Setup** (Required for production)
   - SQLite won't work on Vercel (serverless environment)
   - Recommended: **Supabase** (free PostgreSQL)
   - Alternative: **PlanetScale**, **Railway**, **Neon**

2. **Get a PostgreSQL Database** (Free Options):
   
   **Option A: Supabase (Recommended)**
   ```bash
   # 1. Go to https://supabase.com
   # 2. Create a new project
   # 3. Copy the DATABASE_URL from Settings > Database
   # Format: postgresql://[user]:[password]@[host]:[port]/[database]
   ```
   
   **Option B: Railway**
   ```bash
   # 1. Go to https://railway.app
   # 2. Create a PostgreSQL service
   # 3. Copy the connection string
   ```

### **Step 2: Deploy to Vercel**

1. **Connect Repository**
   ```bash
   # Go to https://vercel.com
   # Import your GitHub repository: revenue.app
   # Vercel will auto-detect it as a Python project
   ```

2. **Environment Variables**
   Add these in Vercel Dashboard → Settings → Environment Variables:
   ```
   DATABASE_URL=postgresql://your_db_connection_string
   SECRET_KEY=your-super-secret-key-here
   FLASK_ENV=production
   API_PREFIX=/api/v1
   ```

3. **Deploy**
   - Click "Deploy" - Vercel will build and deploy automatically
   - Your app will be available at: `https://your-app.vercel.app`

### **Step 3: Initialize Database**

After first deployment, initialize your database:

```bash
# Option 1: Using API endpoint (recommended)
curl -X POST https://your-app.vercel.app/api/v1/init-db

# Option 2: Run locally against production DB
# Set DATABASE_URL to your production database
cd backend
python -c "from config.database import init_db; init_db()"
python seed_data.py  # Optional: Add sample data
```

---

## 🐳 **Alternative: Docker Deployment**

For other platforms (AWS, DigitalOcean, etc.):

### **Dockerfile**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy requirements
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application
COPY . .

# Set environment variables
ENV FLASK_ENV=production
ENV PORT=8080

# Expose port
EXPOSE 8080

# Run application
CMD ["python", "backend/app.py"]
```

### **Docker Compose** (with PostgreSQL)
```yaml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "8080:8080"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/tutoring
      - SECRET_KEY=your-secret-key
    depends_on:
      - db
  
  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=tutoring
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

---

## ☁️ **Other Cloud Platforms**

### **Render.com**
1. Connect GitHub repository
2. Choose "Web Service"
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `python backend/app.py`
5. Add environment variables

### **Railway.app**
1. Connect GitHub repository
2. Add PostgreSQL service
3. Add environment variables
4. Deploy automatically

### **Heroku**
```bash
# Create Procfile
echo "web: python backend/app.py" > Procfile

# Add buildpack
heroku buildpacks:set heroku/python

# Add PostgreSQL addon
heroku addons:create heroku-postgresql:hobby-dev

# Deploy
git push heroku main
```

---

## 🔐 **Environment Variables Reference**

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@host:5432/db` |
| `SECRET_KEY` | Flask secret key | `super-secret-key-123` |
| `FLASK_ENV` | Environment mode | `production` |
| `API_PREFIX` | API URL prefix | `/api/v1` |
| `ALLOWED_ORIGINS` | CORS origins | `https://yourapp.vercel.app` |

---

## 🧪 **Testing Production Setup**

Before going live, test your deployment:

1. **Health Check**
   ```bash
   curl https://your-app.vercel.app/health
   # Should return: {"status": "healthy"}
   ```

2. **API Test**
   ```bash
   curl https://your-app.vercel.app/api/v1/students/
   # Should return: [] (empty array for new deployment)
   ```

3. **Frontend Test**
   - Visit: `https://your-app.vercel.app`
   - Check that all pages load
   - Test adding a student/teacher

---

## 🔧 **Troubleshooting**

### **Common Issues**

1. **Database Connection Error**
   ```
   Solution: Verify DATABASE_URL format and credentials
   Check: Supabase/Railway dashboard for correct connection string
   ```

2. **CORS Errors**
   ```
   Solution: Add your Vercel domain to ALLOWED_ORIGINS
   Check: Vercel domain matches the one in environment variables
   ```

3. **Build Failures**
   ```
   Solution: Check requirements.txt for correct package versions
   Check: Vercel build logs for specific error messages
   ```

4. **API 404 Errors**
   ```
   Solution: Verify vercel.json routing configuration
   Check: API endpoints use correct /api/v1/ prefix
   ```

### **Database Migration**

If you need to update database schema:

```python
# Create migration script: migrate.py
from config.database import init_db
from sqlalchemy import text, create_engine
import os

engine = create_engine(os.getenv('DATABASE_URL'))
with engine.connect() as conn:
    # Add your migration SQL here
    conn.execute(text("ALTER TABLE students ADD COLUMN new_field VARCHAR(50)"))
    conn.commit()
```

---

## 📊 **Performance Optimization**

### **Production Checklist**

- [ ] PostgreSQL database configured
- [ ] Environment variables set
- [ ] CORS origins configured
- [ ] Database initialized
- [ ] Sample data loaded (optional)
- [ ] Health check working
- [ ] All API endpoints tested
- [ ] Frontend loading correctly
- [ ] Mobile responsiveness verified

### **Monitoring**

- Monitor Vercel dashboard for function execution
- Set up Supabase monitoring for database performance
- Check Vercel logs for any runtime errors

---

**🎉 Your grade-based tutoring management system is now live and ready to help tutoring centers worldwide!** 🌍 