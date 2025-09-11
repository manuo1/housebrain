import React from "react";
import { Link } from "react-router-dom";
import styles from "./NotFound.module.scss";

export default function NotFound() {
  return (
    <div className={styles.notFound}>
      <h1>404</h1>
      <p>Oops ! La page que vous recherchez n'existe pas.</p>
      <Link to="/">Retour à l'accueil</Link>
    </div>
  );
}
