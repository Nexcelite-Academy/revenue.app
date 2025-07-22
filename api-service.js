/**
 * API Service Layer for Tutoring Center Management
 * Handles all communication with the backend Flask API
 */

class ApiService {
  constructor() {
    // Detect environment and set appropriate base URL
    this.baseURL = this.getApiBaseURL();
    this.isLoading = false;
    this.loadingCallbacks = [];
  }

  /**
   * Get the appropriate API base URL based on environment
   */
  getApiBaseURL() {
    // Production/Vercel deployment
    if (window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1') {
      return ''; // Use relative URLs for Vercel
    }
    
    // Local development
    return 'http://localhost:5000';
  }

  // Loading state management
  setLoading(loading) {
    this.isLoading = loading;
    this.loadingCallbacks.forEach(callback => callback(loading));
  }

  onLoadingChange(callback) {
    this.loadingCallbacks.push(callback);
  }

  showGlobalLoading() {
    this.setLoading(true);
    const loader = document.getElementById('globalLoader');
    if (loader) {
      loader.style.display = 'flex';
    }
  }

  hideGlobalLoading() {
    this.setLoading(false);
    const loader = document.getElementById('globalLoader');
    if (loader) {
      loader.style.display = 'none';
    }
  }

  // Generic HTTP methods
  async request(endpoint, options = {}) {
    const url = `${this.baseURL}/api/v1${endpoint}`;
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      },
      ...options
    };

    this.showGlobalLoading();
    
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
      this.hideGlobalLoading();
    }
  }

  async get(endpoint, params = {}) {
    const queryString = Object.keys(params).length
      ? '?' + new URLSearchParams(params).toString()
      : '';
    return this.request(`${endpoint}${queryString}`);
  }

  async post(endpoint, data = {}) {
    return this.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(data)
    });
  }

  async put(endpoint, data = {}) {
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

  // Health check
  async healthCheck() {
    try {
      const response = await fetch(`${this.baseURL}/health`);
      return response.ok;
    } catch {
      return false;
    }
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

  // Reports API
  async getDashboardData() {
    return this.get('/reports/dashboard/');
  }

  async getFinancialReport(startDate = '', endDate = '') {
    const params = {};
    if (startDate) params.start_date = startDate;
    if (endDate) params.end_date = endDate;
    return this.get('/reports/financial/', params);
  }

  async getAttendanceReport(startDate = '', endDate = '') {
    const params = {};
    if (startDate) params.start_date = startDate;
    if (endDate) params.end_date = endDate;
    return this.get('/reports/attendance/', params);
  }

  async exportFinancialCsv(startDate, endDate) {
    const url = `${this.baseURL}/api/v1/reports/export/csv?start_date=${startDate}&end_date=${endDate}`;
    window.open(url, '_blank');
  }
}

// Global API instance
window.api = new ApiService();

// Global error handler
window.handleApiError = function(error, context = '') {
  console.error(`Error during ${context}:`, error);
  
  const message = error.message || 'An unexpected error occurred';
  const errorDiv = document.createElement('div');
  errorDiv.className = 'alert alert-danger alert-dismissible fade show';
  errorDiv.innerHTML = `
    <strong>Error ${context ? `during ${context}` : ''}:</strong> ${message}
    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
  `;
  
  const container = document.getElementById('view-container');
  if (container) {
    container.insertBefore(errorDiv, container.firstChild);
  }
};

// Toast notification system
window.showToast = function(message, type = 'info', duration = 5000) {
  const toastContainer = document.getElementById('toastContainer');
  if (!toastContainer) return;

  const toastId = 'toast-' + Date.now();
  const bgClass = {
    'success': 'bg-success',
    'error': 'bg-danger', 
    'warning': 'bg-warning',
    'info': 'bg-info'
  }[type] || 'bg-info';

  const toastHtml = `
    <div id="${toastId}" class="toast" role="alert" aria-live="assertive" aria-atomic="true">
      <div class="toast-header ${bgClass} text-white">
        <strong class="me-auto">Notification</strong>
        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast"></button>
      </div>
      <div class="toast-body">
        ${message}
      </div>
    </div>
  `;

  toastContainer.insertAdjacentHTML('beforeend', toastHtml);
  
  const toastElement = document.getElementById(toastId);
  const toast = new bootstrap.Toast(toastElement, { delay: duration });
  toast.show();

  // Remove from DOM after hiding
  toastElement.addEventListener('hidden.bs.toast', () => {
    toastElement.remove();
  });
}; 