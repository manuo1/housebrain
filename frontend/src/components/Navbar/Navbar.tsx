import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import Dropdown from "./Dropdown";
import AuthDropdown from "./AuthDropdown";
import styles from "./Navbar.module.scss";

export default function Navbar() {
  const [hidden, setHidden] = useState<boolean>(false);
  const [lastScrollY, setLastScrollY] = useState<number>(0);

  useEffect(() => {
    const handleScroll = () => {
      const scrollTop = window.scrollY;
      const windowHeight = window.innerHeight;
      const fullHeight = document.documentElement.scrollHeight;
      const isScrollable = fullHeight > windowHeight + 1;

      if (!isScrollable) {
        setHidden(false);
        return;
      }

      if (scrollTop + windowHeight >= fullHeight - 1) {
        setHidden(true);
      } else if (scrollTop < lastScrollY) {
        setHidden(false);
      } else if (scrollTop > lastScrollY && scrollTop > 100) {
        setHidden(true);
      }

      setLastScrollY(scrollTop);
    };

    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => window.removeEventListener("scroll", handleScroll);
  }, [lastScrollY]);

  const menuLinks = [
    { to: "/teleinfo", text: "Téléinformation" },
    { to: "/consumption", text: "Suivi consommation" },
    { to: "/heating/schedule", text: "Chauffages" },
  ];

  return (
    <nav className={`${styles.navbar} ${hidden ? styles.hidden : ""}`}>
      <div className={styles.container}>
        <Link to="/" className={styles.logo}>
          <img src="/favicon.png" alt="Logo" className={styles.logoIcon} />
          <span>HouseBrain</span>
        </Link>
        <div className={styles.navigation}>
          <Dropdown links={menuLinks} />
          <AuthDropdown />
        </div>
      </div>
    </nav>
  );
}
