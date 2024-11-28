document.getElementById("submit-btn").addEventListener("click", async () => {
    const jobDescription = document.getElementById("job-description").value;
    const extraPrompt = document.getElementById("extra-prompt").value;
    const resumeFile = document.getElementById("resume-upload").files[0];

    if (!resumeFile || !jobDescription) {
        alert("Please upload a resume and provide a job description.");
        return;
    }

    const formData = new FormData();
    formData.append("resume", resumeFile);
    formData.append("job_description", jobDescription);
    formData.append("extra_prompt", extraPrompt);

    const resultsDiv = document.getElementById("results");
    resultsDiv.innerHTML = "Processing...";

    try {
        const response = await fetch("http://127.0.0.1:8000/upload-resume/", {
            method: "POST",
            body: formData,
        });
        const result = await response.json();

        if (response.ok) {
            const analysis = result.structured_analysis;
            const metrics = result.metrics;

            resultsDiv.innerHTML = `
                <h3>Overall Score: ${metrics.overall_score} / 100</h3>
                <h3>Readability: ${metrics.readability_score} / 100</h3>
                <h3>ATS Compatibility: ${metrics.ats_score} / 100</h3>
            `;

            // Plotting the graph using Plotly
            const data = [{
                x: ["Overall Score", "Readability", "ATS Compatibility"],
                y: [metrics.overall_score, metrics.readability_score, metrics.ats_score],
                type: "bar"
            }];
            Plotly.newPlot('chart', data);
        } else {
            resultsDiv.innerHTML = `<p>Error: ${result.error}</p>`;
        }
    } catch (error) {
        resultsDiv.innerHTML = `<p>Error: ${error.message}</p>`;
    }
});
