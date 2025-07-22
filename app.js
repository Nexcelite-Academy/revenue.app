// Tutoring Center Manager - Frontend Application
// Updated to use backend API instead of in-memory store
// =======================

/********************* Utility Helpers ************************/ 
const $ = (selector, scope = document) => scope.querySelector(selector);
const todayStr = () => new Date().toISOString().slice(0, 10);

function calculateStudentAge(birthdate) {
  const diff = Date.now() - new Date(birthdate).getTime();
  return Math.floor(diff / (1000 * 60 * 60 * 24 * 365.25));
}

/********************* Toast Notifications *******************/
function showToast(message, type = 'info') {
  const toastContainer = document.getElementById('toastContainer');
  const toastId = 'toast-' + Date.now();
  
  const bgClass = {
    'success': 'bg-success',
    'error': 'bg-danger', 
    'warning': 'bg-warning',
    'info': 'bg-info'
  }[type] || 'bg-info';
  
  const toastHtml = `
    <div class="toast ${bgClass} text-white" id="${toastId}" role="alert" aria-live="assertive" aria-atomic="true">
      <div class="toast-header ${bgClass} text-white border-0">
        <strong class="me-auto">Notification</strong>
        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast"></button>
      </div>
      <div class="toast-body">
        ${message}
      </div>
    </div>`;
  
  toastContainer.insertAdjacentHTML('beforeend', toastHtml);
  
  const toastElement = document.getElementById(toastId);
  const toast = new bootstrap.Toast(toastElement, {
    autohide: true,
    delay: 5000
  });
  
  toast.show();
  
  toastElement.addEventListener('hidden.bs.toast', () => {
    toastElement.remove();
  });
}

// Make showToast globally available
window.showToast = showToast;

/********************* Navigation ******************************/
let currentView = 'dashboard';

async function switchView(view) {
  currentView = view;
  // update nav active link
  const navLinks = document.querySelectorAll('#main-nav .nav-link');
  navLinks.forEach(a => {
    a.classList.toggle('active', a.dataset.view === view);
  });

  // render (await if it's an async function)
  try {
    const result = render[view]();
    if (result && typeof result.then === 'function') {
      await result;
    }
  } catch (error) {
    console.error(`Error rendering ${view}:`, error);
    handleApiError(error, `loading ${view} view`);
  }
}

/********************* Error Handling *************************/
function showError(container, message, retryCallback = null) {
  const errorHtml = `
    <div class="error-message">
      <strong>Error:</strong> ${message}
      ${retryCallback ? '<button class="btn btn-sm btn-outline-primary retry-button" onclick="' + retryCallback + '">Retry</button>' : ''}
    </div>`;
  
  if (typeof container === 'string') {
    container = document.getElementById(container);
  }
  
  if (container) {
    container.innerHTML = errorHtml;
  }
}

