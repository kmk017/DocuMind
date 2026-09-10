import { useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";
import "./Navbar.css";

export default function Navbar({ inWorkspace = false, onNavigateBack }) {
  const [isScrolled, setIsScrolled] = useState(false);

  const { user, logout } = useAuth();

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 8);
    };

    window.addEventListener(
      "scroll",
      handleScroll,
      { passive: true }
    );

    return () => {
      window.removeEventListener(
        "scroll",
        handleScroll
      );
    };
  }, []);

  const avatarLetter =
    user?.email?.charAt(0)?.toUpperCase() || "D";

  const handleDocumentsClick = (event) => {
    if (onNavigateBack) {
      event.preventDefault();
      onNavigateBack();
    }
  };

  return (
    <header
      className={`navbar ${
        isScrolled ? "navbar--scrolled" : ""
      }`}
    >
      <div className="navbar__inner">

        <span className="navbar__brand">
          DocuMind
        </span>

        <nav
          className="navbar__links"
          aria-label="Primary"
        >
          {/* "Workspace" scrolls to the upload area on the dashboard.
              It has no valid target while inside a document workspace,
              so it's hidden there rather than left pointing at nothing. */}
          {!inWorkspace && (
            <a
              href="#upload"
              className="navbar__link"
            >
              Workspace
            </a>
          )}

          <a
            href="#documents"
            className="navbar__link"
            onClick={handleDocumentsClick}
          >
            Documents
          </a>
        </nav>

        <div className="navbar__profile">

          <span
            className="navbar__email"
            title={user?.email}
          >
            {user?.email}
          </span>

          <span className="navbar__avatar">
            {avatarLetter}
          </span>

          <button
            type="button"
            className="navbar__logout"
            onClick={logout}
          >
            Logout
          </button>

        </div>

      </div>
    </header>
  );
}