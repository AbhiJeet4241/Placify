document.addEventListener('DOMContentLoaded', () => {
    // Initial State: All sections are visible in the new scrollable layout
});

function startAssessment(mode) {
    // Visual Feedback: Highlight the selected mode (optional, can be enhanced later)
    console.log(`Selected mode: ${mode}`);

    // Update Title based on Mode (optional, if we want to reflect it in the assessment section)
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
