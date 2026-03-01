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

  const consumptionLinks = [
    { to: "/teleinfo", icon: "⚡", text: "Téléinformation" },
    { to: "/consumption", icon: "📈", text: "Historique" },
  ];

  const heatingLinks = [
    { to: "/heating/schedule/", icon: "⚙️", text: "Planning" },
  ];

  return (
    <nav className={`${styles.navbar} ${hidden ? styles.hidden : ""}`}>
      <div className={styles.container}>
        <Link to="/" className={styles.logo}>
          <img src="/favicon.png" alt="Logo" className={styles.logoIcon} />
          <span>HouseBrain</span>
        </Link>
        <div className={styles.navigation}>
          <Dropdown title="Consommation" icon="⚡" links={consumptionLinks} />
          <Dropdown title="Chauffage" icon="🔥" links={heatingLinks} />
          <AuthDropdown />
        </div>
      </div>
    </nav>
  );
}