/********************* Rendering Functions ********************/
const render = {
  async dashboard() {
    const viewContainer = $('#view-container');
    
    try {
      const dashboardData = await api.getDashboardData();
      
      // Render dashboard cards
      const cardsHtml = `
        <div class="row row-cols-2 row-cols-md-4 g-3 mb-4">
          <div class="col">
            <div class="card text-center">
              <div class="card-body">
                <h6 class="card-title">Total Revenue</h6>
                <h4 class="text-primary">$${dashboardData.current_month.revenue.toFixed(2)}</h4>
              </div>
            </div>
          </div>
          <div class="col">
            <div class="card text-center">
              <div class="card-body">
                <h6 class="card-title">Salary Expense</h6>
                <h4 class="text-danger">$${dashboardData.current_month.salary_cost.toFixed(2)}</h4>
              </div>
            </div>
          </div>
          <div class="col">
            <div class="card text-center">
              <div class="card-body">
                <h6 class="card-title">Other Costs</h6>
                <h4 class="text-warning">$${dashboardData.current_month.expenses.toFixed(2)}</h4>
              </div>
            </div>
          </div>
          <div class="col">
            <div class="card text-center">
              <div class="card-body">
                <h6 class="card-title">Net Profit</h6>
                <h4 class="text-success">$${dashboardData.current_month.net_profit.toFixed(2)}</h4>
              </div>
            </div>
          </div>
        </div>`;

      // Low balance alerts
      let alertsHtml = '';
      if (dashboardData.low_balance_alerts && dashboardData.low_balance_alerts.length > 0) {
        const alertsList = dashboardData.low_balance_alerts.map(alert => 
          `<li class="list-group-item d-flex justify-content-between align-items-center">
            <span><strong>${alert.student_name}</strong> - ${alert.course_name}</span>
            <span class="badge bg-danger rounded-pill">${alert.balance.toFixed(1)}h</span>
          </li>`
        ).join('');
        
        alertsHtml = `
          <div class="alert alert-warning mt-3">
            <h6><i class="bi bi-exclamation-triangle"></i> Low Balance Alerts</h6>
            <ul class="list-group list-group-flush mt-2">
              ${alertsList}
            </ul>
          </div>`;
      }

      // Chart section
      const chartHtml = `
        <div class="row">
          <div class="col-12">
            <div class="card">
              <div class="card-header">
                <h5 class="card-title">Income vs Costs (Last 6 Months)</h5>
              </div>
              <div class="card-body" style="height: 300px;">
                <canvas id="dashboardChart"></canvas>
              </div>
            </div>
          </div>
        </div>`;

      viewContainer.innerHTML = cardsHtml + alertsHtml + chartHtml;

      // Create chart
      setTimeout(() => {
        const ctx = $('#dashboardChart');
        if (ctx && window.Chart && dashboardData.chart_data) {
          if (window.dashboardChartInst) {
            window.dashboardChartInst.destroy();
          }
          
          const labels = dashboardData.chart_data.map(d => d.month);
          const incomeData = dashboardData.chart_data.map(d => d.revenue);
          const costData = dashboardData.chart_data.map(d => d.costs);
          
          window.dashboardChartInst = new Chart(ctx, {
            type: 'bar',
            data: {
              labels,
              datasets: [
                { label: 'Income', backgroundColor: '#1FB8CD', data: incomeData },
                { label: 'Total Costs', backgroundColor: '#B4413C', data: costData }
              ]
            },
            options: { 
              responsive: true, 
              maintainAspectRatio: false,
              scales: { 
                y: { beginAtZero: true } 
              }
            }
          });
        }
      }, 100);
      
    } catch (error) {
      handleApiError(error, 'loading dashboard');
      showError(viewContainer, 'Failed to load dashboard data', 'render.dashboard()');
    }
  },

  async students() {
    const viewContainer = $('#view-container');
    
    try {
      const students = await api.getStudents();
      
             const rows = students.map(s => {
         const balanceCells = Object.entries(s.balances || {})
           .map(([course, hrs]) => `<div class="${hrs < 2 ? 'low-balance' : ''}">${course}: ${hrs.toFixed(1)}</div>`)
           .join('');
         return `<tr>
           <td>${s.id}</td><td>${s.name}</td><td>${s.gender}</td><td>${s.grade || '<span class="text-muted">Not set</span>'}</td><td>${s.birthdate}</td><td>${s.age}</td><td>${s.parent || ''}</td><td>${s.contact || ''}</td>
           <td>${balanceCells}</td>
           <td>
             <button class="btn btn-sm btn-outline-primary me-2" onclick="openStudentModal(${s.id})">Edit</button>
             <button class="btn btn-sm btn-outline-danger" onclick="deleteStudent(${s.id})">Delete</button>
           </td>
         </tr>`;
       }).join('');

             viewContainer.innerHTML = `<div class="d-flex justify-content-between align-items-center mb-3">
         <h2>Students <span class="badge bg-primary">Grade-Based System ✨</span></h2>
         <button class="btn btn-sm btn-primary" onclick="openStudentModal()">Add Student</button>
       </div>
       <div class="table-responsive">
         <table class="table table-bordered table-hover small">
           <thead class="table-light">
             <tr><th>ID</th><th>Name</th><th>Gender</th><th>Grade</th><th>Birthdate</th><th>Age</th><th>Parent</th><th>Contact</th><th>Balances</th><th>Actions</th></tr>
           </thead>
           <tbody>${rows}</tbody>
         </table>
       </div>`;
      
    } catch (error) {
      handleApiError(error, 'loading students');
      showError(viewContainer, 'Failed to load students', 'render.students()');
    }
  },

  async teachers() {
    const viewContainer = $('#view-container');
    
    try {
      const teachers = await api.getTeachers();
      
             const rows = teachers.map(t => {
         const gradeRatesDisplay = Object.keys(t.grade_rates || {}).length > 0
           ? `<small class="text-success">✓ ${Object.keys(t.grade_rates).length} grades configured</small>`
           : `<small class="text-muted">Using default rate only</small>`;
         
         return `<tr>
           <td>${t.id}</td>
           <td>${t.name}</td>
           <td>$${t.default_rate}</td>
           <td>${gradeRatesDisplay}</td>
           <td>
             <button class="btn btn-sm btn-outline-primary me-2" onclick="openTeacherModal(${t.id})">Edit</button>
             <button class="btn btn-sm btn-outline-info me-2" onclick="showTeacherRates(${t.id})">View Rates</button>
             <button class="btn btn-sm btn-outline-danger" onclick="deleteTeacher(${t.id})">Delete</button>
           </td>
         </tr>`;
       }).join('');

             viewContainer.innerHTML = `<div class="d-flex justify-content-between align-items-center mb-3">
         <h2>Teachers <span class="badge bg-success">Grade-Based Rates ✨</span></h2>
         <button class="btn btn-sm btn-primary" onclick="openTeacherModal()">Add Teacher</button>
       </div>
       <div class="table-responsive">
         <table class="table table-bordered table-hover small">
           <thead class="table-light"><tr><th>ID</th><th>Name</th><th>Default Rate</th><th>Grade Rates</th><th>Actions</th></tr></thead>
           <tbody>${rows}</tbody>
         </table>
       </div>`;
      
    } catch (error) {
      handleApiError(error, 'loading teachers');
      showError(viewContainer, 'Failed to load teachers', 'render.teachers()');
    }
  },

  async courses() {
    const viewContainer = $('#view-container');
    
    try {
      const courses = await api.getCourses();
      
      const rows = courses.map(c => {
        return `<tr><td>${c.id}</td><td>${c.name}</td><td>$${c.base_rate}</td><td>${c.teacher_name || 'Unassigned'}</td>
        <td>
          <button class="btn btn-sm btn-outline-primary me-2" onclick="openCourseModal(${c.id})">Edit</button>
          <button class="btn btn-sm btn-outline-danger" onclick="deleteCourse(${c.id})">Delete</button>
        </td></tr>`;
      }).join('');

      viewContainer.innerHTML = `<div class="d-flex justify-content-between align-items-center mb-3">
        <h2>Courses</h2>
        <button class="btn btn-sm btn-primary" onclick="openCourseModal()">Add Course</button>
      </div>
             <div class="table-responsive">
         <table class="table table-bordered table-hover small">
           <thead class="table-light"><tr><th>ID</th><th>Name</th><th>Base Rate</th><th>Teacher</th><th>Actions</th></tr></thead>
           <tbody>${rows}</tbody>
         </table>
       </div>`;
      
    } catch (error) {
      handleApiError(error, 'loading courses');
      showError(viewContainer, 'Failed to load courses', 'render.courses()');
    }
  },

  async payments() {
    await renderPaymentsView();
  },

  async sessions() {
    await renderSessionsView();
  },

  async attendance() {
    await renderAttendanceView();
  },

  async expenses() {
    await renderExpensesView();
  },

  async reports() {
    await renderReportsView();
  }
};

