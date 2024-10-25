import streamlit as st
import numpy as np
import pandas as pd
import requests
from tensorflow.keras.preprocessing import image
from tensorflow.keras.models import load_model
import os

# Load your model
model = load_model('./best_model_101class.hdf5')

# Define the target size for the images
target_size = (200, 200)

# Function to load and preprocess images
def load_and_preprocess_image(img_path):
    img = image.load_img(img_path, target_size=target_size)
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension
    img_array /= 255.0  # Normalize to [0, 1]
    return img_array

# Function to get nutrition data
def get_nutrition(food_name):
    url = f"https://api.nal.usda.gov/fdc/v1/foods/search?api_key=pKs5ENGpUPMM9ZC2yCWz2MOJEhrMWM6yYHDDbIjK&query={food_name}"
    response = requests.get(url)
    
    if response.status_code != 200:
        return {"error": "Error fetching data"}
    
    data = response.json()
    flatten_json = pd.json_normalize(data["foods"])
    
    if flatten_json.empty:
        return {"error": "No data found"}

    first_food = flatten_json.iloc[0]
    first_food_nutrition_list = first_food.get('foodNutrients', [])

    # Initialize nutrient values
    protein = calcium = fat = carbs = vitamin_a = vitamin_c = 0
    
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

    vitamins = vitamin_a + vitamin_c
    return {
        'name': food_name,
        'protein': protein,
        'calcium': calcium,
        'fat': fat,
        'carbohydrates': carbs,
        'vitamins': vitamins / 1000  # Convert to grams
    }

# Streamlit application
st.title("Food Image Classification and Nutrition Info")

uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Save the uploaded file temporarily
    img_path = os.path.join("uploads", uploaded_file.name)
    with open(img_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Load and preprocess the image
    img_array = load_and_preprocess_image(img_path)

    # Predict the class
    predictions = model.predict(img_array)
    predicted_class_idx = np.argmax(predictions, axis=1)[0]

    # List of class labels
    class_labels = ['apple_pie', 'baby_back_ribs', 'baklava', 'beef_carpaccio', 'beef_tartare',
                    'beet_salad', 'beignets', 'bibimbap', 'bread_pudding', 'breakfast_burrito',
                    'bruschetta', 'caesar_salad', 'cannoli', 'caprese_salad', 'carrot_cake',
                    'ceviche', 'cheese_plate', 'cheesecake', 'chicken_curry', 'chicken_quesadilla',
                    'chicken_wings', 'chocolate_cake', 'chocolate_mousse', 'churros', 'clam_chowder',
                    'club_sandwich', 'crab_cakes', 'creme_brulee', 'croque_madame', 'cup_cakes',
                    'deviled_eggs', 'donuts', 'dumplings', 'edamame', 'eggs_benedict',
                    'escargots', 'falafel', 'filet_mignon', 'fish_and_chips', 'foie_gras',
                    'french_fries', 'french_onion_soup', 'french_toast', 'fried_calamari',
                    'fried_rice', 'frozen_yogurt', 'garlic_bread', 'gnocchi', 'greek_salad',
                    'grilled_cheese_sandwich', 'grilled_salmon', 'guacamole', 'gyoza',
                    'hamburger', 'hot_and_sour_soup', 'hot_dog', 'huevos_rancheros', 'hummus',
                    'ice_cream', 'lasagna', 'lobster_bisque', 'lobster_roll_sandwich',
                    'macaroni_and_cheese', 'macarons', 'miso_soup', 'mussels', 'nachos',
                    'omelette', 'onion_rings', 'oysters', 'pad_thai', 'paella', 'pancakes',
                    'panna_cotta', 'peking_duck', 'pho', 'pizza', 'pork_chop', 'poutine',
                    'prime_rib', 'pulled_pork_sandwich', 'ramen', 'ravioli', 'red_velvet_cake',
                    'risotto', 'samosa', 'sashimi', 'scallops', 'seaweed_salad', 'shrimp_and_grits',
                    'spaghetti_bolognese', 'spaghetti_carbonara', 'spring_rolls', 'steak',
                    'strawberry_shortcake', 'sushi', 'tacos', 'takoyaki', 'tiramisu', 'tuna_tartare', 'waffles']
    
    predicted_label = class_labels[predicted_class_idx]

    # Get nutritional information
    predicted_label_formatted = predicted_label.replace('_', ' ')
    nutrition_info = get_nutrition(predicted_label_formatted)

    # Display results
    st.write(f"**Predicted Food Item:** {predicted_label_formatted}")
    
    if "error" in nutrition_info:
        st.write(nutrition_info["error"])
    else:
        st.write(f"**Nutritional Information for {nutrition_info['name']}:**")
        st.write(f"- Protein: {nutrition_info['protein']} g")
        st.write(f"- Calcium: {nutrition_info['calcium']} g")
        st.write(f"- Fat: {nutrition_info['fat']} g")
        st.write(f"- Carbohydrates: {nutrition_info['carbohydrates']} g")
        st.write(f"- Vitamins: {nutrition_info['vitamins']} g")

    # Optional: Clean up by removing the uploaded file
    os.remove(img_path)
