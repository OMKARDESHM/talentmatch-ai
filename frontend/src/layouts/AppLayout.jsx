import { NavLink, Outlet } from "react-router-dom";

import { useAuth } from "../auth/useAuth";

function getNavigation(role) {
  if (role === "admin") {
    return [
      {
        label: "Dashboard",
        to: "/admin",
        end: true,
      },
    ];
  }

  return [
    {
      label: "Dashboard",
      to: "/candidate",
      end: true,
    },
  ];
}

export default function AppLayout() {
  const { user, logout } = useAuth();
  const navigation = getNavigation(user.role);

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div>
          <div className="sidebar-brand">
            <div className="brand-mark" aria-hidden="true">
              TM
            </div>
            <div>
              <strong>TalentMatch AI</strong>
              <span>Job matching workspace</span>
            </div>
          </div>

          <nav
            className="sidebar-navigation"
            aria-label="Primary navigation"
          >
            {navigation.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.end}
                className={({ isActive }) =>
                  isActive
                    ? "navigation-link active"
                    : "navigation-link"
                }
              >
                {item.label}
              </NavLink>
            ))}
          </nav>
        </div>

        <div className="sidebar-footer">
          <div className="user-summary">
            <span className="role-badge">{user.role}</span>
            <span>{user.email}</span>
          </div>

          <button
            className="secondary-button full-width"
            type="button"
            onClick={logout}
          >
            Sign out
          </button>
        </div>
      </aside>

      <main className="app-content">
        <Outlet />
      </main>
    </div>
  );
}