/********************* Specific Render Functions *************/

async function renderPaymentsView() {
  const viewContainer = $('#view-container');
  
  try {
    const [students, courses, payments] = await Promise.all([
      api.getStudents(),
      api.getCourses(), 
      api.getPayments()
    ]);
    
    const studentOptions = students.map(s => `<option value="${s.id}">${s.name}</option>`).join('');
    const courseOptions = courses.map(c => `<option value="${c.id}">${c.name}</option>`).join('');
    const rows = payments.map(p => {
      return `<tr><td>${p.date}</td><td>${p.student_name}</td><td>${p.course_name}</td><td>${p.purchased_hours}</td><td>$${p.amount_paid}</td><td>${p.payment_method}</td></tr>`;
    }).join('');

    viewContainer.innerHTML = `<h2 class="mb-3">Record Payment</h2>
      <form id="paymentForm" class="row g-3 mb-4 small">
        <div class="col-md-2"><label class="form-label">Date</label><input type="date" class="form-control" name="date" value="${todayStr()}" required></div>
        <div class="col-md-3"><label class="form-label">Student</label><select class="form-select" name="student_id" required><option value="">Select Student</option>${studentOptions}</select></div>
        <div class="col-md-3"><label class="form-label">Course</label><select class="form-select" name="course_id" required><option value="">Select Course</option>${courseOptions}</select></div>
        <div class="col-md-2"><label class="form-label">Purchased Hours</label><input type="number" class="form-control" name="purchased_hours" min="1" step="0.5" required></div>
        <div class="col-md-2"><label class="form-label">Amount Paid</label><input type="number" class="form-control" name="amount_paid" min="0" step="0.01" required></div>
        <div class="col-md-2"><label class="form-label">Payment Method</label><input class="form-control" name="payment_method" value="Cash"></div>
        <div class="col-12"><button class="btn btn-primary btn-sm" type="submit">Add Payment</button></div>
      </form>

      <h3 class="mb-2">Payment History</h3>
      <div class="table-responsive">
        <table class="table table-bordered table-hover small"><thead class="table-light"><tr><th>Date</th><th>Student</th><th>Course</th><th>Hours</th><th>Amount</th><th>Method</th></tr></thead><tbody>${rows}</tbody></table>
      </div>`;

    // Add event listener for form submission
    setTimeout(() => {
      const form = $('#paymentForm');
      if (form) {
        form.addEventListener('submit', handlePaymentSubmit);
      }
    }, 100);
    
  } catch (error) {
    handleApiError(error, 'loading payments');
    showError(viewContainer, 'Failed to load payments data', 'renderPaymentsView()');
  }
}

