import React, { useState, useEffect } from "react";
import { Link, useLocation } from "react-router-dom";
import Dropdown from "./Dropdown";
import styles from "./Navbar.module.scss";

export default function Navbar() {
  const location = useLocation();
  const [hidden, setHidden] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      const scrollTop = window.scrollY;
      const windowHeight = window.innerHeight;
      const fullHeight = document.documentElement.scrollHeight;

      // Si on est proche du bas, cacher la navbar
      if (scrollTop + windowHeight >= fullHeight - 100) {
        setHidden(true);
      } else {
        setHidden(false);
      }
    };

    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const consumptionLinks = [
    { to: "/teleinfo", icon: "⚡", text: "Téléinfo Live" },
    { to: "/consumption", icon: "📊", text: "Historique" },
  ];

  const heatingLinks = [
    { to: "/*", icon: "🚧", text: "Page en construction…" },
  ];

  return (
    <nav className={`${styles.navbar} ${hidden ? styles.hidden : ""}`}>
      <div className={styles.container}>
        {/* Logo */}
        <Link to="/" className={styles.logo}>
          <div className={styles.logoIcon}>🏠</div>
          <span>HouseBrain</span>
        </Link>

        {/* Navigation */}
        <div className={styles.navigation}>
          <Dropdown title="Consommation" icon="⚡" links={consumptionLinks} />
          <Dropdown title="Chauffage" icon="🔥" links={heatingLinks} />
        </div>
      </div>
    </nav>
  );
}
