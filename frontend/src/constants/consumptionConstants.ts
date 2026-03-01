export interface StepOption {
  key: number;
  label: string;
}

export interface ValueType {
  key: "wh" | "average_watt" | "euros";
  label: string;
}

export const STEP_OPTIONS: StepOption[] = [
  { key: 1, label: "1 min" },
  { key: 30, label: "30 min" },
  { key: 60, label: "1 h" },
];

export const VALUE_TYPES: ValueType[] = [
  { key: "wh", label: "Consommation (Wh)" },
  { key: "average_watt", label: "Puissance Moyenne (w)" },
  { key: "euros", label: "Coût (€)" },
];