async function renderSessionsView() {
  const viewContainer = $('#view-container');
  
  try {
    const [students, courses, sessions] = await Promise.all([
      api.getStudents(),
      api.getCourses(),
      api.getSessions()
    ]);
    
    const studentOptions = students.map(s => `<option value="${s.id}">${s.name}</option>`).join('');
    const courseOptions = courses.map(c => `<option value="${c.id}">${c.name}</option>`).join('');
    const rows = sessions.map(s => {
      return `<tr><td>${s.date}</td><td>${s.student_name}</td><td>${s.course_name}</td><td>${s.hours?.toFixed(1)}</td><td>${s.start_time}-${s.end_time}</td></tr>`;
    }).join('');

    viewContainer.innerHTML = `<h2 class="mb-3">Log Session</h2>
      <form id="sessionForm" class="row g-3 small mb-4">
        <div class="col-md-2"><label class="form-label">Date</label><input type="date" class="form-control" name="date" value="${todayStr()}" required></div>
        <div class="col-md-3"><label class="form-label">Student</label><select class="form-select" name="student_id" required><option value="">Select Student</option>${studentOptions}</select></div>
        <div class="col-md-3"><label class="form-label">Course</label><select class="form-select" name="course_id" required><option value="">Select Course</option>${courseOptions}</select></div>
        <div class="col-md-2"><label class="form-label">Start</label><input type="time" class="form-control" name="start_time" required></div>
        <div class="col-md-2"><label class="form-label">End</label><input type="time" class="form-control" name="end_time" required></div>
        <div class="col-12"><button class="btn btn-primary btn-sm" type="submit">Add Session</button></div>
      </form>
      <h3 class="mb-2">Session History</h3>
      <div class="table-responsive"><table class="table table-bordered table-hover small"><thead class="table-light"><tr><th>Date</th><th>Student</th><th>Course</th><th>Hours</th><th>Time</th></tr></thead><tbody>${rows}</tbody></table></div>`;

    // Add event listener for form submission
    setTimeout(() => {
      const form = $('#sessionForm');
      if (form) {
        form.addEventListener('submit', handleSessionSubmit);
      }
    }, 100);
    
  } catch (error) {
    handleApiError(error, 'loading sessions');
    showError(viewContainer, 'Failed to load sessions data', 'renderSessionsView()');
  }
}

async function renderAttendanceView() {
  const viewContainer = $('#view-container');
  const { startInput, endInput } = dateRangeInputs();
  
  viewContainer.innerHTML = `<h2 class="mb-3">Attendance & Salaries</h2>
    <div class="row g-3 align-items-end mb-3 small">${startInput}${endInput}
      <div class="col-auto"><button class="btn btn-sm btn-primary" onclick="renderAttendanceTable()">Run Report</button></div>
    </div>
    <div id="attendanceTableWrap"></div>`;

  renderAttendanceTable();
}

async function renderExpensesView() {
  const viewContainer = $('#view-container');
  
  try {
    const expenses = await api.getExpenses();
    
    const rows = expenses.map(e => `<tr><td>${e.date}</td><td>${e.item}</td><td>$${e.amount.toFixed(2)}</td></tr>`).join('');
    
    viewContainer.innerHTML = `<h2 class="mb-3">Expenses</h2>
      <form id="expenseForm" class="row g-3 small mb-4">
        <div class="col-md-3"><label class="form-label">Date</label><input type="date" class="form-control" name="date" value="${todayStr()}" required></div>
        <div class="col-md-5"><label class="form-label">Item</label><input class="form-control" name="item" required></div>
        <div class="col-md-2"><label class="form-label">Amount</label><input type="number" class="form-control" name="amount" min="0" step="0.01" required></div>
        <div class="col-12"><button class="btn btn-primary btn-sm" type="submit">Add Expense</button></div>
      </form>
      <h3 class="mb-2">Expense Records</h3>
      <div class="table-responsive"><table class="table table-bordered table-hover small"><thead class="table-light"><tr><th>Date</th><th>Item</th><th>Amount</th></tr></thead><tbody>${rows}</tbody></table></div>`;

    // Add event listener for form submission
    setTimeout(() => {
      const form = $('#expenseForm');
      if (form) {
        form.addEventListener('submit', handleExpenseSubmit);
      }
    }, 100);
    
  } catch (error) {
    handleApiError(error, 'loading expenses');
    showError(viewContainer, 'Failed to load expenses data', 'renderExpensesView()');
  }
}

