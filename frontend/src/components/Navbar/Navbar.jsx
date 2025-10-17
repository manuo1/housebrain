import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import Dropdown from './Dropdown';
import styles from './Navbar.module.scss';

export default function Navbar() {
  const [hidden, setHidden] = useState(false);
  const [lastScrollY, setLastScrollY] = useState(0);

  useEffect(() => {
    const handleScroll = () => {
      const scrollTop = window.scrollY;
      const windowHeight = window.innerHeight;
      const fullHeight = document.documentElement.scrollHeight;

      // Si on est proche du bas de la page, cacher la navbar
      if (scrollTop + windowHeight >= fullHeight - 100) {
        setHidden(true);
      }
      // Sinon, gérer le comportement normal de scroll
      else if (scrollTop < lastScrollY) {
        // Scroll vers le haut -> toujours montrer
        setHidden(false);
      } else if (scrollTop > lastScrollY && scrollTop > 100) {
        // Scroll vers le bas (après 100px) -> cacher
        setHidden(true);
      }

      setLastScrollY(scrollTop);
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, [lastScrollY]);

  const consumptionLinks = [
    { to: '/teleinfo', icon: '⚡', text: 'Téléinfo Live' },
    { to: '/consumption', icon: '📊', text: 'Historique' },
  ];

  const heatingLinks = [
    { to: '/*', icon: '🚧', text: 'Page en construction…' },
  ];

  return (
    <nav className={`${styles.navbar} ${hidden ? styles.hidden : ''}`}>
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
