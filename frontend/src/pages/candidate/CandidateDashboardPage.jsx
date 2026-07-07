import { Link } from "react-router-dom";

import { useAuth } from "../../auth/useAuth";

const WORKFLOWS = [
  {
    eyebrow: "PROFILE",
    title: "Keep your candidate profile current",
    description:
      "Update skills, education, project experience, preferred location, role type, and domain interests.",
    link: "/candidate/profile",
    action: "Edit profile",
  },
  {
    eyebrow: "DISCOVERY",
    title: "Search open jobs",
    description:
      "Filter current opportunities by skill, location, and experience level before applying.",
    link: "/candidate/jobs",
    action: "Search jobs",
  },
  {
    eyebrow: "MATCHING",
    title: "Use explainable job matching",
    description:
      "Describe the opportunity you want and review ranked jobs with match scores and explanations.",
    link: "/candidate/matching",
    action: "Match jobs",
  },
  {
    eyebrow: "APPLICATIONS",
    title: "Track your applications",
    description:
      "Review submitted applications and follow their current hiring status.",
    link: "/candidate/applications",
    action: "View applications",
  },
];

export default function CandidateDashboardPage() {
  const { user } = useAuth();

  return (
    <section className="page-container">
      <header className="page-header dashboard-header">
        <div>
          <p className="eyebrow">CANDIDATE WORKSPACE</p>
          <h1>Candidate dashboard</h1>
          <p>
            Signed in as {user.email}. Build your profile, discover
            opportunities, use explainable matching, and track every
            application.
          </p>
        </div>
      </header>

      <div className="workflow-grid">
        {WORKFLOWS.map((workflow) => (
          <article className="workflow-card card" key={workflow.link}>
            <p className="eyebrow">{workflow.eyebrow}</p>
            <h2>{workflow.title}</h2>
            <p>{workflow.description}</p>

            <Link className="text-link" to={workflow.link}>
              {workflow.action}
              <span aria-hidden="true"> →</span>
            </Link>
          </article>
        ))}
      </div>
    </section>
  );
}