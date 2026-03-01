import { useState, useRef, useEffect } from "react";
import styles from "./HoverRectangle.module.scss";

interface Tooltip {
  title: string;
  content: string[];
}

interface HoverRectangleProps {
  tooltip: Tooltip;
}

const HoverRectangle = ({ tooltip }: HoverRectangleProps) => {
  const [isHovered, setIsHovered] = useState<boolean>(false);
  const [side, setSide] = useState<"right" | "left">("right");
  const hoverRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!hoverRef.current) return;

    const hoverRect = hoverRef.current.getBoundingClientRect();
    const graphContainer = hoverRef.current.closest('[class*="chartArea"]');
    if (!graphContainer) return;

    const graphRect = graphContainer.getBoundingClientRect();
    const pointX = hoverRect.left - graphRect.left + hoverRect.width / 2;
    setSide(pointX < graphRect.width / 2 ? "right" : "left");
  }, []);

  return (
    <div
      ref={hoverRef}
      className={styles.hoverRectangle}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {isHovered && (
        <div className={`${styles.tooltip} ${styles[side]}`}>
          <div className={styles.tooltipTitle}>{tooltip.title}</div>
          {tooltip.content.map((line, index) => (
            <div key={index} className={styles.tooltipLine}>{line}</div>
          ))}
        </div>
      )}
    </div>
  );
};

export default HoverRectangle;
