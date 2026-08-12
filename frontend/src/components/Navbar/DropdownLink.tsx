import { Link, useLocation } from "react-router-dom";
import styles from "./DropdownLink.module.scss";

interface DropdownLinkProps {
  to: string;
  text: string;
}

export default function DropdownLink({ to, text }: DropdownLinkProps) {
  const location = useLocation();
  const isActive = location.pathname === to;

  return (
    <Link
      to={to}
      className={`${styles.dropdownLink} ${isActive ? styles.active : ""}`}
    >
      {text}
    </Link>
  );
}
