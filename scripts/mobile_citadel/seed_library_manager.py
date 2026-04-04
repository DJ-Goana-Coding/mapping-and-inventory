#!/usr/bin/env python3
"""
🌱 SEED LIBRARY MANAGER
Mobile Citadel Command Center - Comprehensive Seed Collection Tracker

Manages complete seed library for community establishment:
- Herbs & Spices
- Tobacco & Cannabis (Enlightenment seeds)
- Medicinal plants
- Livestock feed
- Insect repelling
- Barrier & fencing plants
- Food crops
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

class SeedLibraryManager:
    """Manages comprehensive seed collection for off-grid communities"""
    
    def __init__(self, data_file: str = "/tmp/mobile_citadel/seed_library.json"):
        self.data_file = Path(data_file)
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        self.seed_categories = self._initialize_seed_library()
        self.load_data()
    
    def _initialize_seed_library(self) -> Dict:
        """Initialize comprehensive seed library"""
        return {
            "herbs_spices": [
                {"name": "Basil (multiple varieties)", "quantity": "100g", "acquired": False, "cost_estimate": 20},
                {"name": "Oregano", "quantity": "50g", "acquired": False, "cost_estimate": 15},
                {"name": "Thyme", "quantity": "50g", "acquired": False, "cost_estimate": 15},
                {"name": "Rosemary", "quantity": "50g", "acquired": False, "cost_estimate": 15},
                {"name": "Sage", "quantity": "50g", "acquired": False, "cost_estimate": 15},
                {"name": "Mint (peppermint, spearmint)", "quantity": "50g", "acquired": False, "cost_estimate": 15},
                {"name": "Parsley", "quantity": "100g", "acquired": False, "cost_estimate": 15},
                {"name": "Cilantro/Coriander", "quantity": "100g", "acquired": False, "cost_estimate": 15},
                {"name": "Dill", "quantity": "50g", "acquired": False, "cost_estimate": 15},
                {"name": "Fennel", "quantity": "50g", "acquired": False, "cost_estimate": 15},
                {"name": "Chives", "quantity": "50g", "acquired": False, "cost_estimate": 15},
                {"name": "Cumin", "quantity": "100g", "acquired": False, "cost_estimate": 20},
                {"name": "Black Pepper", "quantity": "200g", "acquired": False, "cost_estimate": 30},
                {"name": "Chili Peppers (varieties)", "quantity": "100g", "acquired": False, "cost_estimate": 25},
                {"name": "Turmeric rhizomes", "quantity": "500g", "acquired": False, "cost_estimate": 40},
                {"name": "Ginger rhizomes", "quantity": "500g", "acquired": False, "cost_estimate": 30},
            ],
            "enlightenment_seeds": [
                {"name": "Tobacco (heirloom varieties)", "quantity": "50g", "acquired": False, "cost_estimate": 30, "notes": "Legal heirloom tobacco"},
                {"name": "Cannabis sativa (hemp - legal)", "quantity": "200g", "acquired": False, "cost_estimate": 100, "notes": "Industrial hemp, <0.3% THC, check local laws"},
                {"name": "Cannabis indica (medicinal - where legal)", "quantity": "100g", "acquired": False, "cost_estimate": 150, "notes": "Medical use only, verify legality"},
                {"name": "Blue Lotus (Nymphaea caerulea)", "quantity": "50g", "acquired": False, "cost_estimate": 40},
                {"name": "Damiana (Turnera diffusa)", "quantity": "50g", "acquired": False, "cost_estimate": 35},
                {"name": "Mugwort (Artemisia vulgaris)", "quantity": "50g", "acquired": False, "cost_estimate": 20},
                {"name": "Calea zacatechichi (Dream herb)", "quantity": "25g", "acquired": False, "cost_estimate": 45},
                {"name": "Passion Flower", "quantity": "50g", "acquired": False, "cost_estimate": 25},
            ],
            "medicinal_plants": [
                {"name": "Echinacea (immune support)", "quantity": "50g", "acquired": False, "cost_estimate": 30},
                {"name": "Chamomile (calming)", "quantity": "50g", "acquired": False, "cost_estimate": 20},
                {"name": "Lavender (relaxation)", "quantity": "50g", "acquired": False, "cost_estimate": 25},
                {"name": "Calendula (skin healing)", "quantity": "50g", "acquired": False, "cost_estimate": 20},
                {"name": "St. John's Wort", "quantity": "25g", "acquired": False, "cost_estimate": 30},
                {"name": "Yarrow (wound healing)", "quantity": "25g", "acquired": False, "cost_estimate": 20},
                {"name": "Comfrey (external healing)", "quantity": "50g", "acquired": False, "cost_estimate": 25},
                {"name": "Aloe Vera (gel plants)", "quantity": "10 plants", "acquired": False, "cost_estimate": 50},
                {"name": "Plantain (wound healing)", "quantity": "50g", "acquired": False, "cost_estimate": 15},
                {"name": "Lemon Balm (digestive)", "quantity": "50g", "acquired": False, "cost_estimate": 20},
                {"name": "Valerian (sleep aid)", "quantity": "25g", "acquired": False, "cost_estimate": 35},
                {"name": "Ashwagandha", "quantity": "50g", "acquired": False, "cost_estimate": 40},
            ],
            "livestock_feed": [
                {"name": "Alfalfa (hay crop)", "quantity": "5kg", "acquired": False, "cost_estimate": 50},
                {"name": "Clover (nitrogen fixing)", "quantity": "2kg", "acquired": False, "cost_estimate": 40},
                {"name": "Timothy Grass", "quantity": "2kg", "acquired": False, "cost_estimate": 35},
                {"name": "Ryegrass", "quantity": "3kg", "acquired": False, "cost_estimate": 40},
                {"name": "Oats (feed grain)", "quantity": "10kg", "acquired": False, "cost_estimate": 30},
                {"name": "Barley (feed grain)", "quantity": "10kg", "acquired": False, "cost_estimate": 30},
                {"name": "Corn (field corn)", "quantity": "5kg", "acquired": False, "cost_estimate": 40},
                {"name": "Sorghum", "quantity": "3kg", "acquired": False, "cost_estimate": 35},
                {"name": "Sunflower (fodder)", "quantity": "2kg", "acquired": False, "cost_estimate": 30},
            ],
            "insect_repelling": [
                {"name": "Citronella Grass", "quantity": "100g", "acquired": False, "cost_estimate": 25},
                {"name": "Lemongrass", "quantity": "100g", "acquired": False, "cost_estimate": 20},
                {"name": "Marigold (Tagetes)", "quantity": "200g", "acquired": False, "cost_estimate": 20},
                {"name": "Chrysanthemum (pyrethrum)", "quantity": "50g", "acquired": False, "cost_estimate": 30},
                {"name": "Neem tree seeds", "quantity": "100g", "acquired": False, "cost_estimate": 40},
                {"name": "Catnip", "quantity": "50g", "acquired": False, "cost_estimate": 20},
                {"name": "Pennyroyal", "quantity": "25g", "acquired": False, "cost_estimate": 25},
                {"name": "Tansy", "quantity": "25g", "acquired": False, "cost_estimate": 20},
            ],
            "barrier_fencing": [
                {"name": "Bamboo (running varieties)", "quantity": "50 rhizomes", "acquired": False, "cost_estimate": 200},
                {"name": "Hawthorn", "quantity": "200g", "acquired": False, "cost_estimate": 40},
                {"name": "Blackberry/Raspberry (thorny)", "quantity": "100g", "acquired": False, "cost_estimate": 30},
                {"name": "Rose (wild/hedge varieties)", "quantity": "100g", "acquired": False, "cost_estimate": 35},
                {"name": "Pyracantha (firethorn)", "quantity": "50g", "acquired": False, "cost_estimate": 30},
                {"name": "Bougainvillea", "quantity": "50 cuttings", "acquired": False, "cost_estimate": 100},
                {"name": "Willow (living fence)", "quantity": "100 cuttings", "acquired": False, "cost_estimate": 50},
                {"name": "Hedge plants mix", "quantity": "500g", "acquired": False, "cost_estimate": 60},
            ],
            "food_crops": [
                {"name": "Tomato (heirloom varieties)", "quantity": "200g", "acquired": False, "cost_estimate": 50},
                {"name": "Beans (bush, pole, lima)", "quantity": "5kg", "acquired": False, "cost_estimate": 60},
                {"name": "Peas (sugar snap, snow)", "quantity": "3kg", "acquired": False, "cost_estimate": 45},
                {"name": "Squash (winter, summer)", "quantity": "500g", "acquired": False, "cost_estimate": 40},
                {"name": "Pumpkin", "quantity": "500g", "acquired": False, "cost_estimate": 35},
                {"name": "Cucumber", "quantity": "200g", "acquired": False, "cost_estimate": 30},
                {"name": "Lettuce (varieties)", "quantity": "200g", "acquired": False, "cost_estimate": 30},
                {"name": "Spinach", "quantity": "300g", "acquired": False, "cost_estimate": 25},
                {"name": "Kale", "quantity": "200g", "acquired": False, "cost_estimate": 25},
                {"name": "Carrots", "quantity": "300g", "acquired": False, "cost_estimate": 25},
                {"name": "Beets", "quantity": "300g", "acquired": False, "cost_estimate": 25},
                {"name": "Onions (sets)", "quantity": "2kg", "acquired": False, "cost_estimate": 40},
                {"name": "Garlic (bulbs)", "quantity": "2kg", "acquired": False, "cost_estimate": 60},
                {"name": "Potatoes (seed)", "quantity": "10kg", "acquired": False, "cost_estimate": 50},
                {"name": "Sweet Potatoes (slips)", "quantity": "100 slips", "acquired": False, "cost_estimate": 80},
                {"name": "Melons (watermelon, cantaloupe)", "quantity": "200g", "acquired": False, "cost_estimate": 35},
            ],
            "trees_perennials": [
                {"name": "Fruit tree seeds (apple, pear, cherry)", "quantity": "500g", "acquired": False, "cost_estimate": 100},
                {"name": "Citrus seeds (lemon, orange, lime)", "quantity": "200g", "acquired": False, "cost_estimate": 80},
                {"name": "Avocado pits", "quantity": "50 pits", "acquired": False, "cost_estimate": 50},
                {"name": "Mango seeds", "quantity": "20 seeds", "acquired": False, "cost_estimate": 40},
                {"name": "Berry bushes (blueberry, raspberry)", "quantity": "50 plants", "acquired": False, "cost_estimate": 200},
                {"name": "Grape vines", "quantity": "20 cuttings", "acquired": False, "cost_estimate": 100},
                {"name": "Nut trees (walnut, pecan, almond)", "quantity": "50 seeds", "acquired": False, "cost_estimate": 150},
                {"name": "Moringa seeds", "quantity": "200g", "acquired": False, "cost_estimate": 40},
            ]
        }
    
    def load_data(self):
        """Load seed library data"""
        if self.data_file.exists():
            try:
                with open(self.data_file, 'r') as f:
                    saved_data = json.load(f)
                    for category, seeds in saved_data.get("seed_categories", {}).items():
                        if category in self.seed_categories:
                            for i, seed in enumerate(seeds):
                                if i < len(self.seed_categories[category]):
                                    self.seed_categories[category][i].update(seed)
            except (json.JSONDecodeError, IOError):
                pass
    
    def save_data(self):
        """Save seed library data"""
        data = {
            "last_updated": datetime.utcnow().isoformat(),
            "seed_categories": self.seed_categories
        }
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def get_summary(self) -> Dict:
        """Get seed library summary"""
        summary = {
            "total_varieties": 0,
            "total_acquired": 0,
            "total_cost_estimate": 0,
            "total_actual_cost": 0,
            "by_category": {}
        }
        
        for category, seeds in self.seed_categories.items():
            cat_summary = {
                "varieties": len(seeds),
                "acquired": len([s for s in seeds if s.get("acquired", False)]),
                "cost_estimate": sum(s.get("cost_estimate", 0) for s in seeds),
                "actual_cost": sum(s.get("actual_cost", 0) for s in seeds)
            }
            
            summary["by_category"][category] = cat_summary
            summary["total_varieties"] += cat_summary["varieties"]
            summary["total_acquired"] += cat_summary["acquired"]
            summary["total_cost_estimate"] += cat_summary["cost_estimate"]
            summary["total_actual_cost"] += cat_summary["actual_cost"]
        
        return summary
    
    def generate_report(self) -> str:
        """Generate seed library report"""
        summary = self.get_summary()
        
        report = []
        report.append("=" * 70)
        report.append("🌱 SEED LIBRARY COMPREHENSIVE REPORT")
        report.append("=" * 70)
        
        report.append(f"\n📊 Overview:")
        report.append(f"  Total Varieties: {summary['total_varieties']}")
        report.append(f"  Acquired: {summary['total_acquired']}")
        report.append(f"  Remaining: {summary['total_varieties'] - summary['total_acquired']}")
        report.append(f"  Estimated Cost: ${summary['total_cost_estimate']:,}")
        report.append(f"  Actual Cost: ${summary['total_actual_cost']:,}")
        
        report.append(f"\n📦 By Category:")
        for category, data in summary['by_category'].items():
            percent = (data['acquired'] / data['varieties'] * 100) if data['varieties'] > 0 else 0
            report.append(f"\n  🌿 {category.replace('_', ' ').upper()}:")
            report.append(f"     Varieties: {data['varieties']}")
            report.append(f"     Acquired: {data['acquired']} ({percent:.1f}%)")
            report.append(f"     Cost: ${data['cost_estimate']:,}")
        
        report.append("\n" + "=" * 70)
        
        return "\n".join(report)


def main():
    """Main execution"""
    import sys
    
    manager = SeedLibraryManager()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "report":
            print(manager.generate_report())
        
        elif command == "summary":
            summary = manager.get_summary()
            print(json.dumps(summary, indent=2))
        
        else:
            print(f"Unknown command: {command}")
    else:
        print(manager.generate_report())


if __name__ == "__main__":
    main()
