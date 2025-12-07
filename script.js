document.addEventListener('DOMContentLoaded', () => {
    // Initial State: All sections are visible in the new scrollable layout
});

let selectedMode = 'balanced'; // Default

function startAssessment(mode) {
    selectedMode = mode;
    console.log(`Selected mode: ${mode}`);

    // Update Title based on Mode
    const assessmentSection = document.getElementById('detailed-assessment');
    const titleElement = assessmentSection.querySelector('h2');
    if (mode === 'fast') {
        titleElement.textContent = 'Fast Assessment';
    } else if (mode === 'balanced') {
        titleElement.textContent = 'Balanced Assessment';
    } else if (mode === 'detailed') {
        titleElement.textContent = 'Detailed Assessment';
    }

    // Scroll to Resume Section
    const resumeSection = document.getElementById('resume-section');
    resumeSection.scrollIntoView({ behavior: 'smooth' });
}

async function submitAssessment() {
    const dsaElement = document.querySelector('input[name="dsa"]:checked');
    const projectElement = document.getElementById('project-input');

    if (!dsaElement || !projectElement.value) {
        alert("Please complete the assessment questions.");
        return;
    }

    const requestData = {
        mode: selectedMode,
        dsa_skill: dsaElement.value,
        project_description: projectElement.value
    };

    try {
        // Show loading state (optional: add a spinner or change button text)
        const button = document.querySelector('button[onclick="submitAssessment()"]');
        const originalText = button.textContent;
        button.textContent = "Generating Report...";
        button.disabled = true;

        const response = await fetch('/api/assess', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        });

        if (!response.ok) {
            throw new Error(`API Error: ${response.statusText}`);
        }

        const data = await response.json();
        updateReportUI(data);

        // Scroll to report
        document.getElementById('report').scrollIntoView({ behavior: 'smooth' });

        // Reset button
        button.textContent = originalText;
        button.disabled = false;

    } catch (error) {
        console.error("Error submitting assessment:", error);
        alert("Failed to generate report. Please try again.");
    }
}

function updateReportUI(data) {
    // 1. Update Readiness Score
    const scoreElement = document.querySelector('.progress-circle span');
    if (scoreElement) scoreElement.textContent = `${data.readiness_score}%`;

    // 2. Update Strengths
    const strengthsList = document.querySelector('#report ul.text-green-700');
    if (strengthsList) {
        strengthsList.innerHTML = data.strengths.map(s => `<li>${s}</li>`).join('');
    }

    // 3. Update Gaps
    const gapsList = document.querySelector('#report ul.text-red-700');
    if (gapsList) {
        gapsList.innerHTML = data.gaps.map(g => `<li>${g}</li>`).join('');
    }

    // 4. Update Action Plan
    const actionPlanList = document.querySelector('#report ol');
    if (actionPlanList) {
        actionPlanList.innerHTML = data.action_plan.map(plan => `<li class="text-gray-700">${plan}</li>`).join('');
    }

    // 5. Update Job Recommendations
    const jobsContainer = document.querySelector('#report .space-y-4');
    if (jobsContainer && data.job_recommendations) {
        jobsContainer.innerHTML = data.job_recommendations.map(job => `
            <div class="flex justify-between items-center p-4 border rounded-lg">
                <div>
                    <h4 class="text-lg font-semibold text-blue-700">${job.role}</h4>
                    <p class="text-gray-600">${job.company} (${job.location}) - ${job.match} Match</p>
                </div>
                <a href="#" class="py-2 px-4 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700">View</a>
            </div>
        `).join('');
    }

    // 6. Update Email Draft
    const emailTextarea = document.getElementById('email-draft-output');
    if (emailTextarea) {
        emailTextarea.value = data.email_draft;
    }
}
