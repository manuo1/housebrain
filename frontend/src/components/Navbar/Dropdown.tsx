import { useState, useRef, useEffect } from "react";
import { useLocation } from "react-router-dom";
import DropdownLink from "./DropdownLink";
import styles from "./Dropdown.module.scss";

interface NavLink {
  to: string;
  icon?: string;
  text: string;
}

interface DropdownProps {
  title: string;
  links: NavLink[];
  icon?: string;
}

export default function Dropdown({ title, links, icon }: DropdownProps) {
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
      >
        {icon && <span className={styles.titleIcon}>{icon}</span>}
        <span className={styles.title}>{title}</span>
        <span className={styles.arrow}>▾</span>
      </button>

      <div className={`${styles.dropdownMenu} ${isOpen ? styles.show : ""}`}>
        {links.map((link, index) => (
          <DropdownLink key={index} to={link.to} icon={link.icon} text={link.text} />
        ))}
      </div>
    </div>
  );
}
