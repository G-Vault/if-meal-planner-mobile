"""
Meal Customizer for Intermittent Fasting
========================================
Advanced customization options for personalizing your IF meal plans
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from intro import IntermittentFastingPlanner, Food, Supplement, FastingSchedule
import json

@dataclass
class NutritionalGoals:
    calories_per_day: int
    protein_percentage: float  # 0.25 = 25%
    fat_percentage: float      # 0.65 = 65%
    carb_percentage: float     # 0.10 = 10%
    fiber_goal: int           # grams per day

@dataclass
class PersonalPreferences:
    food_allergies: List[str]
    food_dislikes: List[str]
    preferred_cuisines: List[str]
    cooking_skill_level: str  # "beginner", "intermediate", "advanced"
    max_prep_time: int       # minutes per meal

class AdvancedIFPlanner(IntermittentFastingPlanner):
    def __init__(self):
        super().__init__()
        self.custom_foods = []
        self.custom_supplements = []
    
    def customize_nutritional_goals(self, goals: NutritionalGoals) -> Dict:
        """Calculate macronutrient targets based on personal goals"""
        protein_calories = goals.calories_per_day * goals.protein_percentage
        fat_calories = goals.calories_per_day * goals.fat_percentage
        carb_calories = goals.calories_per_day * goals.carb_percentage
        
        return {
            "daily_calories": goals.calories_per_day,
            "protein_grams": protein_calories / 4,  # 4 cal per gram
            "fat_grams": fat_calories / 9,          # 9 cal per gram
            "carb_grams": carb_calories / 4,        # 4 cal per gram
            "fiber_grams": goals.fiber_goal,
            "macros_percentage": {
                "protein": goals.protein_percentage * 100,
                "fat": goals.fat_percentage * 100,
                "carbs": goals.carb_percentage * 100
            }
        }
    
    def filter_foods_by_preferences(self, preferences: PersonalPreferences) -> List[Food]:
        """Filter foods based on personal preferences and restrictions"""
        filtered_foods = []
        
        for food in self.foods + self.custom_foods:
            # Skip foods with allergies
            if any(allergen.lower() in food.name.lower() for allergen in preferences.food_allergies):
                continue
            
            # Skip disliked foods
            if any(dislike.lower() in food.name.lower() for dislike in preferences.food_dislikes):
                continue
            
            # Filter by prep time
            if food.preparation_time <= preferences.max_prep_time:
                filtered_foods.append(food)
        
        return filtered_foods
    
    def add_custom_food(self, food: Food):
        """Add a custom food to the database"""
        self.custom_foods.append(food)
        print(f"Added custom food: {food.name}")
    
    def add_custom_supplement(self, supplement: Supplement):
        """Add a custom supplement to the regimen"""
        self.custom_supplements.append(supplement)
        print(f"Added custom supplement: {supplement.name}")
    
    def create_personalized_meal_plan(self, 
                                    fasting_schedule: FastingSchedule,
                                    nutritional_goals: NutritionalGoals,
                                    preferences: PersonalPreferences) -> Dict:
        """Create a personalized meal plan based on individual needs"""
        
        # Calculate nutritional targets
        nutrition_targets = self.customize_nutritional_goals(nutritional_goals)
        
        # Filter foods by preferences
        available_foods = self.filter_foods_by_preferences(preferences)
        
        # Create optimized meal plan
        meal_plan = self._create_optimized_plan(
            fasting_schedule, 
            nutrition_targets, 
            available_foods,
            preferences
        )
        
        return meal_plan
    
    def _create_optimized_plan(self, 
                             fasting_schedule: FastingSchedule,
                             nutrition_targets: Dict,
                             available_foods: List[Food],
                             preferences: PersonalPreferences) -> Dict:
        """Create an optimized meal plan"""
        
        eating_window_hours = 24 - fasting_schedule.fasting_duration
        
        # Determine meal distribution
        if eating_window_hours <= 4:  # OMAD (One Meal A Day)
            meal_distribution = {"main_meal": 1.0}
        elif eating_window_hours <= 8:  # Standard 16:8 or 18:6
            meal_distribution = {"first_meal": 0.6, "last_meal": 0.4}
        else:  # Longer eating windows
            meal_distribution = {"first_meal": 0.4, "lunch": 0.3, "last_meal": 0.3}
        
        meal_plan = {
            "personalized_plan": True,
            "nutritional_targets": nutrition_targets,
            "preferences_applied": True,
            "fasting_schedule": fasting_schedule.__dict__,
            "meals": {},
            "supplements": self._get_personalized_supplements(),
            "meal_timing_optimization": self._optimize_meal_timing(fasting_schedule)
        }
        
        # Create meals based on distribution
        for meal_name, calorie_percentage in meal_distribution.items():
            target_calories = nutrition_targets["daily_calories"] * calorie_percentage
            
            meal_plan["meals"][meal_name] = self._create_optimized_meal(
                available_foods,
                target_calories,
                nutrition_targets,
                preferences
            )
        
        return meal_plan
    
    def _create_optimized_meal(self, 
                             available_foods: List[Food],
                             target_calories: float,
                             nutrition_targets: Dict,
                             preferences: PersonalPreferences) -> Dict:
        """Create an optimized individual meal"""
        
        # Sort foods by nutritional density score
        scored_foods = []
        for food in available_foods:
            nutrition_score = self._calculate_nutrition_score(food, nutrition_targets)
            preference_score = self._calculate_preference_score(food, preferences)
            total_score = nutrition_score * 0.7 + preference_score * 0.3
            
            scored_foods.append((food, total_score))
        
        # Sort by score (highest first)
        scored_foods.sort(key=lambda x: x[1], reverse=True)
        
        # Select foods for meal
        selected_foods = []
        current_calories = 0
        current_protein = 0
        current_fat = 0
        
        for food, score in scored_foods:
            if current_calories >= target_calories:
                break
            
            if len(selected_foods) >= 5:  # Max 5 foods per meal
                break
            
            # Calculate serving to fit remaining calories
            remaining_calories = target_calories - current_calories
            max_serving_size = min(1.5, remaining_calories / food.calories_per_100g)  # Max 150g serving
            
            if max_serving_size > 0.3:  # Minimum 30g serving
                serving_size = max_serving_size
                serving_calories = food.calories_per_100g * serving_size
                serving_protein = food.protein_per_100g * serving_size
                serving_fat = food.fat_per_100g * serving_size
                
                selected_foods.append({
                    "name": food.name,
                    "serving_size_multiplier": serving_size,
                    "calories": serving_calories,
                    "protein": serving_protein,
                    "fat": serving_fat,
                    "carbs": food.carbs_per_100g * serving_size,
                    "prep_time": food.preparation_time,
                    "nutrition_score": score
                })
                
                current_calories += serving_calories
                current_protein += serving_protein
                current_fat += serving_fat
        
        return {
            "foods": selected_foods,
            "total_calories": current_calories,
            "total_protein": current_protein,
            "total_fat": current_fat,
            "cooking_instructions": self._generate_cooking_instructions(selected_foods, preferences)
        }
    
    def _calculate_nutrition_score(self, food: Food, targets: Dict) -> float:
        """Calculate nutritional score based on targets"""
        # Higher score for foods that align with macro targets
        protein_score = min(food.protein_per_100g / 30, 1.0)  # Max at 30g protein per 100g
        fat_score = min(food.fat_per_100g / 50, 1.0)         # Max at 50g fat per 100g
        carb_penalty = max(0, 1 - (food.carbs_per_100g / 10)) # Penalty for high carbs
        
        return (protein_score * 0.4 + fat_score * 0.4 + carb_penalty * 0.2)
    
    def _calculate_preference_score(self, food: Food, preferences: PersonalPreferences) -> float:
        """Calculate preference score based on user preferences"""
        score = 0.5  # Base score
        
        # Cooking skill level adjustment
        if preferences.cooking_skill_level == "beginner" and food.preparation_time <= 10:
            score += 0.3
        elif preferences.cooking_skill_level == "advanced":
            score += 0.1  # Slight bonus for more complex foods
        
        # Prep time preference
        if food.preparation_time <= preferences.max_prep_time / 2:
            score += 0.2
        
        return min(score, 1.0)
    
    def _generate_cooking_instructions(self, foods: List[Dict], preferences: PersonalPreferences) -> List[str]:
        """Generate cooking instructions based on selected foods"""
        instructions = []
        
        if preferences.cooking_skill_level == "beginner":
            instructions.append("Keep it simple - focus on basic cooking methods")
            instructions.append("Season with salt, pepper, and olive oil")
        else:
            instructions.append("Feel free to experiment with herbs and spices")
            instructions.append("Consider advanced cooking techniques like sous vide or grilling")
        
        # Add specific instructions based on foods
        for food in foods:
            if "salmon" in food["name"].lower():
                instructions.append(f"Pan-sear {food['name']} for 4-5 minutes per side")
            elif "beef" in food["name"].lower():
                instructions.append(f"Cook {food['name']} to desired doneness (medium-rare recommended)")
            elif "eggs" in food["name"].lower():
                instructions.append(f"Scramble or fry {food['name']} in grass-fed butter")
        
        return instructions
    
    def _get_personalized_supplements(self) -> Dict:
        """Get personalized supplement recommendations"""
        base_supplements = super()._get_daily_supplement_schedule()
        
        # Add custom supplements
        for custom_supp in self.custom_supplements:
            timing_key = custom_supp.timing.replace("_", " ")
            if timing_key not in base_supplements:
                base_supplements[timing_key] = []
            
            base_supplements[timing_key].append({
                "name": custom_supp.name,
                "dosage": custom_supp.dosage,
                "notes": custom_supp.notes
            })
        
        return base_supplements
    
    def _optimize_meal_timing(self, fasting_schedule: FastingSchedule) -> Dict:
        """Optimize meal timing for better results"""
        eating_window = 24 - fasting_schedule.fasting_duration
        
        recommendations = {
            "break_fast_with": "High-fat foods (MCT oil, avocado) to maintain ketosis",
            "pre_workout": "If exercising, consider BCAAs during fasting",
            "post_workout": "Prioritize protein within eating window",
            "last_meal_cutoff": "Stop eating 3 hours before sleep for better digestion"
        }
        
        if eating_window <= 4:  # OMAD
            recommendations["meal_composition"] = "Balance all macros in single meal"
        elif eating_window <= 8:  # Standard IF
            recommendations["first_meal"] = "Higher fat and protein"
            recommendations["last_meal"] = "Include some carbs for better sleep"
        
        return recommendations
    
    def export_custom_configuration(self, filename: str = "custom_if_config.json"):
        """Export custom foods and supplements configuration"""
        config = {
            "custom_foods": [food.__dict__ for food in self.custom_foods],
            "custom_supplements": [supp.__dict__ for supp in self.custom_supplements],
            "export_date": str(datetime.now())
        }
        
        with open(filename, 'w') as f:
            json.dump(config, f, indent=4)
        
        print(f"Custom configuration exported to: {filename}")
    
    def import_custom_configuration(self, filename: str):
        """Import custom foods and supplements from file"""
        try:
            with open(filename, 'r') as f:
                config = json.load(f)
            
            # Import custom foods
            for food_data in config.get("custom_foods", []):
                food = Food(**food_data)
                self.custom_foods.append(food)
            
            # Import custom supplements
            for supp_data in config.get("custom_supplements", []):
                supplement = Supplement(**supp_data)
                self.custom_supplements.append(supplement)
            
            print(f"Configuration imported from: {filename}")
            print(f"Imported {len(self.custom_foods)} custom foods and {len(self.custom_supplements)} custom supplements")
            
        except FileNotFoundError:
            print(f"Configuration file {filename} not found")
        except Exception as e:
            print(f"Error importing configuration: {e}")

def example_usage():
    """Example of how to use the advanced planner"""
    planner = AdvancedIFPlanner()
    
    # Define personal goals
    goals = NutritionalGoals(
        calories_per_day=1800,
        protein_percentage=0.25,  # 25%
        fat_percentage=0.65,      # 65%
        carb_percentage=0.10,     # 10%
        fiber_goal=25
    )
    
    # Define preferences
    preferences = PersonalPreferences(
        food_allergies=["dairy"],  # Example: lactose intolerant
        food_dislikes=["sardines"],
        preferred_cuisines=["Mediterranean", "Keto"],
        cooking_skill_level="intermediate",
        max_prep_time=25
    )
    
    # Add custom foods
    custom_food = Food(
        name="Grass-fed Butter",
        protein_per_100g=0.9,
        fat_per_100g=81.1,
        carbs_per_100g=0.1,
        calories_per_100g=717,
        serving_size="1 tbsp",
        meal_timing="anytime",
        preparation_time=0
    )
    planner.add_custom_food(custom_food)
    
    # Create fasting schedule
    fasting_schedule = FastingSchedule(
        eating_window_start="14:00",
        eating_window_end="20:00",
        fasting_duration=18  # 18:6 IF
    )
    
    # Create personalized plan
    personalized_plan = planner.create_personalized_meal_plan(
        fasting_schedule, goals, preferences
    )
    
    # Display results
    print("🎯 Personalized IF Meal Plan")
    print("=" * 30)
    print(f"Daily Calories: {personalized_plan['nutritional_targets']['daily_calories']}")
    print(f"Protein: {personalized_plan['nutritional_targets']['protein_grams']:.1f}g")
    print(f"Fat: {personalized_plan['nutritional_targets']['fat_grams']:.1f}g")
    print(f"Carbs: {personalized_plan['nutritional_targets']['carb_grams']:.1f}g")
    
    # Save personalized plan
    with open("personalized_if_plan.json", 'w') as f:
        json.dump(personalized_plan, f, indent=4, default=str)
    
    print("\nPersonalized plan saved to: personalized_if_plan.json")

if __name__ == "__main__":
    example_usage()