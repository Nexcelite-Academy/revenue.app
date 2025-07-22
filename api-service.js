/**
 * API Service Layer for Tutoring Center Management
 * Handles all communication with the backend Flask API
 */

class ApiService {
  constructor() {
    // Use relative URLs so it works on both localhost and Railway
    this.baseURL = '/api/v1';
    this.isLoading = false;
    this.loadingCallbacks = [];
  }

  // Loading state management
  setLoading(loading) {
    this.isLoading = loading;
    this.loadingCallbacks.forEach(callback => callback(loading));
  }

  onLoadingChange(callback) {
    this.loadingCallbacks.push(callback);
  }

  // Generic HTTP methods
  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      },
      ...options
    };

    this.setLoading(true);
    
    try {
      const response = await fetch(url, config);
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.error || `HTTP ${response.status}: ${response.statusText}`);
      }
      
      return data;
    } catch (error) {
      console.error(`API Error [${endpoint}]:`, error);
      throw error;
    } finally {
      this.setLoading(false);
    }
  }

  async get(endpoint, params = {}) {
    const searchParams = new URLSearchParams(params);
    const url = searchParams.toString() ? `${endpoint}?${searchParams}` : endpoint;
    return this.request(url);
  }

  async post(endpoint, data) {
    return this.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(data)
    });
  }

  async put(endpoint, data) {
    return this.request(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data)
    });
  }

  async delete(endpoint) {
    return this.request(endpoint, {
      method: 'DELETE'
    });
  }

  // Students API
  async getStudents(search = '') {
    return this.get('/students/', search ? { search } : {});
  }

  async getStudent(id) {
    return this.get(`/students/${id}/`);
  }

  async createStudent(data) {
    return this.post('/students/', data);
  }

  async updateStudent(id, data) {
    return this.put(`/students/${id}/`, data);
  }

  async deleteStudent(id) {
    return this.delete(`/students/${id}/`);
  }

  async getStudentBalance(studentId, courseName) {
    return this.get(`/students/${studentId}/balance/${encodeURIComponent(courseName)}`);
  }

  async updateStudentBalance(studentId, courseName, hoursChange) {
    return this.put(`/students/${studentId}/balance/${encodeURIComponent(courseName)}/`, {
      hours_change: hoursChange
    });
  }

  async getAvailableGrades() {
    return this.get('/students/grades/');
  }

  // Teachers API
  async getTeachers(search = '') {
    return this.get('/teachers/', search ? { search } : {});
  }

  async getTeacher(id) {
    return this.get(`/teachers/${id}/`);
  }

  async createTeacher(data) {
    return this.post('/teachers/', data);
  }

  async updateTeacher(id, data) {
    return this.put(`/teachers/${id}/`, data);
  }

  async deleteTeacher(id) {
    return this.delete(`/teachers/${id}/`);
  }

  async getTeacherStats(id, startDate = '', endDate = '') {
    const params = {};
    if (startDate) params.start_date = startDate;
    if (endDate) params.end_date = endDate;
    return this.get(`/teachers/${id}/stats/`, params);
  }

  async setTeacherGradeRate(id, grade, rate) {
    return this.post(`/teachers/${id}/grade-rate/`, { grade, rate });
  }

  // Courses API
  async getCourses(search = '') {
    return this.get('/courses/', search ? { search } : {});
  }

  async getCourse(id) {
    return this.get(`/courses/${id}/`);
  }

  async createCourse(data) {
    return this.post('/courses/', data);
  }

  async updateCourse(id, data) {
    return this.put(`/courses/${id}/`, data);
  }

  async deleteCourse(id) {
    return this.delete(`/courses/${id}/`);
  }

  async getCourseStats(id, startDate = '', endDate = '') {
    const params = {};
    if (startDate) params.start_date = startDate;
    if (endDate) params.end_date = endDate;
    return this.get(`/courses/${id}/stats`, params);
  }

  // Payments API
  async getPayments(filters = {}) {
    return this.get('/payments/', filters);
  }

  async getPayment(id) {
    return this.get(`/payments/${id}/`);
  }

  async createPayment(data) {
    return this.post('/payments/', data);
  }

  async updatePayment(id, data) {
    return this.put(`/payments/${id}/`, data);
  }

  async deletePayment(id) {
    return this.delete(`/payments/${id}/`);
  }

  async getPaymentSummary(startDate = '', endDate = '') {
    const params = {};
    if (startDate) params.start_date = startDate;
    if (endDate) params.end_date = endDate;
    return this.get('/payments/summary', params);
  }

  // Sessions API
  async getSessions(filters = {}) {
    return this.get('/sessions/', filters);
  }

  async getSession(id) {
    return this.get(`/sessions/${id}/`);
  }

  async createSession(data) {
    return this.post('/sessions/', data);
  }

  async updateSession(id, data) {
    return this.put(`/sessions/${id}/`, data);
  }

  async deleteSession(id) {
    return this.delete(`/sessions/${id}/`);
  }

  async getSessionSummary(startDate = '', endDate = '') {
    const params = {};
    if (startDate) params.start_date = startDate;
    if (endDate) params.end_date = endDate;
    return this.get('/sessions/summary', params);
  }

  // Expenses API
  async getExpenses(filters = {}) {
    return this.get('/expenses/', filters);
  }

  async getExpense(id) {
    return this.get(`/expenses/${id}/`);
  }

  async createExpense(data) {
    return this.post('/expenses/', data);
  }

  async updateExpense(id, data) {
    return this.put(`/expenses/${id}/`, data);
  }

  async deleteExpense(id) {
    return this.delete(`/expenses/${id}/`);
  }

  async getExpenseCategories() {
    return this.get('/expenses/categories/');
  }

  async getExpenseSummary(startDate = '', endDate = '') {
    const params = {};
    if (startDate) params.start_date = startDate;
    if (endDate) params.end_date = endDate;
    return this.get('/expenses/summary', params);
  }

  // Reports API
  async getDashboardData() {
    return this.get('/reports/dashboard');
  }

  async getFinancialReport(startDate = '', endDate = '') {
    const params = {};
    if (startDate) params.start_date = startDate;
    if (endDate) params.end_date = endDate;
    return this.get('/reports/financial', params);
  }

  async getAttendanceReport(startDate = '', endDate = '') {
    const params = {};
    if (startDate) params.start_date = startDate;
    if (endDate) params.end_date = endDate;
    return this.get('/reports/attendance', params);
  }

  async exportFinancialCsv(startDate, endDate) {
    const url = `${this.baseURL}/reports/export/csv?start_date=${startDate}&end_date=${endDate}`;
    window.open(url, '_blank');
  }

  // Health check
  async healthCheck() {
    return fetch('/health').then(r => r.json());
  }
}

// Global API instance
window.api = new ApiService();

// Global error handler for API errors
window.handleApiError = function(error, operation = 'operation') {
  console.error(`Error during ${operation}:`, error);
  
  let message = 'An unexpected error occurred.';
  if (error.message) {
    message = error.message;
  }
  
  // Show error to user (you can customize this)
  if (typeof showToast === 'function') {
    showToast(message, 'error');
  } else {
    alert(`Error: ${message}`);
  }
};

// Loading indicator helpers
window.showLoading = function() {
  const loader = document.getElementById('globalLoader');
  if (loader) {
    loader.style.display = 'block';
  }
};

window.hideLoading = function() {
  const loader = document.getElementById('globalLoader');
  if (loader) {
    loader.style.display = 'none';
  }
};

// Initialize loading state management
window.api.onLoadingChange((isLoading) => {
  if (isLoading) {
    showLoading();
  } else {
    hideLoading();
  }
}); 