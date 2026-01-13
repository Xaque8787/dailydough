# Email Modal Template Integration Guide

This guide shows how to integrate the new email modal into report templates.

## Required Changes

### 1. Add Email Button to Report Actions

For saved reports, add an "Email" button alongside View/Download buttons:

```html
<div class="report-actions">
    <a href="/reports/tip-report/view/{{ report.filename }}" class="btn btn-primary btn-sm">View</a>
    <a href="/reports/tip-report/download/{{ report.filename }}" class="btn btn-secondary btn-sm">Download</a>
    <button class="btn btn-secondary btn-sm" onclick="openEmailModalForSaved('{{ report.filename }}')">Email</button>
</div>
```

### 2. Add Email Option to Export Modal

In the export/generate report modal, add an email button:

```html
<div class="modal-actions">
    <button class="btn btn-secondary" onclick="closeExportModal()">Cancel</button>
    <button class="btn btn-primary" onclick="exportReport()">Export CSV</button>
    <button class="btn btn-primary" onclick="openEmailModalForExport()">Send via Email</button>
</div>
```

### 3. Add Email Modal HTML

Add this modal structure before the closing `</div>` of your container:

```html
<div id="email-modal" class="modal">
    <div class="modal-content">
        <h3>Email Report</h3>
        <p>Select recipients to email this report.</p>

        <form id="email-form" onsubmit="return sendEmails(event)">
            <div class="email-recipients-section">
                <h4>Admin Users</h4>
                <div id="admin-users-list" class="user-checkboxes">
                    <!-- Admin users will be loaded here dynamically -->
                    <p style="color: #666;">Loading users...</p>
                </div>
            </div>

            <div class="form-group">
                <label class="checkbox-label">
                    <input type="checkbox" id="additional_email_checkbox" onchange="toggleAdditionalEmail()">
                    Send to additional email address
                </label>
            </div>

            <div id="additional_email_container" style="display: none;">
                <div class="form-group">
                    <label for="additional_email_input">Additional Email Address</label>
                    <input type="email" id="additional_email_input" class="form-control" placeholder="example@domain.com">
                </div>
            </div>

            <div class="modal-actions">
                <button type="button" class="btn btn-secondary" onclick="closeEmailModal()">Cancel</button>
                <button type="submit" class="btn btn-primary">Send Emails</button>
            </div>
        </form>
    </div>
</div>
```

### 4. Add CSS Styles

Add these styles to your `<style>` section:

```css
.email-recipients-section {
    margin: 20px 0;
    padding: 15px;
    background: #f8f9fa;
    border-radius: 5px;
}

.email-recipients-section h4 {
    margin: 0 0 15px 0;
    font-size: 1rem;
    color: #2c3e50;
}

.user-checkboxes {
    display: flex;
    flex-direction: column;
    gap: 10px;
}

.user-checkbox-label {
    display: flex;
    align-items: center;
    padding: 8px 12px;
    background: white;
    border: 1px solid #e9ecef;
    border-radius: 4px;
    cursor: pointer;
    transition: background 0.2s;
}

.user-checkbox-label:hover {
    background: #f8f9fa;
}

.user-checkbox-label input[type="checkbox"] {
    margin-right: 10px;
    cursor: pointer;
}

.user-checkbox-label span {
    font-size: 0.95rem;
    color: #495057;
}
```

### 5. Add JavaScript Functions

Add these JavaScript functions to your `<script>` section:

