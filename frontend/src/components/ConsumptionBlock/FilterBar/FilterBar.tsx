import TypeSelector from "./TypeSelector";
import TimeStepSelector from "./TimeStepSelector";
import DateSelector from "./DateSelector";
import styles from "./FilterBar.module.scss";
import { ValueType, StepOption } from "../../../constants/consumptionConstants";

interface FilterBarProps {
  displayType: ValueType["key"];
  onDisplayTypeChange: (key: ValueType["key"]) => void;
  step: StepOption["key"];
  onStepChange: (key: StepOption["key"]) => void;
  date: string;
  onDateChange: (date: string) => void;
}

export default function FilterBar({
  displayType,
  onDisplayTypeChange,
  step,
  onStepChange,
  date,
  onDateChange,
}: FilterBarProps) {
  return (
    <div className={styles.filterBar}>
      <TypeSelector value={displayType} onChange={onDisplayTypeChange} />
      <DateSelector value={date} onChange={onDateChange} />
      <TimeStepSelector value={step} onChange={onStepChange} />
    </div>
  );
}
