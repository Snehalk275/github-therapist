import { useState } from "react";
import "./App.css";

function App() {
  const [username, setUsername] = useState("");
  const [mode, setMode] = useState("therapist");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

    const analyzeGithub = async (selectedMode = mode) => {
    if (!username.trim()) {
      setError("Enter a GitHub username first 😭");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await fetch(
      `http://127.0.0.1:8000/github/${username.trim()}/ai-report?mode=${selectedMode}`
      );

      const data = await response.json();

      if (!response.ok || data.error) {
        throw new Error(data.details || "Something went wrong");
      }

      setResult(data);
    } catch (err) {
      setError(
        "Couldn't analyze this GitHub profile. Make sure your backend is running."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">

      {/* HERO */}

      <section className="hero">

        <div className="badge">
          🧠 AI-POWERED GITHUB THERAPIST
        </div>

        <h1>
          Your GitHub
          <span> needs therapy.</span>
        </h1>

        <p>
          We inspect your projects, documentation and engineering signals
          and tell you what your GitHub is really saying about you.
        </p>

        <div className="search-box">

          <input
            type="text"
            placeholder="Enter GitHub username..."
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                analyzeGithub();
              }
            }}
          />

          <button onClick={analyzeGithub} disabled={loading}>
            {loading ? "Diagnosing..." : "Analyze →"}
          </button>

        </div>

        {error && (
          <div className="error">
            ⚠️ {error}
          </div>
        )}

        {/* MODES */}

        <div className="modes">

         <button
  className={mode === "therapist" ? "active" : ""}
  onClick={() => {
    setMode("therapist");
    if (username.trim()) {
      analyzeGithub("therapist");
    }
  }}
>
  🧠 Therapist
</button>
          <button
  className={mode === "roast" ? "active" : ""}
  onClick={() => {
    setMode("roast");
    if (username.trim()) {
      analyzeGithub("roast");
    }
  }}
>
  🔥 Roast Me
</button>
          <button
  className={mode === "recruiter" ? "active" : ""}
  onClick={() => {
    setMode("recruiter");
    if (username.trim()) {
      analyzeGithub("recruiter");
    }
  }}
>
  💼 Recruiter
</button>
        </div>

      </section>


      {/* RESULTS */}

      {result && (
        <section className="results">

          {/* SCORE */}

          <div className="score-card">

            <div>
              <p className="small-label">
                DEVELOPER HEALTH
              </p>

              <div className="score">
                {result.developer_health}
                <span>/100</span>
              </div>

              <h2>
                {result.diagnosis}
              </h2>

              <p>
                @{result.username}
              </p>
            </div>

            <div className="readiness">

              <p className="small-label">
                RECRUITER READINESS
              </p>

              <strong>
                {result.recruiter_readiness}/100
              </strong>

            </div>

          </div>


          {/* AI MESSAGE */}

          <div className="ai-card">

            <div className="card-title">
              🧠 Therapist says
            </div>

            <div className="ai-message">
              {result.ai_message}
            </div>

          </div>


          {/* STRENGTHS + WEAKNESSES */}

          <div className="grid">

            <div className="info-card strengths">

              <h3>🟢 What's working</h3>

              {result.github_analysis.strengths.length > 0 ? (
                <ul>
                  {result.github_analysis.strengths.map(
                    (item, index) => (
                      <li key={index}>{item}</li>
                    )
                  )}
                </ul>
              ) : (
                <p>No major strengths detected yet.</p>
              )}

            </div>


            <div className="info-card weaknesses">

              <h3>🔴 What's hurting you</h3>

              {result.github_analysis.weaknesses.length > 0 ? (
                <ul>
                  {result.github_analysis.weaknesses.map(
                    (item, index) => (
                      <li key={index}>{item}</li>
                    )
                  )}
                </ul>
              ) : (
                <p>No major weaknesses detected.</p>
              )}

            </div>

          </div>


          {/* PRESCRIPTION */}

          <div className="prescription">

            <div className="card-title">
              💊 Your prescription
            </div>

            <ul>

              {result.github_analysis.prescription.map(
                (item, index) => (
                  <li key={index}>
                    {item}
                  </li>
                )
              )}

            </ul>

          </div>


          {/* PROJECTS */}

          <div className="projects">

            <h2>
              📂 Project health
            </h2>

            <div className="project-grid">

              {result.github_analysis.projects.map(
                (project) => (

                  <div
                    className="project-card"
                    key={project.name}
                  >

                    <div className="project-header">

                      <strong>
                        {project.name}
                      </strong>

                      <span>
                        {project.project_score}/100
                      </span>

                    </div>

                    <p>
                      {project.description ||
                        "No description"}
                    </p>

                    <div className="project-tags">

                      <span>
                        {project.language ||
                          "Unknown language"}
                      </span>

                      <span>
                        {project.has_readme
                          ? "📖 README"
                          : "❌ README"}
                      </span>

                      <span>
                        {project.has_tests
                          ? "🧪 Tests"
                          : "❌ Tests"}
                      </span>

                    </div>

                  </div>

                )
              )}

            </div>

          </div>

        </section>
      )}

    </div>
  );
}

export default App;