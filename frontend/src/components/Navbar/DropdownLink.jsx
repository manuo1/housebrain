import React from "react";
import { Link, useLocation } from "react-router-dom";
import styles from "./DropdownLink.module.scss";

export default function DropdownLink({ to, icon, text }) {
  const location = useLocation();
  const isActive = location.pathname === to;

  return (
    <Link
      to={to}
      className={`${styles.dropdownLink} ${isActive ? styles.active : ""}`}
    >
      {icon && <span className={styles.icon}>{icon}</span>}
      <span className={styles.text}>{text}</span>
    </Link>
  );
}
