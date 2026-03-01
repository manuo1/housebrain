import styles from "./AreaRectangle.module.scss";

interface AreaRectangleProps {
  area_height: number;
  area_color: string;
}

const AreaRectangle = ({ area_height, area_color }: AreaRectangleProps) => {
  const style: React.CSSProperties = { height: `${area_height}%`, opacity: 0.5 };
  if (area_color) style.backgroundColor = area_color;

  return <div className={styles.areaRectangle} style={style} />;
};

export default AreaRectangle;