async function renderReportsView() {
  const viewContainer = $('#view-container');
  const { startInput, endInput } = dateRangeInputs();
  
  viewContainer.innerHTML = `<h2 class="mb-3">Financial Reports</h2>
    <div class="row g-3 align-items-end mb-3 small">${startInput}${endInput}
      <div class="col-auto"><button class="btn btn-sm btn-primary" onclick="generateReport()">Run Report</button></div>
      <div class="col-auto"><button class="btn btn-sm btn-outline-secondary" onclick="exportCsv()">Export CSV</button></div>
    </div>
    <div id="reportOutput"></div>`;

  generateReport();
}

/********************* Date Range Helper ***********************/
function dateRangeInputs() {
  const today = new Date();
  const firstDay = new Date(today.getFullYear(), today.getMonth(), 1);
  const startHtml = `<div class="col-auto"><label class="form-label">Start Date</label><input type="date" class="form-control" id="startDate" value="${firstDay.toISOString().slice(0, 10)}"></div>`;
  const endHtml = `<div class="col-auto"><label class="form-label">End Date</label><input type="date" class="form-control" id="endDate" value="${today.toISOString().slice(0, 10)}"></div>`;
  return { startInput: startHtml, endInput: endHtml };
}

/********************* Event Handlers **************************/
async function handlePaymentSubmit(e) {
  e.preventDefault();
  
  try {
    const data = Object.fromEntries(new FormData(e.target).entries());
    
    // Convert to proper types
    data.student_id = parseInt(data.student_id);
    data.course_id = parseInt(data.course_id);
    data.purchased_hours = parseFloat(data.purchased_hours);
    data.amount_paid = parseFloat(data.amount_paid);
    
    await api.createPayment(data);
    showToast('Payment recorded successfully!', 'success');
    
    // Refresh the payments view
    render.payments();
    
  } catch (error) {
    handleApiError(error, 'recording payment');
  }
}

async function handleSessionSubmit(e) {
  e.preventDefault();
  
  try {
    const data = Object.fromEntries(new FormData(e.target).entries());
    
    // Convert to proper types
    data.student_id = parseInt(data.student_id);
    data.course_id = parseInt(data.course_id);
    
    await api.createSession(data);
    showToast('Session logged successfully!', 'success');
    
    // Refresh the sessions view
    render.sessions();
    
  } catch (error) {
    handleApiError(error, 'logging session');
  }
}

async function handleExpenseSubmit(e) {
  e.preventDefault();
  
  try {
    const data = Object.fromEntries(new FormData(e.target).entries());
    data.amount = parseFloat(data.amount);
    
    await api.createExpense(data);
    showToast('Expense recorded successfully!', 'success');
    
    // Refresh the expenses view
    render.expenses();
    
  } catch (error) {
    handleApiError(error, 'recording expense');
  }
}

/********************* CRUD Operations *************************/
async function deleteStudent(id) {
  if (confirm('Delete this student?')) {
    try {
      await api.deleteStudent(id);
      showToast('Student deleted successfully!', 'success');
      render.students();
    } catch (error) {
      handleApiError(error, 'deleting student');
    }
  }
}

async function deleteTeacher(id) {
  if (confirm('Delete this teacher?')) {
    try {
      await api.deleteTeacher(id);
      showToast('Teacher deleted successfully!', 'success');
      render.teachers();
    } catch (error) {
      handleApiError(error, 'deleting teacher');
    }
  }
}

async function deleteCourse(id) {
  if (confirm('Delete this course?')) {
    try {
      await api.deleteCourse(id);
      showToast('Course deleted successfully!', 'success');
      render.courses();
    } catch (error) {
      handleApiError(error, 'deleting course');
    }
  }
}

/********************* Report Functions ***********************/

/********************* Modals *********************************/
let currentModal = null;

function openModal(title, bodyHtml, onSave) {
  const modalElem = $('#globalModal');
  const modalContent = $('#globalModalContent');
  
  modalContent.innerHTML = `
    <div class="modal-header">
      <h5 class="modal-title">${title}</h5>
      <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
    </div>
    <form id="modalForm">
      <div class="modal-body">${bodyHtml}</div>
      <div class="modal-footer">
        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
        <button type="submit" class="btn btn-primary">Save</button>
      </div>
    </form>`;
  
  const form = $('#modalForm');
  form.addEventListener('submit', e => {
    e.preventDefault();
    const data = Object.fromEntries(new FormData(e.target).entries());
    if (onSave(data) !== false) {
      currentModal.hide();
    }
  });
  
  currentModal = new bootstrap.Modal(modalElem);
  currentModal.show();
}

