"""
Card data loader for Townsfolk/Crew cards
"""
import json
from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from pathlib import Path


@dataclass
class TownsfolkCard:
    """Represents a Townsfolk/Crew card"""
    id: str
    name: str
    cost: int
    strength: int
    deck_count: int
    vp: int
    hire_crew_action: Dict[str, Any]
    town_hall_action: Dict[str, Any]
    color_requirement: Optional[str]
    is_hero: bool = False
    
    def __str__(self) -> str:
        return f"{self.name} (Cost: {self.cost}, Strength: {self.strength})"
    
    def is_playable_at_town_hall(self) -> bool:
        """Check if this card can be played at Town Hall (heroes cannot)"""
        return self.town_hall_action.get("type") != "hero_no_discard"


class CardDatabase:
    """Manages all Townsfolk/Crew cards"""
    
    def __init__(self, data_path: str = None):
        """Load cards from JSON file"""
        if data_path is None:
            # Default path relative to this file
            base_dir = Path(__file__).parent.parent
            data_path = base_dir / "data" / "cards_townsfolk.json"
        
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.cards: List[TownsfolkCard] = []
        for card_data in data["cards"]:
            card = TownsfolkCard(
                id=card_data["id"],
                name=card_data["name"],
                cost=card_data["cost"],
                strength=card_data["strength"],
                deck_count=card_data["deck_count"],
                vp=card_data["vp"],
                hire_crew_action=card_data["hire_crew_action"],
                town_hall_action=card_data["town_hall_action"],
                color_requirement=card_data.get("color_requirement"),
                is_hero=card_data.get("is_hero", False)
            )
            self.cards.append(card)
        
        # Create lookup dictionaries
        self.cards_by_id: Dict[str, TownsfolkCard] = {c.id: c for c in self.cards}
        self.cards_by_name: Dict[str, TownsfolkCard] = {c.name: c for c in self.cards}
    
    def get_card(self, card_id: str) -> Optional[TownsfolkCard]:
        """Get card by ID"""
        return self.cards_by_id.get(card_id)
    
    def get_card_by_name(self, name: str) -> Optional[TownsfolkCard]:
        """Get card by name"""
        return self.cards_by_name.get(name)
    
    def get_all_cards(self) -> List[TownsfolkCard]:
        """Get all cards"""
        return self.cards.copy()
    
    def get_heroes(self) -> List[TownsfolkCard]:
        """Get all hero cards"""
        return [c for c in self.cards if c.is_hero]
    
    def create_deck(self) -> List[TownsfolkCard]:
        """Create a full game deck with correct quantities"""
        deck = []
        for card in self.cards:
            deck.extend([card] * card.deck_count)
        return deck
    
    def __len__(self) -> int:
        return len(self.cards)
    
    def __repr__(self) -> str:
        return f"CardDatabase({len(self.cards)} unique cards)"


# Singleton instance for easy access
_card_db: Optional[CardDatabase] = None

def get_card_database() -> CardDatabase:
    """Get or create the card database singleton"""
    global _card_db
    if _card_db is None:
        _card_db = CardDatabase()
    return _card_db


if __name__ == "__main__":
    # Test loading
    db = CardDatabase()
    print(f"Loaded {len(db)} cards")
    print(f"\nHeroes: {[h.name for h in db.get_heroes()]}")
    print(f"\nTotal cards in deck: {len(db.create_deck())}")
    
    # Show some examples
    print("\nExample cards:")
    for card in db.get_all_cards()[:5]:
        print(f"  {card}")
