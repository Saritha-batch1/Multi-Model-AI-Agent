document.getElementById('uploadForm').addEventListener('submit', async function(e) {
    e.preventDefault();

    // UI State Management
    const loader = document.getElementById('loader');
    const resultsSection = document.getElementById('resultsSection');
    const btn = document.getElementById('analyzeBtn');

    loader.classList.remove('hidden');
    resultsSection.classList.add('hidden');
    btn.disabled = true;

    // Prepare Data
    const formData = new FormData();
    const fileField = document.querySelector('input[type="file"]');
    const ageField = document.querySelector('input[name="age"]');
    const genderField = document.querySelector('select[name="gender"]');

    formData.append('report', fileField.files[0]);
    formData.append('age', ageField.value);
    formData.append('gender', genderField.value);

    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (response.ok) {
            displayResults(data);
        } else {
            alert('Error: ' + data.error);
        }

    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred during analysis.');
    } finally {
        loader.classList.add('hidden');
        btn.disabled = false;
    }
});

function displayResults(data) {
    const resultsSection = document.getElementById('resultsSection');
    const tableBody = document.querySelector('#analysisTable tbody');
    const riskList = document.getElementById('riskList');
    const recList = document.getElementById('recommendationList');
    const disclaimer = document.getElementById('disclaimerText');

    // Clear previous results
    tableBody.innerHTML = '';
    riskList.innerHTML = '';
    recList.innerHTML = '';

    // 1. Populate Analysis Table (Model 1 Output)
    data.analysis.forEach(item => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${item.parameter}</td>
            <td>${item.value} ${item.unit}</td>
            <td>${item.range}</td>
            <td class="status-${item.status}">${item.status}</td>
        `;
        tableBody.appendChild(row);
    });

    // 2. Populate Risks (Model 2 Output)
    if (data.risks.length > 0) {
        data.risks.forEach(risk => {
            const li = document.createElement('li');
            li.textContent = risk;
            li.style.color = "#c0392b"; // Red text for risks
            riskList.appendChild(li);
        });
    } else {
        riskList.innerHTML = '<li>No significant patterns detected.</li>';
    }

    // 3. Populate Recommendations [cite: 29]
    data.recommendations.forEach(rec => {
        const li = document.createElement('li');
        li.textContent = rec;
        recList.appendChild(li);
    });

    // 4. Set Disclaimer [cite: 31]
    disclaimer.textContent = data.disclaimer;

    // Show Results
    resultsSection.classList.remove('hidden');
    
    // Smooth scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}