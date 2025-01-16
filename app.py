from flask import Flask, render_template, request, jsonify
import random
import time
import requests
from math import radians, sin, cos, sqrt, atan2

app = Flask(__name__)

# Mock data for food items
FOOD_ITEMS = ["Pizza", "Burger", "Sushi", "Pasta", "Salad"]

# Haversine function (no change)
def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371.0  # Radius of the Earth in kilometers
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

# Generate a mock order
def generate_mock_order(restaurant):
    order = {
        "restaurant": restaurant["name"],
        "order_time": time.strftime("%H:%M:%S"),
        "food_item": random.choice(FOOD_ITEMS),
        "quantity": random.randint(1, 5),
        "status": random.choice(["Pending", "Processing", "Completed"]),
    }
    return order

# Route for the homepage
@app.route('/')
def home():
    return render_template('index.html')

# API endpoint to fetch nearby restaurants and mock orders
@app.route('/get_nearby_restaurants', methods=['POST'])
def get_nearby_restaurants():
    try:
        lat = float(request.json['latitude'])
        lon = float(request.json['longitude'])
        radius = int(request.json['radius'])

        # API details
        url = "https://google-map-places.p.rapidapi.com/maps/api/place/nearbysearch/json"
        query_params = {
            "location": f"{lat},{lon}",
            "radius": str(radius),
            "type": "restaurant",
            "keyword": "restaurant"
        }
        headers = {
            "X-RapidAPI-Key": "f0bf44faafmshd94eaf4554f487ap1ec254jsn5e2be721029d",
            "X-RapidAPI-Host": "google-map-places.p.rapidapi.com"
        }

        # Make API request
        response = requests.get(url, headers=headers, params=query_params)

        if response.status_code == 200:
            places = response.json().get("results", [])
            closest_restaurant = None
            shortest_distance = float('inf')

            # Process restaurants
            restaurant_list = []
            for place in places:
                name = place["name"]
                vicinity = place["vicinity"]
                rating = place.get("rating", "N/A")
                location = place["geometry"]["location"]
                rest_lat, rest_lon = location["lat"], location["lng"]

                # Calculate distance
                distance = haversine_distance(lat, lon, rest_lat, rest_lon)

                if distance < shortest_distance:
                    shortest_distance = distance
                    closest_restaurant = {
                        "name": name,
                        "vicinity": vicinity,
                        "rating": rating,
                        "distance": distance
                    }

                restaurant_list.append({
                    'name': name,
                    'vicinity': vicinity,
                    'rating': rating,
                    'distance': f"{distance:.2f} km"
                })

            # Generate mock orders for all nearby restaurants
            mock_orders = [generate_mock_order(restaurant) for restaurant in restaurant_list]

            return jsonify({
                'restaurant_list': restaurant_list,
                'closest_restaurant': closest_restaurant,
                'mock_orders': mock_orders
            })

        else:
            return jsonify({'error': 'API Error', 'status_code': response.status_code})

    except ValueError:
        return jsonify({'error': 'Invalid input data'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run()