async function openStudentModal(id) {
  try {
    const [existing, grades] = await Promise.all([
      id ? api.getStudent(id) : Promise.resolve({ name: '', gender: 'F', birthdate: '', grade: '', parent: '', contact: '' }),
      api.getAvailableGrades()
    ]);
    
    const gradeOptions = grades.map(grade => 
      `<option value="${grade}" ${grade === existing.grade ? 'selected' : ''}>${grade}</option>`
    ).join('');
    
    openModal(id ? 'Edit Student' : 'Add Student', `
      <div class="row g-3">
        <div class="col-md-6">
          <label class="form-label">Name</label>
          <input class="form-control" name="name" value="${existing.name || ''}" required>
        </div>
        <div class="col-md-3">
          <label class="form-label">Gender</label>
          <select class="form-select" name="gender">
            <option value="F" ${existing.gender === 'F' ? 'selected' : ''}>Female</option>
            <option value="M" ${existing.gender === 'M' ? 'selected' : ''}>Male</option>
          </select>
        </div>
        <div class="col-md-3">
          <label class="form-label">Grade Level ✨</label>
          <select class="form-select" name="grade">
            <option value="">Select Grade</option>
            ${gradeOptions}
          </select>
        </div>
        <div class="col-md-3">
          <label class="form-label">Birthdate</label>
          <input type="date" class="form-control" name="birthdate" value="${existing.birthdate || ''}">
        </div>
        <div class="col-md-4">
          <label class="form-label">Parent</label>
          <input class="form-control" name="parent" value="${existing.parent || ''}">
        </div>
        <div class="col-md-5">
          <label class="form-label">Contact</label>
          <input class="form-control" name="contact" value="${existing.contact || ''}">
        </div>
      </div>`, async (data) => {
        if (id) {
          await api.updateStudent(id, data);
          showToast('Student updated successfully!', 'success');
        } else {
          await api.createStudent(data);
          showToast('Student created successfully!', 'success');
        }
        render.students();
      });
  } catch (error) {
    handleApiError(error, id ? 'loading student details' : 'opening student form');
  }
}

async function openTeacherModal(id) {
  try {
    const [existing, grades] = await Promise.all([
      id ? api.getTeacher(id) : Promise.resolve({ name: '', default_rate: 30.0, grade_rates: {} }),
      api.getAvailableGrades()
    ]);
    
    // Generate grade rate inputs
    const gradeRateInputs = grades.map(grade => {
      const rate = (existing.grade_rates && existing.grade_rates[grade]) || '';
      return `
        <div class="col-md-6">
          <label class="form-label">${grade} Rate</label>
          <div class="input-group">
            <span class="input-group-text">$</span>
            <input type="number" step="0.01" class="form-control grade-rate-input" 
                   data-grade="${grade}" value="${rate}" placeholder="Use default">
          </div>
        </div>`;
    }).join('');
    
    openModal(id ? 'Edit Teacher - Grade-Based Rates ✨' : 'Add Teacher - Grade-Based Rates ✨', `
      <div class="row g-3">
        <div class="col-md-8">
          <label class="form-label">Teacher Name</label>
          <input class="form-control" name="name" value="${existing.name || ''}" required>
        </div>
        <div class="col-md-4">
          <label class="form-label">Default Rate</label>
          <div class="input-group">
            <span class="input-group-text">$</span>
            <input type="number" step="0.01" class="form-control" name="default_rate" 
                   value="${existing.default_rate || 30.0}" required>
          </div>
        </div>
        <div class="col-12">
          <hr>
          <h6 class="text-primary">📚 Grade-Specific Rates (Optional)</h6>
          <small class="text-muted">Leave empty to use default rate for that grade</small>
        </div>
        ${gradeRateInputs}
      </div>`, async (data) => {
        // Process form data
        data.default_rate = parseFloat(data.default_rate);
        
        // Collect grade rates
        const gradeRates = {};
        document.querySelectorAll('.grade-rate-input').forEach(input => {
          const grade = input.dataset.grade;
          const rate = input.value.trim();
          if (rate && !isNaN(rate)) {
            gradeRates[grade] = parseFloat(rate);
          }
        });
        data.grade_rates = gradeRates;
        
        if (id) {
          await api.updateTeacher(id, data);
          showToast('Teacher updated with grade-based rates!', 'success');
        } else {
          await api.createTeacher(data);
          showToast('Teacher created with grade-based rates!', 'success');
        }
        render.teachers();
      });
  } catch (error) {
    handleApiError(error, id ? 'loading teacher details' : 'opening teacher form');
  }
}

