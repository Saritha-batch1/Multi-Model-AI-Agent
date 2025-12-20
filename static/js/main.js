// Complete JavaScript for Health Diagnostics App
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 AI Health Diagnostics System Loaded');
    
    // ========== FILE UPLOAD FUNCTIONALITY ==========
    const fileInput = document.getElementById('fileInput');
    const fileNameDisplay = document.querySelector('.file-name');
    
    if (fileInput && fileNameDisplay) {
        // Click label to trigger file input
        document.querySelector('.custom-file-upload').addEventListener('click', function() {
            fileInput.click();
        });
        
        // Update file name when selected
        fileInput.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                const file = this.files[0];
                const fileName = file.name;
                const fileSize = (file.size / (1024 * 1024)).toFixed(2); // MB
                
                // Update display
                fileNameDisplay.innerHTML = `
                    <i class="fas fa-file-medical" style="color: #4361ee;"></i>
                    <strong>${fileName}</strong>
                    <span style="color: #6c757d; font-size: 0.9em;"> (${fileSize} MB)</span>
                `;
                fileNameDisplay.style.color = '#155724';
                
                // Validate file type
                const allowedTypes = ['application/pdf', 'image/jpeg', 'image/png', 'image/jpg'];
                if (!allowedTypes.includes(file.type)) {
                    alert('⚠️ Please upload only PDF or image files (JPEG, PNG)');
                    this.value = '';
                    fileNameDisplay.innerHTML = 'Invalid file type. Please select PDF or image.';
                    fileNameDisplay.style.color = '#dc3545';
                }
            } else {
                fileNameDisplay.innerHTML = 'No file chosen';
                fileNameDisplay.style.color = '#6c757d';
            }
        });
    }
    
    // ========== FORM SUBMISSION ==========
    const uploadForm = document.getElementById('uploadForm');
    const analyzeBtn = document.querySelector('.analyze-btn');
    
    if (uploadForm && analyzeBtn) {
        uploadForm.addEventListener('submit', function(e) {
            // Validate file
            if (fileInput && fileInput.files.length === 0) {
                e.preventDefault();
                showNotification('Please select a blood report file first!', 'error');
                return false;
            }
            
            // Validate file size (max 10MB)
            const file = fileInput.files[0];
            if (file && file.size > 10 * 1024 * 1024) {
                e.preventDefault();
                showNotification('File size exceeds 10MB limit!', 'error');
                return false;
            }
            
            // Show loading state
            const originalText = analyzeBtn.innerHTML;
            analyzeBtn.innerHTML = `
                <div class="spinner" style="width: 20px; height: 20px; border: 3px solid #f3f3f3; 
                    border-top: 3px solid white; border-radius: 50%; animation: spin 1s linear infinite;"></div>
                Analyzing Report...
            `;
            analyzeBtn.disabled = true;
            analyzeBtn.style.opacity = '0.8';
            
            // Show processing message
            showNotification('Processing your blood report with AI models...', 'info');
            
            // Form will submit normally after short delay
            setTimeout(() => {
                // Keep disabled until form submits
            }, 1000);
        });
    }
    
    // ========== INPUT VALIDATIONS ==========
    const ageInput = document.querySelector('input[name="age"]');
    if (ageInput) {
        ageInput.addEventListener('input', function() {
            let value = this.value;
            // Remove non-numeric characters
            value = value.replace(/[^\d]/g, '');
            
            // Limit to 3 digits and reasonable age
            if (value > 120) value = 120;
            if (value < 0) value = 0;
            
            this.value = value;
            
            // Show age group hint
            const hint = document.getElementById('ageHint');
            if (!hint) {
                const hintDiv = document.createElement('div');
                hintDiv.id = 'ageHint';
                hintDiv.style.fontSize = '0.8rem';
                hintDiv.style.color = '#6c757d';
                hintDiv.style.marginTop = '5px';
                ageInput.parentNode.appendChild(hintDiv);
            }
            
            if (value >= 60) {
                document.getElementById('ageHint').textContent = 'Senior age group - enhanced monitoring';
            } else if (value >= 18) {
                document.getElementById('ageHint').textContent = 'Adult age group';
            } else if (value > 0) {
                document.getElementById('ageHint').textContent = 'Pediatric age group';
            } else {
                document.getElementById('ageHint').textContent = '';
            }
        });
    }
    
    const genderSelect = document.querySelector('select[name="gender"]');
    if (genderSelect) {
        genderSelect.addEventListener('change', function() {
            // Update gender-specific reference ranges hint
            console.log('Gender selected:', this.value);
        });
    }
    
    // ========== ANIMATIONS FOR FEATURE CARDS ==========
    const featureCards = document.querySelectorAll('.feature-card');
    featureCards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
        card.classList.add('fade-in');
        
        // Add hover effect
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-10px) scale(1.02)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });
    
    // ========== RESULTS PAGE FUNCTIONALITY ==========
    // Download Report
    const downloadBtn = document.querySelector('.download-btn');
    if (downloadBtn) {
        downloadBtn.addEventListener('click', function() {
            const reportContent = generateReportContent();
            const blob = new Blob([reportContent], { type: 'text/plain' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'Health_Report_' + new Date().toISOString().split('T')[0] + '.txt';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            
            showNotification('Report downloaded successfully!', 'success');
        });
    }
    
    // Print Results
    const printBtn = document.querySelector('.print-btn');
    if (printBtn) {
        printBtn.addEventListener('click', function() {
            window.print();
            showNotification('Printing health report...', 'info');
        });
    }
    
    // ========== HELPER FUNCTIONS ==========
    function showNotification(message, type = 'info') {
        // Remove existing notification
        const existingNotification = document.querySelector('.notification');
        if (existingNotification) {
            existingNotification.remove();
        }
        
        // Create notification
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <i class="fas fa-${type === 'error' ? 'exclamation-circle' : type === 'success' ? 'check-circle' : 'info-circle'}"></i>
            ${message}
        `;
        
        // Style notification
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 25px;
            background: ${type === 'error' ? '#dc3545' : type === 'success' ? '#28a745' : '#17a2b8'};
            color: white;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            z-index: 1000;
            display: flex;
            align-items: center;
            gap: 10px;
            animation: slideIn 0.3s ease-out;
        `;
        
        // Add animation
        const style = document.createElement('style');
        style.textContent = `
            @keyframes slideIn {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
            @keyframes slideOut {
                from { transform: translateX(0); opacity: 1; }
                to { transform: translateX(100%); opacity: 0; }
            }
        `;
        document.head.appendChild(style);
        
        document.body.appendChild(notification);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease-out forwards';
            setTimeout(() => notification.remove(), 300);
        }, 5000);
    }
    
    function generateReportContent() {
        const reportTitle = 'AI HEALTH DIAGNOSTICS REPORT\n';
        const separator = '='.repeat(50) + '\n\n';
        
        // Get patient info
        const patientInfo = `PATIENT INFORMATION:\n`;
        const timestamp = document.querySelector('p')?.textContent || new Date().toLocaleString();
        
        // Get parameters
        let parameters = 'BLOOD PARAMETERS:\n';
        const paramCards = document.querySelectorAll('.parameter-card');
        paramCards.forEach(card => {
            const name = card.querySelector('.parameter-name').textContent.trim();
            const value = card.querySelector('.parameter-value').textContent.trim();
            const unit = card.querySelector('.parameter-unit').textContent.trim();
            parameters += `• ${name}: ${value} ${unit}\n`;
        });
        
        // Get findings
        let findings = '\nAI ANALYSIS FINDINGS:\n';
        const findingItems = document.querySelectorAll('.finding-item');
        findingItems.forEach(item => {
            const text = item.querySelector('.finding-text').textContent.trim();
            findings += `• ${text}\n`;
        });
        
        // Get score
        const score = document.querySelector('.score-value')?.textContent || 'N/A';
        const scoreSection = `\nHEALTH SCORE: ${score}\n`;
        
        // Get recommendations
        let recommendations = '\nRECOMMENDATIONS:\n';
        const recCards = document.querySelectorAll('.recommendation-card');
        recCards.forEach(card => {
            const text = card.querySelector('div p').textContent.trim();
            recommendations += `• ${text}\n`;
        });
        
        const disclaimer = '\n\nDISCLAIMER:\n';
        const disclaimerText = 'This AI analysis is for informational purposes only. Consult a healthcare professional for medical advice.';
        
        return reportTitle + separator + patientInfo + separator + parameters + 
               separator + findings + separator + scoreSection + separator + 
               recommendations + separator + disclaimer + disclaimerText;
    }
    
    // ========== PAGE LOAD EFFECTS ==========
    // Add fade-in effect to all sections
    const sections = document.querySelectorAll('section, .feature-card, .parameter-card');
    sections.forEach((section, index) => {
        section.style.opacity = '0';
        section.style.transform = 'translateY(20px)';
        section.style.transition = 'all 0.6s ease-out';
        
        setTimeout(() => {
            section.style.opacity = '1';
            section.style.transform = 'translateY(0)';
        }, index * 100);
    });
    
    // ========== REAL-TIME VALIDATION ==========
    const inputs = document.querySelectorAll('input, select');
    inputs.forEach(input => {
        input.addEventListener('focus', function() {
            this.style.borderColor = '#4361ee';
            this.style.boxShadow = '0 0 0 3px rgba(67, 97, 238, 0.1)';
        });
        
        input.addEventListener('blur', function() {
            this.style.borderColor = '#e0e0e0';
            this.style.boxShadow = 'none';
        });
    });
    
    console.log('✅ All JavaScript functionality loaded successfully');
});