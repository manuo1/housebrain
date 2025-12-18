import React, { useState, useRef, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import DropdownLink from './DropdownLink';
import styles from './Dropdown.module.scss';

export default function Dropdown({ title, links, icon }) {
  const [isOpen, setIsOpen] = useState(false);
  const [isTouchDevice, setIsTouchDevice] = useState(false);
  const location = useLocation();
  const dropdownRef = useRef(null);

  useEffect(() => {
    setIsTouchDevice('ontouchstart' in window || navigator.maxTouchPoints > 0);
  }, []);

  useEffect(() => {
    function handleClickOutside(event) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    }

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  useEffect(() => {
    setIsOpen(false);
  }, [location]);

  const toggleDropdown = () => {
    setIsOpen(!isOpen);
  };

  const handleMouseEnter = () => {
    if (!isTouchDevice) {
      setIsOpen(true);
    }
  };

  const handleMouseLeave = () => {
    if (!isTouchDevice) {
      setIsOpen(false);
    }
  };

  return (
    <div
      className={styles.dropdown}
      ref={dropdownRef}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
    >
      <button
        className={`${styles.dropdownToggle} ${isOpen ? styles.active : ''}`}
        onClick={toggleDropdown}
      >
        {icon && <span className={styles.titleIcon}>{icon}</span>}
        <span className={styles.title}>{title}</span>
        <span className={styles.arrow}>▾</span>
      </button>

      <div className={`${styles.dropdownMenu} ${isOpen ? styles.show : ''}`}>
        {links.map((link, index) => (
          <DropdownLink
            key={index}
            to={link.to}
            icon={link.icon}
            text={link.text}
          />
        ))}
      </div>
    </div>
  );
}