async function openCourseModal(id) {
  try {
    const [existing, teachers] = await Promise.all([
      id ? api.getCourse(id) : Promise.resolve({ name: '', base_rate: '', teacher_id: '' }),
      api.getTeachers()
    ]);
    
    const teacherOptions = teachers.map(t => 
      `<option value="${t.id}" ${t.id === existing.teacher_id ? 'selected' : ''}>${t.name}</option>`
    ).join('');
    
    openModal(id ? 'Edit Course' : 'Add Course', `
      <div class="row g-3">
        <div class="col-md-6">
          <label class="form-label">Name</label>
          <input class="form-control" name="name" value="${existing.name || ''}" required>
        </div>
        <div class="col-md-3">
          <label class="form-label">Base Rate</label>
          <input type="number" step="0.01" class="form-control" name="base_rate" value="${existing.base_rate || ''}" required>
        </div>
        <div class="col-md-3">
          <label class="form-label">Teacher</label>
          <select class="form-select" name="teacher_id" required>
            <option value="">Select Teacher</option>
            ${teacherOptions}
          </select>
        </div>
      </div>`, async (data) => {
        data.base_rate = parseFloat(data.base_rate);
        data.teacher_id = parseInt(data.teacher_id);
        if (id) {
          await api.updateCourse(id, data);
          showToast('Course updated successfully!', 'success');
        } else {
          await api.createCourse(data);
          showToast('Course created successfully!', 'success');
        }
        render.courses();
      });
  } catch (error) {
    handleApiError(error, id ? 'loading course details' : 'opening course form');
  }
}

/********************* Report Functions ***********************/
async function renderAttendanceTable() {
  const startEl = $('#startDate');
  const endEl = $('#endDate');
  const start = startEl ? startEl.value : '';
  const end = endEl ? endEl.value : '';
  
  try {
    const data = await api.getAttendanceReport(start, end);
    const rows = data.teachers.map(d => 
      `<tr><td>${d.teacher_name}</td><td>${d.total_hours.toFixed(1)}</td><td>$${d.hourly_rate}</td><td>$${d.total_salary.toFixed(2)}</td></tr>`
    ).join('');
    
    const wrapEl = $('#attendanceTableWrap');
    if (wrapEl) {
      wrapEl.innerHTML = `<div class="table-responsive">
        <table class="table table-bordered table-hover">
          <thead class="table-light">
            <tr><th>Teacher</th><th>Total Hours</th><th>Hourly Rate</th><th>Salary</th></tr>
          </thead>
          <tbody>${rows}</tbody>
        </table>
      </div>`;
    }
  } catch (error) {
    handleApiError(error, 'loading attendance report');
    const wrapEl = $('#attendanceTableWrap');
    if (wrapEl) {
      showError(wrapEl, 'Failed to load attendance data', 'renderAttendanceTable()');
    }
  }
}

async function generateReport() {
  const startEl = $('#startDate');
  const endEl = $('#endDate');
  const start = startEl ? startEl.value : '';
  const end = endEl ? endEl.value : '';
  
  try {
    const fin = await api.getFinancialReport(start, end);
    
    const summaryHtml = `<div class="row row-cols-2 row-cols-md-4 g-3 mb-4">
      <div class="col"><div class="card text-center"><div class="card-body"><h6>Revenue</h6><h4>$${fin.summary.total_revenue.toFixed(2)}</h4></div></div></div>
      <div class="col"><div class="card text-center"><div class="card-body"><h6>Salary Expense</h6><h4>$${fin.summary.total_salary_cost.toFixed(2)}</h4></div></div></div>
      <div class="col"><div class="card text-center"><div class="card-body"><h6>Other Expenses</h6><h4>$${fin.summary.total_expenses.toFixed(2)}</h4></div></div></div>
      <div class="col"><div class="card text-center"><div class="card-body"><h6>Net Profit</h6><h4>$${fin.summary.net_profit.toFixed(2)}</h4></div></div></div>
    </div>`;
    
    const courseRows = Object.entries(fin.course_analysis).map(([courseName, data]) => 
      `<tr><td>${courseName}</td><td>${data.enrollment_count}</td><td>$${data.revenue.toFixed(2)}</td><td>$${data.salary_cost.toFixed(2)}</td><td>${data.outstanding_balance.toFixed(1)}</td></tr>`
    ).join('');
    
    const coursesTable = `<h5>Course Level Analysis</h5>
      <div class="table-responsive">
        <table class="table table-bordered table-hover">
          <thead class="table-light">
            <tr><th>Course</th><th>Enrollments</th><th>Revenue</th><th>Salary</th><th>Outstanding Hours</th></tr>
          </thead>
          <tbody>${courseRows}</tbody>
        </table>
      </div>`;
    
    const teacherRows = Object.entries(fin.teacher_analysis).map(([teacherName, data]) => 
      `<tr><td>${teacherName}</td><td>${data.signed_hours.toFixed(1)}</td><td>${data.total_hours.toFixed(1)}</td><td>${data.remaining_hours.toFixed(1)}</td></tr>`
    ).join('');
    
    const teacherTable = `<h5 class="mt-4">Teacher Level Analysis</h5>
      <div class="table-responsive">
        <table class="table table-bordered table-hover">
          <thead class="table-light">
            <tr><th>Teacher</th><th>Signed Hours</th><th>Taught Hours</th><th>Remaining</th></tr>
          </thead>
          <tbody>${teacherRows}</tbody>
        </table>
      </div>`;

    const outputEl = $('#reportOutput');
    if (outputEl) {
      outputEl.innerHTML = summaryHtml + coursesTable + teacherTable;
    }
  } catch (error) {
    handleApiError(error, 'generating financial report');
    const outputEl = $('#reportOutput');
    if (outputEl) {
      showError(outputEl, 'Failed to generate report', 'generateReport()');
    }
  }
}