```javascript
let emailContext = {
    type: null,  // 'saved_daily', 'saved_tip', 'export_daily', 'export_tip', 'employee_tip'
    year: null,
    month: null,
    filename: null,
    startDate: null,
    endDate: null,
    employeeSlug: null
};

const REPORT_TYPE = 'tips'; // or 'daily' depending on your report page

async function loadAdminUsers() {
    try {
        const response = await fetch(`/reports/api/admin-users?report_type=${REPORT_TYPE}`);
        const result = await response.json();

        if (result.success) {
            renderAdminUsers(result.users);
        }
    } catch (error) {
        console.error('Failed to load admin users:', error);
        document.getElementById('admin-users-list').innerHTML =
            '<p style="color: #dc3545;">Failed to load users</p>';
    }
}

function renderAdminUsers(users) {
    const container = document.getElementById('admin-users-list');

    if (users.length === 0) {
        container.innerHTML = '<p style="color: #666; font-style: italic;">No admin users with emails found.</p>';
        return;
    }

    let html = '';
    users.forEach(user => {
        html += `
            <label class="user-checkbox-label">
                <input type="checkbox"
                       name="user_email"
                       value="${user.email}"
                       data-user-id="${user.id}"
                       ${user.opt_in ? 'checked' : ''}>
                <span>${user.username} (${user.email})</span>
            </label>
        `;
    });

    container.innerHTML = html;
}

function openEmailModalForSaved(filename) {
    emailContext = {
        type: 'saved_tip',  // or 'saved_daily'
        filename: filename
    };
    loadAdminUsers();
    document.getElementById('email-modal').classList.add('active');
}

function openEmailModalForExport() {
    // Get dates from your export form
    const exportType = document.querySelector('input[name="export_type"]:checked').value;

    let startDate, endDate;

    if (exportType === 'month') {
        const monthValue = document.getElementById('export_month').value;
        if (!monthValue) {
            alert('Please select a month');
            return;
        }
        const [year, month] = monthValue.split('-');
        startDate = `${year}-${month}-01`;
        const lastDay = new Date(year, month, 0).getDate();
        endDate = `${year}-${month}-${String(lastDay).padStart(2, '0')}`;
    } else {
        startDate = document.getElementById('export_start_date').value;
        endDate = document.getElementById('export_end_date').value;

        if (!startDate || !endDate) {
            alert('Please select both start and end dates');
            return;
        }
    }

    emailContext = {
        type: 'export_tip',  // or 'export_daily'
        startDate: startDate,
        endDate: endDate
    };

    closeExportModal(); // Close the export modal first
    loadAdminUsers();
    document.getElementById('email-modal').classList.add('active');
}

function closeEmailModal() {
    document.getElementById('email-modal').classList.remove('active');

    // Reset form
    const checkboxes = document.querySelectorAll('input[name="user_email"]');
    checkboxes.forEach(cb => cb.checked = false);

    document.getElementById('additional_email_input').value = '';
    document.getElementById('additional_email_checkbox').checked = false;
    document.getElementById('additional_email_container').style.display = 'none';

    emailContext = {
        type: null,
        year: null,
        month: null,
        filename: null,
        startDate: null,
        endDate: null,
        employeeSlug: null
    };
}

function toggleAdditionalEmail() {
    const checkbox = document.getElementById('additional_email_checkbox');
    const container = document.getElementById('additional_email_container');

    if (checkbox.checked) {
        container.style.display = 'block';
    } else {
        container.style.display = 'none';
        document.getElementById('additional_email_input').value = '';
    }
}

function validateEmail(email) {
    const pattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    return pattern.test(email);
}

async function sendEmails(event) {
    event.preventDefault();

    const selectedEmails = [];
    const checkboxes = document.querySelectorAll('input[name="user_email"]:checked');
    checkboxes.forEach(cb => selectedEmails.push(cb.value));

    const additionalEmailCheckbox = document.getElementById('additional_email_checkbox');
    const additionalEmailInput = document.getElementById('additional_email_input');

    if (additionalEmailCheckbox.checked) {
        const additionalEmail = additionalEmailInput.value.trim();
        if (additionalEmail) {
            if (!validateEmail(additionalEmail)) {
                alert('Please enter a valid email address');
                return false;
            }
            selectedEmails.push(additionalEmail);
        }
    }

    if (selectedEmails.length === 0) {
        alert('Please select at least one recipient');
        return false;
    }

    let url;
    const formData = new FormData();

    selectedEmails.forEach(email => {
        formData.append('user_emails[]', email);
    });

    if (additionalEmailCheckbox.checked) {
        const additionalEmail = additionalEmailInput.value.trim();
        if (additionalEmail) {
            formData.append('additional_email', additionalEmail);
        }
    }

    // Determine URL based on context
    if (emailContext.type === 'saved_daily') {
        url = `/reports/daily-balance/email/${emailContext.year}/${emailContext.month}/${emailContext.filename}`;
    } else if (emailContext.type === 'saved_tip') {
        url = `/reports/tip-report/email/${emailContext.filename}`;
    } else if (emailContext.type === 'export_daily') {
        url = '/reports/daily-balance/email';
        formData.append('start_date', emailContext.startDate);
        formData.append('end_date', emailContext.endDate);
    } else if (emailContext.type === 'export_tip') {
        url = '/reports/tip-report/email';
        formData.append('start_date', emailContext.startDate);
        formData.append('end_date', emailContext.endDate);
    } else if (emailContext.type === 'employee_tip') {
        url = `/reports/tip-report/employee/${emailContext.employeeSlug}/email`;
        formData.append('start_date', emailContext.startDate);
        formData.append('end_date', emailContext.endDate);
    }

    try {
        const response = await fetch(url, {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (result.success) {
            alert(result.message);
            closeEmailModal();
        } else {
            alert(`Error: ${result.message}`);
        }
    } catch (error) {
        alert(`Failed to send emails: ${error.message}`);
    }

    return false;
}

// Handle clicks outside modal
window.addEventListener('click', function(event) {
    const emailModal = document.getElementById('email-modal');
    if (event.target === emailModal) {
        closeEmailModal();
    }
});
```

## Complete Example for Tip Reports

See `app/static/js/email_modal.js` for a reusable EmailModal class that can be instantiated for any report type:

```javascript
// In your template
<script src="/static/js/email_modal.js"></script>
<script>
const emailModal = new EmailModal('tips'); // or 'daily'

function openEmailModalForSaved(filename) {
    emailModal.openEmailModal({
        type: 'saved_tip',
        filename: filename
    });
}

function closeEmailModal() {
    emailModal.closeEmailModal();
}

function sendEmails(event) {
    return emailModal.sendEmails(event);
}
</script>
```

## Notes

1. **Report Type**: Set `REPORT_TYPE` to either `'daily'` or `'tips'` based on your page
2. **Context Type**: Use appropriate context type:
   - `'saved_daily'` - Saved daily balance report
   - `'saved_tip'` - Saved tip report
   - `'export_daily'` - Newly generated daily report
   - `'export_tip'` - Newly generated tip report
   - `'employee_tip'` - Employee-specific tip report

3. **URL Construction**: The URL is built based on context type and includes necessary path/query parameters

4. **Error Handling**: Always validate emails and show clear error messages

5. **User Experience**: Pre-check opted-in users and show loading states while fetching users
