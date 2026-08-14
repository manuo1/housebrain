interface EquipmentRaw {
  id: string;
  name: string;
  state: string | null;
  status_level: string;
  operational: boolean;
}

type EquipmentGroupsRaw = Record<string, EquipmentRaw[]>;

class Equipment {
  id: string;
  name: string;
  state: string | null;
  statusLevel: string;
  operational: boolean;
  interactionType: string;

  constructor(
    { id, name, state, status_level, operational }: EquipmentRaw,
    interactionType: string
  ) {
    this.id = id;
    this.name = name;
    this.state = state;
    this.statusLevel = status_level;
    this.operational = operational;
    this.interactionType = interactionType;
  }
}

export default Equipment;
export type { EquipmentRaw, EquipmentGroupsRaw };
