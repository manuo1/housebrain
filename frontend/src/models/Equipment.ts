interface EquipmentRaw {
  id: string;
  name: string;
  state: string | null;
  operational: boolean;
}

type EquipmentGroupsRaw = Record<string, EquipmentRaw[]>;

class Equipment {
  id: string;
  name: string;
  state: string | null;
  operational: boolean;
  interactionType: string;

  constructor({ id, name, state, operational }: EquipmentRaw, interactionType: string) {
    this.id = id;
    this.name = name;
    this.state = state;
    this.operational = operational;
    this.interactionType = interactionType;
  }
}

export default Equipment;
export type { EquipmentRaw, EquipmentGroupsRaw };
