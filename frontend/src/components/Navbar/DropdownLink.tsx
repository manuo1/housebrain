import { Link, useLocation } from "react-router-dom";
import styles from "./DropdownLink.module.scss";

interface DropdownLinkProps {
  to: string;
  icon?: string;
  text: string;
}

export default function DropdownLink({ to, icon, text }: DropdownLinkProps) {
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
