# IF Meal Planner - Android App

🍽️ A comprehensive Intermittent Fasting meal planner optimized for Scottish users.

## Features

- 🧮 **Automatic Calorie Calculation** - BMR/TDEE based on personal details
- ⏰ **Flexible Fasting Schedules** - 16:8, 18:6, 20:4, OMAD support
- 🍽️ **4-Day Meal Plans** - Personalized high-fat, low-carb meals
- 🛒 **Smart Shopping Lists** - Metric measurements, Scottish food names
- 🌱 **Seasonal Ingredients** - Prioritizes local produce like beetroot, turnips
- 💾 **Auto-Save Preferences** - Never lose your settings
- 👨‍🍳 **Enhanced Cooking Tips** - Detailed instructions with temperatures and timing
- 🏴󠁧󠁢󠁳󠁣󠁴󠁿 **Scottish Optimized** - Courgette not zucchini, kg not lbs, °C not °F

## Screenshots

*Mobile-optimized interface with touch-friendly tabs and scrollable content*

## Download

Get the latest Android APK from the [Releases](../../releases) section or build it yourself using GitHub Actions.

## Building

This repository uses GitHub Actions to automatically build Android APKs. Every push triggers a new build.

### Manual Build
```bash
pip install buildozer
buildozer android debug
```

## Installation

1. Enable "Unknown Sources" in Android Settings → Security
2. Download the APK file
3. Tap the APK to install
4. Open the "IF Meal Planner" app

## Requirements

- Android 5.0+ (API 21+)
- ~50MB storage space
- Internet permission for initial setup

## How to Use

1. **Personal Tab** - Enter your age, weight, height, and activity level
2. **Food Tab** - Set your fasting schedule and food preferences
3. **Plan Tab** - Generate your personalized 4-day meal plan
4. **Shop Tab** - Get your metric shopping list with accurate quantities

## Scottish Food Database

Includes local favorites and terminology:
- **Vegetables**: Courgette, aubergine, rocket, beetroot, turnips, swede
- **Dairy**: Double cream, mature cheddar, Scottish cheese varieties
- **Measurements**: All quantities in kilograms, grams, and Celsius
- **Seasonal Support**: Prioritizes Scottish seasonal produce

## Meal Planning Features

- **High-Fat Low-Carb Focus** - Perfect for ketogenic IF
- **Macro Tracking** - 25% protein, 65% fat, 10% carbs
- **Portion Control** - Accurate serving sizes in metric
- **Variety** - Different meals each day to prevent boredom
- **Shopping Integration** - Exact quantities needed for 4 days

## Technical Details

- Built with **Kivy** for cross-platform mobile development
- Uses **Python 3.9+** with scientific meal planning algorithms
- **Mifflin-St Jeor equation** for accurate calorie calculation
- **Local storage** for preferences (no cloud dependency)
- **Offline functionality** once installed

## Privacy

- All data stored locally on your device
- No personal information transmitted
- No tracking or analytics
- Your meal plans and preferences stay private

## Support

For issues or feature requests, please open an issue in this repository.

## License

Built with ❤️ for the Scottish IF community!

---

*This app provides nutritional guidance and meal suggestions. Please consult with healthcare professionals for personalized dietary advice.*