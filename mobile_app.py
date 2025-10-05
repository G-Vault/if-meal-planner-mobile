"""
Android-compatible IF Meal Planner using Kivy
=============================================
Mobile version that reuses all existing meal planning logic
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.spinner import Spinner
from kivy.uix.switch import Switch
from kivy.uix.gridlayout import GridLayout
from kivy.storage.jsonstore import JsonStore
from kivy.clock import Clock
from kivy.uix.popup import Popup
from kivy.metrics import dp
import json

# Import your existing meal planning logic
from intro import IntermittentFastingPlanner, FastingSchedule
from meal_customizer import AdvancedIFPlanner, NutritionalGoals, PersonalPreferences

class PersonalTab(BoxLayout):
    def __init__(self, app_instance, **kwargs):
        super().__init__(orientation='vertical', padding=dp(10), spacing=dp(10), **kwargs)
        self.app = app_instance
        
        # Title
        title = Label(text='👤 Personal Details', font_size=dp(20), size_hint_y=None, height=dp(40))
        self.add_widget(title)
        
        # Personal details form
        form_layout = GridLayout(cols=2, spacing=dp(10), size_hint_y=None)
        form_layout.bind(minimum_height=form_layout.setter('height'))
        
        # Age
        form_layout.add_widget(Label(text='Age (years):', size_hint_y=None, height=dp(40)))
        self.age_input = TextInput(multiline=False, size_hint_y=None, height=dp(40), input_filter='int')
        form_layout.add_widget(self.age_input)
        
        # Weight
        form_layout.add_widget(Label(text='Weight (kg):', size_hint_y=None, height=dp(40)))
        self.weight_input = TextInput(multiline=False, size_hint_y=None, height=dp(40), input_filter='float')
        form_layout.add_widget(self.weight_input)
        
        # Height
        form_layout.add_widget(Label(text='Height (cm):', size_hint_y=None, height=dp(40)))
        self.height_input = TextInput(multiline=False, size_hint_y=None, height=dp(40), input_filter='int')
        form_layout.add_widget(self.height_input)
        
        # Gender
        form_layout.add_widget(Label(text='Gender:', size_hint_y=None, height=dp(40)))
        self.gender_spinner = Spinner(
            text='Select Gender',
            values=['Male', 'Female'],
            size_hint_y=None, height=dp(40)
        )
        form_layout.add_widget(self.gender_spinner)
        
        self.add_widget(form_layout)
        
        # Activity level
        activity_label = Label(text='Activity Level:', size_hint_y=None, height=dp(30))
        self.add_widget(activity_label)
        
        self.activity_spinner = Spinner(
            text='Select Activity Level',
            values=[
                'Sedentary (office job, minimal exercise)',
                'Light (desk job + light exercise)',
                'Moderate (some exercise, active lifestyle)',
                'Active (regular exercise, physical job)',
                'Very Active (intense exercise, physical job)'
            ],
            size_hint_y=None, height=dp(44)
        )
        self.add_widget(self.activity_spinner)
        
        # Calculate button
        calc_btn = Button(
            text='🧮 Auto-Calculate My Daily Calories',
            size_hint_y=None, height=dp(50),
            background_color=(0.2, 0.6, 1, 1)  # Blue color
        )
        calc_btn.bind(on_press=self.calculate_calories)
        self.add_widget(calc_btn)
        
        # Results label
        self.results_label = Label(
            text='Enter your details above and press Calculate',
            size_hint_y=None, height=dp(80),
            text_size=(None, None),
            halign='center'
        )
        self.add_widget(self.results_label)
        
        # Auto-save bindings
        self.age_input.bind(text=self.auto_save)
        self.weight_input.bind(text=self.auto_save)
        self.height_input.bind(text=self.auto_save)
        self.gender_spinner.bind(text=self.auto_save)
        self.activity_spinner.bind(text=self.auto_save)
    
    def calculate_calories(self, instance):
        try:
            age = int(self.age_input.text) if self.age_input.text else 0
            weight = float(self.weight_input.text) if self.weight_input.text else 0
            height = float(self.height_input.text) if self.height_input.text else 0
            gender = self.gender_spinner.text
            activity = self.activity_spinner.text
            
            if not all([age, weight, height, gender != 'Select Gender', activity != 'Select Activity Level']):
                self.results_label.text = '⚠️ Please fill in all fields'
                return
            
            # Use Mifflin-St Jeor equation (same as desktop version)
            if gender == "Male":
                bmr = 10 * weight + 6.25 * height - 5 * age + 5
            else:
                bmr = 10 * weight + 6.25 * height - 5 * age - 161
                
            # Activity multipliers
            activity_multipliers = {
                "Sedentary (office job, minimal exercise)": 1.2,
                "Light (desk job + light exercise)": 1.375,
                "Moderate (some exercise, active lifestyle)": 1.55,
                "Active (regular exercise, physical job)": 1.725,
                "Very Active (intense exercise, physical job)": 1.9
            }
            
            # Calculate TDEE
            tdee = bmr * activity_multipliers.get(activity, 1.55)
            recommended_calories = round(tdee / 50) * 50
            
            # Update results
            self.results_label.text = (
                f'✅ Calculation Complete!\n'
                f'BMR: {int(bmr)} calories/day\n'
                f'TDEE: {int(tdee)} calories/day\n'
                f'🎯 RECOMMENDED: {int(recommended_calories)} calories/day'
            )
            
            # Store for other tabs
            self.app.user_calories = int(recommended_calories)
            self.app.user_data = {
                'age': age, 'weight': weight, 'height': height,
                'gender': gender, 'activity': activity,
                'calories': int(recommended_calories)
            }
            
            self.auto_save()
            
        except ValueError:
            self.results_label.text = '❌ Please enter valid numbers for age, weight, and height'
    
    def auto_save(self, *args):
        """Auto-save preferences"""
        Clock.schedule_once(lambda dt: self.app.save_preferences(), 0.1)

class FoodPreferencesTab(BoxLayout):
    def __init__(self, app_instance, **kwargs):
        super().__init__(orientation='vertical', padding=dp(10), spacing=dp(10), **kwargs)
        self.app = app_instance
        
        # Title
        title = Label(text='🍽️ Food Preferences', font_size=dp(20), size_hint_y=None, height=dp(40))
        self.add_widget(title)
        
        # Fasting Schedule
        fasting_label = Label(text='Intermittent Fasting Schedule:', size_hint_y=None, height=dp(30))
        self.add_widget(fasting_label)
        
        self.fasting_spinner = Spinner(
            text='16:8 (Most Popular)',
            values=['16:8 (Most Popular)', '14:10 (Beginner)', '18:6 (Advanced)', '20:4 (Warrior Diet)', '23:1 (OMAD)'],
            size_hint_y=None, height=dp(44)
        )
        self.add_widget(self.fasting_spinner)
        
        # Eating window start time
        time_label = Label(text='Eating Window Start Time:', size_hint_y=None, height=dp(30))
        self.add_widget(time_label)
        
        self.start_time_spinner = Spinner(
            text='12:00',
            values=[f"{h:02d}:00" for h in range(6, 20)],
            size_hint_y=None, height=dp(44)
        )
        self.add_widget(self.start_time_spinner)
        
        # Food allergies
        allergies_label = Label(text='🚨 Food Allergies (comma-separated):', size_hint_y=None, height=dp(30))
        self.add_widget(allergies_label)
        
        self.allergies_input = TextInput(
            multiline=True, size_hint_y=None, height=dp(60),
            hint_text='e.g., nuts, dairy, shellfish'
        )
        self.add_widget(self.allergies_input)
        
        # Food dislikes
        dislikes_label = Label(text='👎 Food Dislikes (comma-separated):', size_hint_y=None, height=dp(30))
        self.add_widget(dislikes_label)
        
        self.dislikes_input = TextInput(
            multiline=True, size_hint_y=None, height=dp(60),
            hint_text='e.g., brussels sprouts, liver'
        )
        self.add_widget(self.dislikes_input)
        
        # Seasonal ingredients
        seasonal_label = Label(text='🌱 Seasonal/Preferred Ingredients:', size_hint_y=None, height=dp(30))
        self.add_widget(seasonal_label)
        
        self.seasonal_input = TextInput(
            multiline=True, size_hint_y=None, height=dp(60),
            hint_text='e.g., beetroot, turnips, asparagus'
        )
        self.add_widget(self.seasonal_input)
        
        # Auto-save bindings
        self.fasting_spinner.bind(text=self.auto_save)
        self.start_time_spinner.bind(text=self.auto_save)
        self.allergies_input.bind(text=self.auto_save)
        self.dislikes_input.bind(text=self.auto_save)
        self.seasonal_input.bind(text=self.auto_save)
    
    def auto_save(self, *args):
        Clock.schedule_once(lambda dt: self.app.save_preferences(), 0.1)

class MealPlanTab(BoxLayout):
    def __init__(self, app_instance, **kwargs):
        super().__init__(orientation='vertical', padding=dp(10), spacing=dp(10), **kwargs)
        self.app = app_instance
        
        # Header with generate button
        header = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
        
        title = Label(text='🍽️ Your 4-Day Meal Plan', font_size=dp(18))
        header.add_widget(title)
        
        generate_btn = Button(
            text='Generate Plan',
            size_hint_x=None, width=dp(120),
            background_color=(0.2, 0.8, 0.2, 1)  # Green color
        )
        generate_btn.bind(on_press=self.generate_meal_plan)
        header.add_widget(generate_btn)
        
        self.add_widget(header)
        
        # Scrollable meal plan display
        self.plan_scroll = ScrollView()
        self.plan_label = Label(
            text='Press "Generate Plan" to create your personalized 4-day meal plan!\n\n'
                 'Make sure to:\n'
                 '• Set your personal details in the Personal tab\n'
                 '• Configure food preferences in the Food tab\n'
                 '• Then generate your Scottish-optimized meal plan here!',
            text_size=(None, None),
            halign='left',
            valign='top'
        )
        self.plan_scroll.add_widget(self.plan_label)
        self.add_widget(self.plan_scroll)
    
    def generate_meal_plan(self, instance):
        if not hasattr(self.app, 'user_calories'):
            self.plan_label.text = '⚠️ Please calculate your calories first in the Personal tab!'
            return
        
        try:
            # Create fasting schedule
            fasting_type = self.app.food_tab.fasting_spinner.text.split(' ')[0]  # Extract "16:8" part
            start_time = self.app.food_tab.start_time_spinner.text
            
            fasting_schedule = FastingSchedule(
                fasting_hours=int(fasting_type.split(':')[0]),
                eating_hours=int(fasting_type.split(':')[1]),
                start_time=start_time
            )
            
            # Create nutritional goals
            goals = NutritionalGoals(
                calories_per_day=self.app.user_calories,
                protein_percentage=0.25,  # 25%
                fat_percentage=0.65,      # 65%
                carb_percentage=0.10      # 10%
            )
            
            # Create personal preferences
            allergies = [x.strip() for x in self.app.food_tab.allergies_input.text.split(',') if x.strip()]
            dislikes = [x.strip() for x in self.app.food_tab.dislikes_input.text.split(',') if x.strip()]
            seasonal = [x.strip() for x in self.app.food_tab.seasonal_input.text.split(',') if x.strip()]
            
            preferences = PersonalPreferences(
                allergies=allergies,
                dislikes=dislikes,
                preferred_foods=seasonal
            )
            
            # Generate meal plan using existing logic
            planner = AdvancedIFPlanner()
            meal_plan = planner.create_4_day_meal_plan(fasting_schedule, goals, preferences, seasonal)
            
            # Format for mobile display
            plan_text = self.format_meal_plan_for_mobile(meal_plan)
            self.plan_label.text = plan_text
            self.plan_label.text_size = (dp(350), None)  # Enable text wrapping
            
            # Store for shopping list
            self.app.current_meal_plan = meal_plan
            
        except Exception as e:
            self.plan_label.text = f'❌ Error generating meal plan: {str(e)}\n\nPlease check your inputs and try again.'
    
    def format_meal_plan_for_mobile(self, meal_plan):
        """Format meal plan for mobile display"""
        if not meal_plan or 'days' not in meal_plan:
            return '❌ No meal plan generated. Please try again.'
        
        text = '✅ YOUR 4-DAY SCOTTISH IF MEAL PLAN\n' + '='*40 + '\n\n'
        
        for day_info in meal_plan['days']:
            text += f"📅 {day_info['day'].upper()}\n"
            text += f"⏰ Eating Window: {day_info['eating_window']}\n\n"
            
            for meal in day_info['meals']:
                text += f"🍽️ {meal['name']} ({meal['calories']:.0f} cal)\n"
                for i, food in enumerate(meal['foods'], 1):
                    text += f"  {i}. {food['name']} ({food['serving']})\n"
                text += '\n'
            
            # Nutrition summary
            text += f"📊 Daily Totals:\n"
            text += f"  🔥 {day_info['total_calories']:.0f} calories\n"
            text += f"  💪 {day_info['total_protein']:.1f}g protein\n"
            text += f"  🥑 {day_info['total_fat']:.1f}g fat\n"
            text += f"  🌾 {day_info['total_carbs']:.1f}g carbs\n\n"
            
            # Cooking tips
            if 'cooking_tips' in day_info and day_info['cooking_tips']:
                text += "👨‍🍳 Cooking Tips:\n"
                for tip in day_info['cooking_tips']:
                    text += f"  • {tip}\n"
                text += '\n'
            
            text += '─'*30 + '\n\n'
        
        return text

class ShoppingTab(BoxLayout):
    def __init__(self, app_instance, **kwargs):
        super().__init__(orientation='vertical', padding=dp(10), spacing=dp(10), **kwargs)
        self.app = app_instance
        
        # Header with generate button
        header = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
        
        title = Label(text='🛒 Shopping List', font_size=dp(18))
        header.add_widget(title)
        
        generate_btn = Button(
            text='Generate List',
            size_hint_x=None, width=dp(120),
            background_color=(1, 0.5, 0, 1)  # Orange color
        )
        generate_btn.bind(on_press=self.generate_shopping_list)
        header.add_widget(generate_btn)
        
        self.add_widget(header)
        
        # Scrollable shopping list display
        self.shopping_scroll = ScrollView()
        self.shopping_label = Label(
            text='Generate a meal plan first, then create your shopping list!\n\n'
                 'The shopping list will include:\n'
                 '• Accurate quantities for 4 days\n'
                 '• Metric measurements (kg, grams)\n'
                 '• Scottish food names\n'
                 '• Organized by food category',
            text_size=(None, None),
            halign='left',
            valign='top'
        )
        self.shopping_scroll.add_widget(self.shopping_label)
        self.add_widget(self.shopping_scroll)
    
    def generate_shopping_list(self, instance):
        if not hasattr(self.app, 'current_meal_plan'):
            self.shopping_label.text = '⚠️ Please generate a meal plan first!'
            return
        
        try:
            # Generate shopping list using existing logic
            planner = AdvancedIFPlanner()
            shopping_list = planner.generate_shopping_list(self.app.current_meal_plan)
            
            # Format for mobile display
            shopping_text = self.format_shopping_list_for_mobile(shopping_list)
            self.shopping_label.text = shopping_text
            self.shopping_label.text_size = (dp(350), None)  # Enable text wrapping
            
        except Exception as e:
            self.shopping_label.text = f'❌ Error generating shopping list: {str(e)}'
    
    def format_shopping_list_for_mobile(self, shopping_list):
        """Format shopping list for mobile display"""
        if not shopping_list or 'categories' not in shopping_list:
            return '❌ No shopping list generated. Please try again.'
        
        text = '🛒 YOUR 4-DAY SHOPPING LIST\n' + '='*40 + '\n'
        text += '📍 Quantities in metric (perfect for Scotland!)\n\n'
        
        for category, items in shopping_list['categories'].items():
            if items:
                text += f"{category}:\n"
                for item in items:
                    text += f"  □ {item}\n"
                text += '\n'
        
        if 'cooking_tips' in shopping_list and shopping_list['cooking_tips']:
            text += '👨‍🍳 COOKING TIPS:\n' + '─'*20 + '\n'
            for tip in shopping_list['cooking_tips']:
                text += f"• {tip}\n"
            text += '\n'
        
        text += f"📅 Generated: {shopping_list.get('generated_date', 'Today')}\n"
        text += '🏴󠁧󠁢󠁳󠁣󠁴󠁿 Optimized for Scottish shoppers!'
        
        return text

class IFPlannerMobileApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.store = JsonStore('if_preferences.json')
        self.user_calories = None
        self.user_data = {}
        self.current_meal_plan = None
        
    def build(self):
        # Main tabbed interface
        main_tabs = TabbedPanel(do_default_tab=False, tab_height=dp(50))
        
        # Personal Details Tab
        personal_tab = TabbedPanelItem(text='👤 Personal')
        self.personal_tab = PersonalTab(self)
        personal_scroll = ScrollView()
        personal_scroll.add_widget(self.personal_tab)
        personal_tab.add_widget(personal_scroll)
        main_tabs.add_widget(personal_tab)
        
        # Food Preferences Tab
        food_tab = TabbedPanelItem(text='🍽️ Food')
        self.food_tab = FoodPreferencesTab(self)
        food_scroll = ScrollView()
        food_scroll.add_widget(self.food_tab)
        food_tab.add_widget(food_scroll)
        main_tabs.add_widget(food_tab)
        
        # Meal Plan Tab
        plan_tab = TabbedPanelItem(text='📋 Plan')
        self.plan_tab = MealPlanTab(self)
        plan_tab.add_widget(self.plan_tab)
        main_tabs.add_widget(plan_tab)
        
        # Shopping List Tab
        shopping_tab = TabbedPanelItem(text='🛒 Shop')
        self.shopping_tab = ShoppingTab(self)
        shopping_tab.add_widget(self.shopping_tab)
        main_tabs.add_widget(shopping_tab)
        
        # Load saved preferences
        Clock.schedule_once(lambda dt: self.load_preferences(), 0.5)
        
        return main_tabs
    
    def save_preferences(self):
        """Save all preferences to storage"""
        try:
            preferences = {
                'age': self.personal_tab.age_input.text,
                'weight': self.personal_tab.weight_input.text,
                'height': self.personal_tab.height_input.text,
                'gender': self.personal_tab.gender_spinner.text,
                'activity': self.personal_tab.activity_spinner.text,
                'fasting_type': self.food_tab.fasting_spinner.text,
                'start_time': self.food_tab.start_time_spinner.text,
                'allergies': self.food_tab.allergies_input.text,
                'dislikes': self.food_tab.dislikes_input.text,
                'seasonal': self.food_tab.seasonal_input.text,
                'calories': getattr(self, 'user_calories', None)
            }
            
            self.store.put('user_preferences', **preferences)
            
        except Exception as e:
            print(f"Error saving preferences: {e}")
    
    def load_preferences(self):
        """Load saved preferences"""
        try:
            if self.store.exists('user_preferences'):
                prefs = self.store.get('user_preferences')
                
                # Load personal details
                self.personal_tab.age_input.text = prefs.get('age', '')
                self.personal_tab.weight_input.text = prefs.get('weight', '')
                self.personal_tab.height_input.text = prefs.get('height', '')
                
                if prefs.get('gender') and prefs['gender'] != 'Select Gender':
                    self.personal_tab.gender_spinner.text = prefs['gender']
                    
                if prefs.get('activity') and prefs['activity'] != 'Select Activity Level':
                    self.personal_tab.activity_spinner.text = prefs['activity']
                
                # Load food preferences
                if prefs.get('fasting_type'):
                    self.food_tab.fasting_spinner.text = prefs['fasting_type']
                if prefs.get('start_time'):
                    self.food_tab.start_time_spinner.text = prefs['start_time']
                    
                self.food_tab.allergies_input.text = prefs.get('allergies', '')
                self.food_tab.dislikes_input.text = prefs.get('dislikes', '')
                self.food_tab.seasonal_input.text = prefs.get('seasonal', '')
                
                # Load calculated calories
                if prefs.get('calories'):
                    self.user_calories = prefs['calories']
                    self.personal_tab.results_label.text = f'🎯 Saved: {self.user_calories} calories/day\n(Tap Calculate to recalculate)'
                
        except Exception as e:
            print(f"Error loading preferences: {e}")

if __name__ == '__main__':
    IFPlannerMobileApp().run()