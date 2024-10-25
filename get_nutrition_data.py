import requests
import pandas as pd

def get_nutrition(food_names):
    nutrition_data = pd.DataFrame(columns=['name', 'protein', 'calcium', 'fat', 'carbohydrates', 'vitamins'])
    
    for name in food_names:
        url = f"https://api.nal.usda.gov/fdc/v1/foods/search?api_key=pKs5ENGpUPMM9ZC2yCWz2MOJEhrMWM6yYHDDbIjK&query={name}"
        response = requests.get(url)
        
        if response.status_code != 200:
            print(f"Error fetching data for {name}: {response.status_code}")
            continue
        
        data = response.json()
        flatten_json = pd.json_normalize(data.get("foods", []))
        
        if flatten_json.empty:
            print(f"No data found for {name}.")
            continue

        first_food = flatten_json.iloc[0]
        first_food_nutrition_list = first_food.get('foodNutrients', [])
        
        # Initialize nutrient values
        protein = calcium = fat = carbs = vitamins = vitamin_a = vitamin_c = 0

        for item in first_food_nutrition_list:
            if item['nutrientNumber'] == "203":
                protein = item['value']
            elif item['nutrientNumber'] == "301":
                calcium = item['value'] / 1000  # Convert to grams
            elif item['nutrientNumber'] == "204":
                fat = item['value']
            elif item['nutrientNumber'] == "205":
                carbs = item['value']
            elif item['nutrientNumber'] == "318":
                vitamin_a = item['value']
            elif item['nutrientNumber'] == "401":
                vitamin_c = item['value']

        vitamins = float(vitamin_a) + float(vitamin_c)

        # Append the data to the DataFrame
        nutrition_data = nutrition_data.append({
            'name': name,
            'protein': protein,
            'calcium': calcium,
            'fat': fat,
            'carbohydrates': carbs,
            'vitamins': vitamins / 1000  # Adjust if needed
        }, ignore_index=True)

    return nutrition_data

