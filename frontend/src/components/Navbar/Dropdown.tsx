import { useState, useRef, useEffect } from "react";
import { useLocation } from "react-router-dom";
import DropdownLink from "./DropdownLink";
import styles from "./Dropdown.module.scss";

interface NavLink {
  to: string;
  text: string;
}

interface DropdownProps {
  links: NavLink[];
}

export default function Dropdown({ links }: DropdownProps) {
  const [isOpen, setIsOpen] = useState<boolean>(false);
  const [isTouchDevice, setIsTouchDevice] = useState<boolean>(false);
  const location = useLocation();
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setIsTouchDevice("ontouchstart" in window || navigator.maxTouchPoints > 0);
  }, []);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  useEffect(() => {
    setIsOpen(false);
  }, [location]);

  const handleMouseEnter = () => { if (!isTouchDevice) setIsOpen(true); };
  const handleMouseLeave = () => { if (!isTouchDevice) setIsOpen(false); };

  return (
    <div
      className={styles.dropdown}
      ref={dropdownRef}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
    >
      <button
        className={`${styles.dropdownToggle} ${isOpen ? styles.active : ""}`}
        onClick={() => setIsOpen(!isOpen)}
        aria-label="Menu"
      >
        <svg className={styles.hamburger} viewBox="0 0 24 24" aria-hidden="true">
          <line x1="4" y1="7" x2="20" y2="7" />
          <line x1="4" y1="12" x2="20" y2="12" />
          <line x1="4" y1="17" x2="20" y2="17" />
        </svg>
      </button>

      <div className={`${styles.dropdownMenu} ${isOpen ? styles.show : ""}`}>
        {links.map((link, index) => (
          <DropdownLink key={index} to={link.to} text={link.text} />
        ))}
      </div>
    </div>
  );
}
