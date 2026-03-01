import styles from "./LineRectangle.module.scss";

interface LineRectangleProps {
  line_height: number;
  area_height: number;
  line_color: string;
}

const LineRectangle = ({ line_height, area_height, line_color }: LineRectangleProps) => {
  const borderStyle = `2px solid ${line_color}`;
  const lineStyle: React.CSSProperties = {};
  const absLineHeight = Math.abs(line_height);

  if (line_height > 0) {
    lineStyle.height = `${absLineHeight}%`;
    lineStyle.bottom = `${area_height}%`;
    lineStyle.borderBottom = borderStyle;
    lineStyle.borderRight = borderStyle;
  } else if (line_height === 0) {
    lineStyle.height = `${area_height}%`;
    lineStyle.bottom = "0";
    lineStyle.borderTop = borderStyle;
  } else {
    lineStyle.height = `${absLineHeight}%`;
    lineStyle.bottom = `${area_height - absLineHeight}%`;
    lineStyle.borderTop = borderStyle;
    lineStyle.borderRight = borderStyle;
  }

  return <div className={styles.lineRectangle} style={lineStyle} />;
};

export default LineRectangle;
