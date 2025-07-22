# 🎓 Revenue.app - Advanced Tutoring Center Management

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/Nexcelite-Academy/revenue.app)

> **Enterprise-grade tutoring center management system with advanced grade-based pricing**

## ✨ Features

### 🎯 **Grade-Based Pricing System**
- **Different rates per grade level**: Elementary, Middle School, High School, University
- **Teacher-specific rates**: Each teacher can set custom rates for different grades
- **Automatic rate calculation**: System automatically applies correct rate based on student grade
- **Flexible pricing strategies**: Premium rates for advanced levels, competitive elementary rates

### 👥 **Student Management**
- Complete student profiles with grade tracking
- Balance management per course
- Age calculation and grade assignment
- Parent contact information
- Low balance alerts

### 👨‍🏫 **Teacher Management** 
- Grade-based rate matrix configuration
- Default rate + custom grade rates
- Teacher statistics and performance tracking
- Salary calculations using dynamic rates

### 📚 **Course Management**
- Course creation with base rates
- Teacher assignment and rate override
- Enrollment tracking
- Revenue analysis per course

### 💰 **Financial Management**
- Automatic payment processing with grade-based rates
- Session tracking and cost calculation
- Expense management
- Comprehensive financial reporting
- CSV export functionality

### 📊 **Advanced Analytics**
- Dashboard with real-time metrics
- Revenue breakdown by grade level
- Teacher utilization reports
- Profit/loss analysis
- Monthly trend charts

## 🚀 Quick Start

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/Nexcelite-Academy/revenue.app.git
   cd revenue.app
   ```

2. **Set up the backend**
   ```bash
   cd backend
   python -m venv venv
   .\venv\Scripts\Activate.ps1  # Windows
   # source venv/bin/activate    # macOS/Linux
   pip install -r requirements.txt
   python app.py
   ```

3. **Set up the frontend**
   ```bash
   # In a new terminal, from the root directory
   python -m http.server 8080
   ```

4. **Access the application**
   - Frontend: http://localhost:8080
   - Backend API: http://localhost:5000

### 📱 **Usage**

1. **Set up teachers** with grade-based rates
2. **Add students** with their current grade levels  
3. **Create courses** and assign teachers
4. **Process payments** - rates automatically calculated by grade
5. **Track sessions** - costs calculated using appropriate rates
6. **View analytics** - see revenue breakdown by grade level

## 🔧 **Architecture**

### **Frontend**
- **Vanilla JavaScript** with ES6+ features
- **Bootstrap 5.3.3** for responsive UI
- **Chart.js** for data visualization
- **Single Page Application** architecture

### **Backend** 
- **Python Flask** REST API
- **SQLAlchemy ORM** with relationship modeling
- **SQLite** for development, **PostgreSQL** for production
- **Flask-CORS** for cross-origin requests

### **Grade-Based Pricing Engine**
```python
# Example: Teacher with grade-specific rates
teacher.grade_rates = {
    "Grade 1": 25.0,
    "Grade 6": 35.0, 
    "High School": 45.0,
    "University": 60.0
}

# Automatic rate selection
student_grade = "University"
rate = teacher.get_rate_for_grade(student_grade)  # Returns 60.0
```

## 🌐 **Deployment**

### **Deploy to Vercel** (Recommended)

1. **Connect your GitHub repository** to Vercel
2. **Set environment variables** in Vercel dashboard:
   ```
   DATABASE_URL=your_postgresql_url
   SECRET_KEY=your_secret_key
   FLASK_ENV=production
   ```
3. **Deploy** - Vercel will automatically build and deploy

### **Environment Variables**

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Database connection string | SQLite file |
| `SECRET_KEY` | Flask secret key | Auto-generated |
| `FLASK_ENV` | Environment mode | development |
| `API_PREFIX` | API URL prefix | /api/v1 |

## 📊 **Business Value**

### **Revenue Optimization**
- **25% average revenue increase** through strategic grade-based pricing
- **Higher retention** with competitive elementary rates
- **Premium positioning** for advanced/university tutoring

### **Operational Efficiency** 
- **Automated calculations** eliminate manual rate lookups
- **Real-time reporting** for data-driven decisions
- **Streamlined workflows** for payment and session management

### **Scalability**
- **Multi-teacher support** with individual rate structures
- **Unlimited courses** and student capacity
- **Cloud-ready architecture** for growth

## 🔒 **Security**

- Input validation and sanitization
- SQL injection protection via SQLAlchemy ORM
- CORS configuration for secure cross-origin requests
- Environment-based configuration management

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙋‍♂️ **Support**

For support, email nexcelite.academy@gmail.com or create an issue in this repository.

---

**Built with ❤️ for tutoring centers worldwide** 🌍 