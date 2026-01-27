"""
Board data loader for Village buildings, Offerings, and Raid locations
"""
import json
from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from pathlib import Path


@dataclass
class VillageBuilding:
    """Represents a village building where workers can be placed"""
    id: str
    name: str
    worker_slots: int
    action: Dict[str, Any]
    worker_requirement: Optional[List[str]]
    
    def allows_worker_color(self, color: str) -> bool:
        """Check if a worker color can be placed here"""
        if self.worker_requirement is None:
            return True
        return color in self.worker_requirement
    
    def __str__(self) -> str:
        req = f" ({'/'.join(self.worker_requirement)} only)" if self.worker_requirement else ""
        return f"{self.name}{req}"


@dataclass
class OfferingTile:
    """Represents an offering tile"""
    id: str
    requirements: Dict[str, int]
    vp: int
    
    def get_cost_string(self) -> str:
        """Get a readable cost string"""
        costs = []
        for resource, amount in self.requirements.items():
            costs.append(f"{amount} {resource}")
        return ", ".join(costs)
    
    def __str__(self) -> str:
        return f"Offering: {self.get_cost_string()} → {self.vp} VP"


@dataclass
class RaidSublocation:
    """Represents a sublocation within a raid"""
    id: str
    plunder: int
    worker_on_spot: str
    
    def __str__(self) -> str:
        return f"{self.id}: {self.plunder} plunder ({self.worker_on_spot} worker)"


@dataclass
class VPTier:
    """Represents a VP tier based on strength achieved"""
    min_strength: int
    vp: int


@dataclass
class RaidLocation:
    """Represents a raid location"""
    id: str
    name: str
    type: str  # harbor, outpost, monastery, fortress
    requirements: Dict[str, Any]
    vp_tiers: List[VPTier]
    dice_added: int
    sublocations: List[RaidSublocation]
    
    def get_vp_for_strength(self, strength: int) -> int:
        """Calculate VP earned for a given strength"""
        # VP tiers are sorted descending by min_strength in JSON
        for tier in self.vp_tiers:
            if strength >= tier.min_strength:
                return tier.vp
        return 0
    
    def allows_worker_color(self, color: str) -> bool:
        """Check if a worker color can raid here"""
        return color in self.requirements["worker_colors"]
    
    def __str__(self) -> str:
        return f"{self.name} ({self.type.title()}, {len(self.sublocations)} spots)"


class BoardDatabase:
    """Manages all board data: buildings, offerings, raids"""
    
    def __init__(self, data_dir: str = None):
        """Load all board data from JSON files"""
        if data_dir is None:
            # Default path relative to this file
            data_dir = Path(__file__).parent.parent / "data"
        else:
            data_dir = Path(data_dir)
        
        # Load village buildings
        with open(data_dir / "board_village.json", 'r', encoding='utf-8') as f:
            village_data = json.load(f)
        
        self.buildings: List[VillageBuilding] = []
        for bldg_data in village_data["buildings"]:
            building = VillageBuilding(
                id=bldg_data["id"],
                name=bldg_data["name"],
                worker_slots=bldg_data["worker_slots"],
                action=bldg_data["action"],
                worker_requirement=bldg_data.get("worker_requirement")
            )
            self.buildings.append(building)
        
        # Load offerings
        with open(data_dir / "offerings.json", 'r', encoding='utf-8') as f:
            offerings_data = json.load(f)
        
        self.offerings: List[OfferingTile] = []
        for offer_data in offerings_data["offerings"]:
            offering = OfferingTile(
                id=offer_data["id"],
                requirements=offer_data["requirements"],
                vp=offer_data["vp"]
            )
            self.offerings.append(offering)
        
        # Load raid locations
        with open(data_dir / "board_raids.json", 'r', encoding='utf-8') as f:
            raids_data = json.load(f)
        
        self.raids: List[RaidLocation] = []
        for raid_data in raids_data["raids"]:
            # Parse VP tiers
            vp_tiers = [
                VPTier(min_strength=tier["min_strength"], vp=tier["vp"])
                for tier in raid_data["vp_tiers"]
            ]
            
            # Parse sublocations
            sublocations = [
                RaidSublocation(
                    id=sub["id"],
                    plunder=sub["plunder"],
                    worker_on_spot=sub["worker_on_spot"]
                )
                for sub in raid_data["sublocations"]
            ]
            
            raid = RaidLocation(
                id=raid_data["id"],
                name=raid_data["name"],
                type=raid_data["type"],
                requirements=raid_data["requirements"],
                vp_tiers=vp_tiers,
                dice_added=raid_data["dice_added"],
                sublocations=sublocations
            )
            self.raids.append(raid)
        
        # Create lookup dictionaries
        self.buildings_by_id: Dict[str, VillageBuilding] = {b.id: b for b in self.buildings}
        self.buildings_by_name: Dict[str, VillageBuilding] = {b.name: b for b in self.buildings}
        self.offerings_by_id: Dict[str, OfferingTile] = {o.id: o for o in self.offerings}
        self.raids_by_id: Dict[str, RaidLocation] = {r.id: r for r in self.raids}
        self.raids_by_name: Dict[str, RaidLocation] = {r.name: r for r in self.raids}
    
    def get_building(self, building_id: str) -> Optional[VillageBuilding]:
        """Get building by ID"""
        return self.buildings_by_id.get(building_id)
    
    def get_building_by_name(self, name: str) -> Optional[VillageBuilding]:
        """Get building by name"""
        return self.buildings_by_name.get(name)
    
    def get_offering(self, offering_id: str) -> Optional[OfferingTile]:
        """Get offering by ID"""
        return self.offerings_by_id.get(offering_id)
    
    def get_raid(self, raid_id: str) -> Optional[RaidLocation]:
        """Get raid by ID"""
        return self.raids_by_id.get(raid_id)
    
    def get_raid_by_name(self, name: str) -> Optional[RaidLocation]:
        """Get raid by name"""
        return self.raids_by_name.get(name)
    
    def get_raids_by_type(self, raid_type: str) -> List[RaidLocation]:
        """Get all raids of a specific type"""
        return [r for r in self.raids if r.type == raid_type]
    
    def __repr__(self) -> str:
        return f"BoardDatabase({len(self.buildings)} buildings, {len(self.offerings)} offerings, {len(self.raids)} raids)"


# Singleton instance for easy access
_board_db: Optional[BoardDatabase] = None

def get_board_database() -> BoardDatabase:
    """Get or create the board database singleton"""
    global _board_db
    if _board_db is None:
        _board_db = BoardDatabase()
    return _board_db


if __name__ == "__main__":
    # Test loading
    db = BoardDatabase()
    print(db)
    
    print("\nVillage Buildings:")
    for building in db.buildings:
        print(f"  {building}")
    
    print("\nRaid Locations:")
    for raid in db.raids:
        print(f"  {raid}")
        for sub in raid.sublocations:
            print(f"    - {sub}")
    
    print("\nOfferings (first 5):")
    for offering in db.offerings[:5]:
        print(f"  {offering}")
    
    # Test strength-to-VP calculation
    print("\nFortress 1 VP calculation:")
    fortress1 = db.get_raid_by_name("Fortress 1")
    if fortress1:
        for strength in [20, 25, 30, 35, 40]:
            vp = fortress1.get_vp_for_strength(strength)
            print(f"  Strength {strength} → {vp} VP")
