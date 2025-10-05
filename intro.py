"""
Intermittent Fasting Meal & Supplement Planner
===============================================
A comprehensive tool to plan optimal meals and supplements for intermittent fasting
with focus on high-fat, high-protein foods and essential vitamins.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json
from dataclasses import dataclass, asdict

@dataclass
class Food:
    name: str
    protein_per_100g: float
    fat_per_100g: float
    carbs_per_100g: float
    calories_per_100g: float
    serving_size: str
    meal_timing: str  # "first_meal", "last_meal", "anytime"
    preparation_time: int  # minutes

@dataclass
class Supplement:
    name: str
    dosage: str
    timing: str  # "with_food", "empty_stomach", "morning", "evening"
    notes: str

@dataclass
class FastingSchedule:
    eating_window_start: str  # "12:00"
    eating_window_end: str    # "20:00"
    fasting_duration: int     # hours

class IntermittentFastingPlanner:
    def __init__(self):
        self.foods = self._initialize_foods()
        self.supplements = self._initialize_supplements()
        self.shopping_list = []
        
    def _initialize_foods(self) -> List[Food]:
        """Initialize database of keto/IF-friendly foods"""
        return [
            # High-fat, high-protein foods
            Food("Avocado", 2.0, 14.7, 8.5, 160, "1 medium avocado", "anytime", 5),
            Food("Salmon (wild-caught)", 25.4, 13.4, 0, 208, "150g fillet", "anytime", 15),
            Food("Eggs (pasture-raised)", 13.0, 11.0, 1.1, 155, "2 large eggs", "anytime", 10),
            Food("Grass-fed Beef", 26.0, 20.0, 0, 250, "150g steak", "anytime", 20),
            Food("Olive Oil (extra virgin)", 0, 100, 0, 884, "1 tbsp", "anytime", 0),
            Food("Nuts (mixed)", 15.0, 54.0, 16.0, 607, "30g handful", "anytime", 0),
            Food("Greek Yogurt (full-fat)", 10.0, 5.0, 4.0, 97, "150g cup", "anytime", 0),
            Food("MCT Oil", 0, 100, 0, 828, "1 tbsp", "first_meal", 0),
            Food("Coconut Oil", 0, 99.0, 0, 862, "1 tbsp", "anytime", 0),
            Food("Sardines", 25.0, 11.5, 0, 208, "100g can", "anytime", 5),
            Food("Mackerel", 26.0, 16.0, 0, 262, "150g fillet", "anytime", 15),
            Food("Cheese (aged cheddar)", 25.0, 33.0, 1.3, 403, "50g portion", "anytime", 0),
            Food("Spinach", 2.9, 0.4, 3.6, 23, "100g serving", "anytime", 5),
            Food("Broccoli", 3.0, 0.4, 7.0, 34, "150g serving", "anytime", 10),
            Food("Brussels Sprouts", 3.4, 0.3, 9.0, 43, "150g serving", "anytime", 15),
            Food("Cauliflower", 1.9, 0.3, 5.0, 25, "150g serving", "anytime", 12),
        ]
    
    def _initialize_supplements(self) -> List[Supplement]:
        """Initialize supplement schedule"""
        return [
            Supplement("Vitamin D3", "2000-4000 IU", "with_food", "Fat-soluble, take with meals containing fat"),
            Supplement("Vitamin K2 (MK-7)", "100-200 mcg", "with_food", "Synergistic with D3, take together"),
            Supplement("Magnesium Glycinate", "200-400mg", "evening", "Better absorption, helps with sleep"),
            Supplement("Biotin", "2500-5000 mcg", "morning", "Support hair, skin, nails"),
            Supplement("Omega-3 Fish Oil", "1000-2000mg EPA/DHA", "with_food", "If not eating enough fatty fish"),
            Supplement("Electrolytes", "As needed", "morning", "Important during fasting periods"),
        ]
    
    def create_daily_meal_plan(self, fasting_schedule: FastingSchedule, target_calories: int = 1800) -> Dict:
        """Create a daily meal plan within eating window"""
        eating_start = datetime.strptime(fasting_schedule.eating_window_start, "%H:%M")
        eating_end = datetime.strptime(fasting_schedule.eating_window_end, "%H:%M")
        
        # Calculate meal times
        window_hours = (eating_end - eating_start).total_seconds() / 3600
        first_meal_time = eating_start
        last_meal_time = eating_end - timedelta(hours=1)  # 1 hour before window closes
        
        # Select foods for optimal nutrition
        first_meal_foods = [f for f in self.foods if f.meal_timing in ["first_meal", "anytime"]]
        last_meal_foods = [f for f in self.foods if f.meal_timing in ["last_meal", "anytime"]]
        
        meal_plan = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "fasting_schedule": asdict(fasting_schedule),
            "meals": {
                "first_meal": {
                    "time": first_meal_time.strftime("%H:%M"),
                    "foods": self._select_meal_foods(first_meal_foods, target_calories * 0.6),
                    "supplements": self._get_meal_supplements("first_meal")
                },
                "last_meal": {
                    "time": last_meal_time.strftime("%H:%M"),
                    "foods": self._select_meal_foods(last_meal_foods, target_calories * 0.4),
                    "supplements": self._get_meal_supplements("last_meal")
                }
            },
            "daily_supplements": self._get_daily_supplement_schedule(),
            "prep_schedule": self._create_prep_schedule(first_meal_time, last_meal_time)
        }
        
        return meal_plan
    
    def _select_meal_foods(self, available_foods: List[Food], target_calories: float) -> List[Dict]:
        """Select foods for a meal based on nutritional goals"""
        selected_foods = []
        current_calories = 0
        
        # Prioritize high-fat, high-protein foods
        sorted_foods = sorted(available_foods, 
                            key=lambda f: (f.protein_per_100g + f.fat_per_100g), 
                            reverse=True)
        
        for food in sorted_foods[:4]:  # Limit to 4 foods per meal
            if current_calories < target_calories:
                serving_calories = food.calories_per_100g * 0.8  # Approximate serving
                selected_foods.append({
                    "name": food.name,
                    "serving": food.serving_size,
                    "calories": serving_calories,
                    "protein": food.protein_per_100g * 0.8,
                    "fat": food.fat_per_100g * 0.8,
                    "prep_time": food.preparation_time
                })
                current_calories += serving_calories
        
        return selected_foods
    
    def _get_meal_supplements(self, meal_type: str) -> List[Dict]:
        """Get supplements to take with specific meals"""
        meal_supplements = []
        
        for supplement in self.supplements:
            if supplement.timing == "with_food":
                meal_supplements.append({
                    "name": supplement.name,
                    "dosage": supplement.dosage,
                    "notes": supplement.notes
                })
        
        return meal_supplements
    
    def _get_daily_supplement_schedule(self) -> Dict:
        """Create full daily supplement schedule"""
        schedule = {
            "morning": [],
            "with_meals": [],
            "evening": []
        }
        
        for supplement in self.supplements:
            supp_info = {
                "name": supplement.name,
                "dosage": supplement.dosage,
                "notes": supplement.notes
            }
            
            if supplement.timing == "morning":
                schedule["morning"].append(supp_info)
            elif supplement.timing == "with_food":
                schedule["with_meals"].append(supp_info)
            elif supplement.timing == "evening":
                schedule["evening"].append(supp_info)
        
        return schedule
    
    def _create_prep_schedule(self, first_meal_time: datetime, last_meal_time: datetime) -> Dict:
        """Create food preparation timeline"""
        prep_schedule = {
            "shopping": "Day before or morning",
            "meal_prep": []
        }
        
        # First meal prep
        first_prep_time = first_meal_time - timedelta(minutes=30)
        prep_schedule["meal_prep"].append({
            "time": first_prep_time.strftime("%H:%M"),
            "task": "Prepare first meal",
            "duration": "20-30 minutes"
        })
        
        # Last meal prep
        last_prep_time = last_meal_time - timedelta(minutes=25)
        prep_schedule["meal_prep"].append({
            "time": last_prep_time.strftime("%H:%M"),
            "task": "Prepare last meal",
            "duration": "15-25 minutes"
        })
        
        return prep_schedule
    
    def generate_shopping_list(self, meal_plan: Dict, days: int = 7) -> List[Dict]:
        """Generate food-focused shopping list for multiple days"""
        shopping_list = {}
        
        # Extract foods from meal plan (supplements excluded as requested)
        for meal in meal_plan["meals"].values():
            for food in meal["foods"]:
                food_name = food["name"]
                if food_name in shopping_list:
                    # Food already exists, just note it appears multiple times
                    continue
                else:
                    shopping_list[food_name] = {
                        "quantity": self._calculate_food_quantity(food_name, days),
                        "category": self._categorize_food(food_name),
                        "notes": f"For {days} days of meal prep"
                    }
        
        return [{"item": k, **v} for k, v in shopping_list.items()]
    
    def _calculate_food_quantity(self, food_name: str, days: int) -> str:
        """Calculate appropriate shopping quantity for food items"""
        food_lower = food_name.lower()
        
        if "salmon" in food_lower or "fish" in food_lower:
            portions = max(1, days // 2)  # Every other day portions
            return f"{portions} fillets"
        elif "beef" in food_lower:
            portions = max(1, days // 2)
            return f"{portions} steaks"
        elif "chicken" in food_lower:
            portions = max(1, days // 2)
            return f"{portions} breasts"
        elif "eggs" in food_lower:
            total_eggs = days * 2  # 2 eggs per day
            dozens = max(1, total_eggs // 12)
            return f"{dozens} dozen"
        elif "avocado" in food_lower:
            return f"{days} avocados"
        elif "oil" in food_lower:
            return "1 bottle"
        elif "nuts" in food_lower:
            return "1 bag"
        elif "cheese" in food_lower:
            return f"1 block ({days} servings)"
        elif any(veg in food_lower for veg in ["spinach", "broccoli", "cauliflower"]):
            portions = max(1, days // 2)
            return f"{portions} bunches/bags"
        else:
            return f"{days} servings"
    
    def _categorize_food(self, food_name: str) -> str:
        """Categorize foods for shopping list organization"""
        if any(protein in food_name.lower() for protein in ["salmon", "beef", "chicken", "fish", "sardines", "mackerel"]):
            return "Meat & Fish"
        elif any(dairy in food_name.lower() for dairy in ["cheese", "yogurt", "butter"]):
            return "Dairy"
        elif any(veg in food_name.lower() for veg in ["spinach", "broccoli", "cauliflower", "brussels"]):
            return "Vegetables"
        elif any(fat in food_name.lower() for fat in ["oil", "nuts", "avocado"]):
            return "Healthy Fats"
        else:
            return "Other"
    
    def create_weekly_plan(self, fasting_schedule: FastingSchedule) -> Dict:
        """Create a complete weekly meal and supplement plan"""
        weekly_plan = {
            "week_of": datetime.now().strftime("%Y-%m-%d"),
            "fasting_schedule": asdict(fasting_schedule),
            "daily_plans": {},
            "weekly_shopping_list": [],
            "prep_tips": self._get_prep_tips()
        }
        
        # Create daily plans
        for day in range(7):
            date = (datetime.now() + timedelta(days=day)).strftime("%Y-%m-%d")
            daily_plan = self.create_daily_meal_plan(fasting_schedule)
            weekly_plan["daily_plans"][date] = daily_plan
        
        # Generate comprehensive shopping list
        weekly_plan["weekly_shopping_list"] = self.generate_shopping_list(
            weekly_plan["daily_plans"][list(weekly_plan["daily_plans"].keys())[0]], 7
        )
        
        return weekly_plan
    
    def _get_prep_tips(self) -> List[str]:
        """Provide meal prep and IF optimization tips"""
        return [
            "Prep proteins in bulk at the start of the week",
            "Pre-wash and chop vegetables for quick cooking",
            "Keep emergency keto snacks (nuts, cheese) on hand",
            "Prepare MCT oil or bulletproof coffee for breaking fast",
            "Set reminders for supplement timing",
            "Stay hydrated during fasting periods with electrolytes",
            "Consider batch cooking proteins like salmon and beef",
            "Keep avocados at different ripeness stages for the week"
        ]
    
    def save_plan_to_file(self, plan: Dict, filename: str = None):
        """Save meal plan to JSON file"""
        if not filename:
            filename = f"IF_meal_plan_{datetime.now().strftime('%Y%m%d')}.json"
        
        with open(filename, 'w') as f:
            json.dump(plan, f, indent=4, default=str)
        
        print(f"Meal plan saved to: {filename}")

def main():
    """Main function to demonstrate the planner"""
    planner = IntermittentFastingPlanner()
    
    # Example fasting schedule (16:8 IF)
    fasting_schedule = FastingSchedule(
        eating_window_start="12:00",
        eating_window_end="20:00",
        fasting_duration=16
    )
    
    print("🍽️  Intermittent Fasting Meal & Supplement Planner")
    print("=" * 50)
    
    # Create daily plan
    daily_plan = planner.create_daily_meal_plan(fasting_schedule)
    
    print(f"\n📅 Daily Plan for {daily_plan['date']}")
    print(f"Eating Window: {fasting_schedule.eating_window_start} - {fasting_schedule.eating_window_end}")
    print(f"Fasting Duration: {fasting_schedule.fasting_duration} hours")
    
    # Display meals
    for meal_name, meal_info in daily_plan["meals"].items():
        print(f"\n🍽️  {meal_name.replace('_', ' ').title()} - {meal_info['time']}")
        print("Foods:")
        for food in meal_info["foods"]:
            print(f"  • {food['name']} ({food['serving']}) - {food['calories']:.0f} cal")
        
        if meal_info["supplements"]:
            print("Supplements:")
            for supp in meal_info["supplements"]:
                print(f"  💊 {supp['name']} - {supp['dosage']}")
    
    # Display supplement schedule
    print(f"\n💊 Daily Supplement Schedule:")
    for timing, supplements in daily_plan["daily_supplements"].items():
        if supplements:
            print(f"\n{timing.replace('_', ' ').title()}:")
            for supp in supplements:
                print(f"  • {supp['name']} - {supp['dosage']}")
    
    # Display prep schedule
    print(f"\n⏰ Preparation Schedule:")
    print(f"Shopping: {daily_plan['prep_schedule']['shopping']}")
    for prep in daily_plan["prep_schedule"]["meal_prep"]:
        print(f"  • {prep['time']}: {prep['task']} ({prep['duration']})")
    
    # Generate shopping list (foods only)
    shopping_list = planner.generate_shopping_list(daily_plan, 7)
    print(f"\n🛒 Weekly Food Shopping List:")
    print("📝 Note: Supplements excluded - manage separately")
    
    categories = {}
    for item in shopping_list:
        category = item["category"]
        if category not in categories:
            categories[category] = []
        categories[category].append(item)
    
    for category, items in categories.items():
        print(f"\n{category}:")
        for item in items:
            print(f"  • {item['item']} - {item['quantity']}")
    
    # Create weekly plan
    print(f"\n📊 Creating weekly plan...")
    weekly_plan = planner.create_weekly_plan(fasting_schedule)
    
    print(f"\n💡 Weekly Prep Tips:")
    for tip in weekly_plan["prep_tips"]:
        print(f"  • {tip}")
    
    # Save plans
    planner.save_plan_to_file(daily_plan, "daily_if_plan.json")
    planner.save_plan_to_file(weekly_plan, "weekly_if_plan.json")
    
    print(f"\n✅ Plans saved! Check the JSON files for detailed meal planning.")

if __name__ == "__main__":
    main()