function exportCsv() {
  const startEl = $('#startDate');
  const endEl = $('#endDate');
  const start = startEl ? startEl.value : '';
  const end = endEl ? endEl.value : '';
  
  if (!start || !end) {
    showToast('Please select start and end dates', 'warning');
    return;
  }
  
  try {
    api.exportFinancialCsv(start, end);
    showToast('Export initiated - check your downloads', 'success');
  } catch (error) {
    handleApiError(error, 'exporting CSV');
  }
}

/********************* Helpers *********************************/
function dateRangeInputs() {
  const today = new Date();
  const thirtyAgo = new Date();
  thirtyAgo.setDate(today.getDate() - 30);
  
  const startHtml = `<div class="col-md-3">
    <label class="form-label">Start Date</label>
    <input type="date" class="form-control" id="startDate" value="${thirtyAgo.toISOString().slice(0, 10)}">
  </div>`;
  
  const endHtml = `<div class="col-md-3">
    <label class="form-label">End Date</label>
    <input type="date" class="form-control" id="endDate" value="${today.toISOString().slice(0, 10)}">
  </div>`;
  
  return { startInput: startHtml, endInput: endHtml };
}

/********************* Grade-Based Rate Functions *************/
async function showTeacherRates(teacherId) {
  try {
    const teacher = await api.getTeacher(teacherId);
    
    const defaultRateHtml = `
      <div class="alert alert-info">
        <strong>Default Rate:</strong> $${teacher.default_rate}/hour
        <br><small>Used when no specific grade rate is set</small>
      </div>`;
    
    const gradeRatesHtml = Object.keys(teacher.grade_rates || {}).length > 0
      ? Object.entries(teacher.grade_rates)
          .sort(([a], [b]) => a.localeCompare(b))
          .map(([grade, rate]) => 
            `<tr>
              <td><strong>${grade}</strong></td>
              <td class="text-end">$${rate}/hour</td>
              <td class="text-center">
                <span class="badge ${rate > teacher.default_rate ? 'bg-success' : rate < teacher.default_rate ? 'bg-warning' : 'bg-secondary'}">
                  ${rate > teacher.default_rate ? '+' : rate < teacher.default_rate ? '-' : '='}${Math.abs(rate - teacher.default_rate).toFixed(2)}
                </span>
              </td>
            </tr>`
          ).join('')
      : '<tr><td colspan="3" class="text-center text-muted">No grade-specific rates configured</td></tr>';
    
    const modalContent = `
      ${defaultRateHtml}
      <h6 class="text-primary mb-3">📚 Grade-Specific Rates</h6>
      <table class="table table-sm table-bordered">
        <thead class="table-light">
          <tr><th>Grade</th><th>Rate</th><th>vs Default</th></tr>
        </thead>
        <tbody>
          ${gradeRatesHtml}
        </tbody>
      </table>
      <div class="mt-3">
        <small class="text-muted">
          💡 <strong>How it works:</strong> When a student books a session, the system automatically uses their grade-specific rate if configured, otherwise falls back to the default rate.
        </small>
      </div>`;
    
    openModal(`${teacher.name} - Rate Structure`, modalContent, () => false); // No save action
  } catch (error) {
    handleApiError(error, 'loading teacher rates');
  }
}

/********************* Init ***********************************/
document.addEventListener('DOMContentLoaded', async () => {
  // Set up navigation
  const navLinks = document.querySelectorAll('#main-nav .nav-link');
  navLinks.forEach(link => {
    link.addEventListener('click', async (e) => {
      e.preventDefault();
      const view = e.target.dataset.view;
      if (view) {
        await switchView(view);
      }
    });
  });
  
  // Check API health on startup
  try {
    await api.healthCheck();
    console.log('Backend API is connected and healthy');
  } catch (error) {
    console.error('Backend API is not available:', error);
    showToast('Backend server is not available. Please check if the server is running.', 'error');
  }
  
  // Load dashboard initially
  await switchView('dashboard');
});