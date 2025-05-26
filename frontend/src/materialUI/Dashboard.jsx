import React from "react";

function DashboardLink() {
  return (
    <div className="background">
    <div style={{ padding: "2rem", maxWidth: "800px", margin: "0 auto", fontFamily: "Arial, sans-serif", lineHeight: "1.6" }}>
      <h1>Welcome to the Company Dashboard!</h1>
      <p>
        We are absolutely thrilled to welcome you to our organization’s central hub! This dashboard has been thoughtfully designed to provide you with
        seamless access to the tools, resources, and information you need to thrive in your role. Whether you're here to manage tasks, monitor
        performance, review reports, or simply stay up-to-date with the latest updates, you're in the right place.
      </p>
      <p>
        As part of our commitment to transparency, productivity, and collaboration, this platform serves as your one-stop destination for all
        internal operations. From personalized insights to team performance tracking, we’ve built this with your success in mind.
      </p>
      <p>
        Please take a moment to explore, familiarize yourself with the features, and don’t hesitate to reach out to your department lead if you have
        any questions. We're excited to have you on board, and we look forward to achieving great things together!
      </p>
      <p>
        Once you're ready, click the link below to access your dashboard and get started.
      </p>
      <div style={{ marginTop: "1.5rem" }}>
        <a href="http://localhost:8000/Ontech/dashboard" style={{ fontSize: "1.1rem", color: "#1e90ff", textDecoration: "none", fontWeight: "bold" }}>
          ➤ Go to Dashboard
        </a>
      </div>
    </div>
    </div>
  );
}

export default DashboardLink;
