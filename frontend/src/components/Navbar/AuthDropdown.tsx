import { useState, useRef, useEffect, FormEvent } from "react";
import { useAuth } from "../../contexts/useAuth";
import styles from "./AuthDropdown.module.scss";

export default function AuthDropdown() {
  const { user, login, logout, loading } = useAuth();
  const [isOpen, setIsOpen] = useState<boolean>(false);
  const [username, setUsername] = useState<string>("");
  const [password, setPassword] = useState<string>("");
  const [error, setError] = useState<string>("");
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
        setError("");
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const toggleDropdown = () => {
    setIsOpen(!isOpen);
    setError("");
  };

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError("");
    setIsSubmitting(true);
    try {
      await login(username, password);
      setUsername("");
      setPassword("");
      setIsOpen(false);
    } catch {
      setError("Identifiants incorrects");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleLogout = () => {
    logout();
    setIsOpen(false);
  };

  if (loading) return null;

  return (
    <div className={styles.authDropdown} ref={dropdownRef}>
      <button
        className={`${styles.authToggle} ${isOpen ? styles.active : ""}`}
        onClick={toggleDropdown}
      >
        <span className={styles.icon}>👤</span>
        {user ? "✅" : "🚫"}
      </button>

      <div className={`${styles.authMenu} ${isOpen ? styles.show : ""}`}>
        {user ? (
          <div className={styles.userMenu}>
            <div className={styles.userInfo}>
              <span className={styles.userIcon}>👤</span>
              <span className={styles.userName}>{user.username}</span>
            </div>
            <button onClick={handleLogout} className={styles.logoutButton}>
              Déconnexion
            </button>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className={styles.loginForm}>
            <h3 className={styles.formTitle}>Connexion</h3>
            {error && <div className={styles.error}>{error}</div>}
            <div className={styles.formGroup}>
              <input
                type="text"
                placeholder="Nom d'utilisateur"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                disabled={isSubmitting}
                className={styles.input}
              />
            </div>
            <div className={styles.formGroup}>
              <input
                type="password"
                placeholder="Mot de passe"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                disabled={isSubmitting}
                className={styles.input}
              />
            </div>
            <button type="submit" disabled={isSubmitting} className={styles.submitButton}>
              {isSubmitting ? "Connexion..." : "Se connecter"}
            </button>
          </form>
        )}
      </div>
    </div>
  );
}
