import json
import datetime
from flask import Flask, jsonify, request, render_template

app = Flask(__name__)

def convert_to_metric(weight, height, weight_unit, height_unit):
    if weight_unit == 'lbs':
        weight = weight * 0.453592  # Convert lbs to kg
    if height_unit == 'ft_in':
        feet, inches = map(float, height.split('_'))
        height = (feet * 30.48) + (inches * 2.54)  # Convert feet and inches to cm
    return weight, height

def calculate_calorie_adjustment(weekly_goal):
    if not -2 <= weekly_goal <= 2:
        raise ValueError("Weekly goal must be between -2kg and 2kg.")
    daily_calorie_adjustment = (weekly_goal * 7700) / 7
    return int(daily_calorie_adjustment)

def generate_generic_diet_plan(calories, diet_type):
    sample_meals = {
        "vegan": [
            {"Breakfast": "Oatmeal with almond milk and berries", "Calories": 350},
            {"Lunch": "Quinoa salad with chickpeas and veggies", "Calories": 500},
            {"Dinner": "Stir-fried tofu with broccoli and brown rice", "Calories": 650},
            {"Snacks": "Hummus with carrot sticks", "Calories": 200}
        ],
        "vegetarian": [
            {"Breakfast": "Greek yogurt with granola and honey", "Calories": 400},
            {"Lunch": "Vegetable pasta with tomato sauce", "Calories": 550},
            {"Dinner": "Eggplant parmesan with a side salad", "Calories": 650},
            {"Snacks": "Cheese and whole-grain crackers", "Calories": 200}
        ],
        "keto": [
            {"Breakfast": "Scrambled eggs with avocado and bacon", "Calories": 400},
            {"Lunch": "Grilled chicken salad with olive oil dressing", "Calories": 550},
            {"Dinner": "Salmon with asparagus and butter", "Calories": 600},
            {"Snacks": "Mixed nuts", "Calories": 200}
        ],
        "paleo": [
            {"Breakfast": "Sweet potato hash with eggs", "Calories": 400},
            {"Lunch": "Grilled steak with a mixed greens salad", "Calories": 600},
            {"Dinner": "Roasted chicken with steamed vegetables", "Calories": 700},
            {"Snacks": "Apple slices with almond butter", "Calories": 200}
        ]
    }

    total_calories = 0
    plan = []

    for meal in sample_meals.get(diet_type, []):
        if total_calories + meal["Calories"] <= calories:
            plan.append(meal)
            total_calories += meal["Calories"]

    return {
        "Diet Type": diet_type,
        "Calories": total_calories,
        "Meals": plan
    }

def create_diet_plan(name, age, weight, height, goal, calorie_adjustment, meals, snacks, diet_type):
    bmr = 10 * weight + 6.25 * height - 5 * age + 5 
    calories = bmr + calorie_adjustment
    calories_per_meal = calories / (meals + snacks)

    meal_plan = {
        "Meals": [f"Meal {i+1}: {calories_per_meal:.0f} kcal" for i in range(meals)],
        "Snacks": [f"Snack {i+1}: {calories_per_meal:.0f} kcal" for i in range(snacks)],
        "Total Calories": calories
    }

    generic_plan = generate_generic_diet_plan(calories, diet_type)

    return json.dumps({
        "Name": name,
        "Age": age,
        "Weight": weight,
        "Height": height,
        "Goal": goal,
        "Diet Type": diet_type,
        "Meal Plan": meal_plan,
        "Generic Plan": generic_plan
    }, indent=4)

def track_calories(food_database):
    print("\nTrack your calories for the day:")
    total_calories = 0
    while True:
        food = input("Enter food item (or type 'done' to finish): ").lower()
        if food == 'done':
            break
        if food in food_database:
            calories = food_database[food]
            print(f"{food.title()} - {calories} kcal per serving")
            servings = float(input(f"Enter number of servings for {food}: "))
            total_calories += calories * servings
            print(f"{food.title()} added. Total calories so far: {total_calories:.0f} kcal.")
        else:
            print("Food item not found in database. Please add manually.")
            calories = float(input(f"Enter calories for {food}: "))
            servings = float(input(f"Enter number of servings for {food}: "))
            total_calories += calories * servings
            print(f"{food.title()} added manually. Total calories so far: {total_calories:.0f} kcal.")
    print(f"\nTotal calories consumed today: {total_calories:.0f} kcal.")
    return total_calories

def update_weight_log(weight_log, current_weight):
    date = datetime.date.today().isoformat()
    weight_log[date] = current_weight
    return weight_log

def display_progress(weight_log):
    print("\nWeight Progress:")
    for date, weight in sorted(weight_log.items()):
        print(f"{date}: {weight:.1f} kg")

def set_goals():
    while True:
        try:
            weekly_goal = float(input("Set your weekly weight goal (e.g., -0.5 to -2 for weight loss or 0.5 to 2 for weight gain): "))
            if -2 <= weekly_goal <= 2:
                break
            else:
                print("Weekly goal must be between -2kg and 2kg.")
        except ValueError:
            print("Invalid input. Please enter a number.")
    return weekly_goal

food_database = {
    "grilled chicken breast": 165,
    "grilled chicken wings": 203,
    "fried chicken breast": 285,
    "fried chicken wings": 294,
    "steamed chicken breast": 150,
    "boiled chicken breast": 165,
    "grilled salmon": 208,
    "baked salmon": 206,
    "fried salmon": 240,
    "grilled tuna": 132,
    "baked tuna": 132,
    "boiled tuna": 130,
    "grilled shrimp": 85,
    "boiled shrimp": 99,
    "steamed shrimp": 85,
    "grilled fish fillet": 180,
    "baked fish fillet": 170,
    "boiled fish fillet": 165,
    "grilled veggie skewers": 100,
    "baked veggie skewers": 95,
    "steamed broccoli": 55,
    "boiled broccoli": 50,
    "grilled broccoli": 60,
    "raw broccoli": 35,
    "grilled bell peppers": 40,
    "baked bell peppers": 45,
    "steamed bell peppers": 50,
    "raw bell peppers": 30,
    "grilled asparagus": 60,
    "steamed asparagus": 50,
    "boiled asparagus": 55,
    "raw asparagus": 20,
    "baked sweet potato": 90,
    "boiled sweet potato": 86,
    "mashed sweet potato": 120,
    "fried sweet potato fries": 200,
    "baked potatoes": 95,
    "boiled potatoes": 77,
    "french fries": 312,
    "steamed green beans": 40,
    "baked green beans": 45,
    "boiled green beans": 50,
    "grilled green beans": 55,
    "grilled mushrooms": 22,
    "baked mushrooms": 35,
    "steamed mushrooms": 25,
    "raw mushrooms": 15,
    "raw carrots": 41,
    "steamed carrots": 30,
    "baked carrots": 35,
    "grilled carrots": 40,
    "boiled carrots": 38,
    "grilled tofu": 144,
    "fried tofu": 190,
    "boiled tofu": 70,
    "raw tofu": 76,
    "grilled tempeh": 192,
    "fried tempeh": 210,
    "boiled tempeh": 193,
    "raw tempeh": 193,
    "almond milk": 17,
    "coconut milk": 230,
    "soy milk": 44,
    "oat milk": 46,
    "rice milk": 49,
    "whole milk": 61,
    "skim milk": 34,
    "caffeinated coffee": 2,
    "black tea": 0,
    "green tea": 0,
    "herbal tea": 1,
    "orange juice": 45,
    "apple juice": 46,
    "carrot juice": 39,
    "tomato juice":