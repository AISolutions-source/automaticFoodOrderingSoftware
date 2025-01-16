import requests
from math import radians, sin, cos, sqrt, atan2
import tkinter as tk
from tkinter import messagebox, ttk


def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate the great-circle distance between two points on the Earth."""
    R = 6371.0  # Radius of the Earth in kilometers
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c


def fetch_nearby_restaurants():
    """Fetch and display nearby restaurants based on user location."""
    try:
        lat = float(lat_entry.get())
        lon = float(lon_entry.get())
        radius = int(radius_entry.get())

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

            # Clear previous results
            results_list.delete(0, tk.END)

            # Display nearby restaurants
            for place in places:
                name = place["name"]
                vicinity = place["vicinity"]
                rating = place.get("rating", "N/A")

                # Get restaurant's location
                location = place["geometry"]["location"]
                rest_lat, rest_lon = location["lat"], location["lng"]

                # Calculate distance
                distance = haversine_distance(lat, lon, rest_lat, rest_lon)

                # Check for closest restaurant
                if distance < shortest_distance:
                    shortest_distance = distance
                    closest_restaurant = {
                        "name": name,
                        "vicinity": vicinity,
                        "rating": rating,
                        "distance": distance
                    }

                # Add to results list
                results_list.insert(tk.END, f"{name} - {vicinity} - Rating: {rating} - Distance: {distance:.2f} km")

            # Display closest restaurant
            if closest_restaurant:
                closest_label.config(
                    text=f"Closest: {closest_restaurant['name']} - {closest_restaurant['distance']:.2f} km"
                )
                messagebox.showinfo(
                    "Order Confirmation",
                    f"Food has been ordered from {closest_restaurant['name']}!"
                )
        else:
            messagebox.showerror("Error", f"API Error: {response.status_code}")

    except ValueError:
        messagebox.showerror("Input Error", "Please enter valid numeric values for latitude, longitude, and radius.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")


# GUI setup
root = tk.Tk()
root.title("Nearby Restaurant Finder")
root.geometry("600x400")

# Input fields
tk.Label(root, text="Latitude:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
lat_entry = tk.Entry(root)
lat_entry.grid(row=0, column=1, padx=10, pady=5)

tk.Label(root, text="Longitude:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
lon_entry = tk.Entry(root)
lon_entry.grid(row=1, column=1, padx=10, pady=5)

tk.Label(root, text="Search Radius (meters):").grid(row=2, column=0, padx=10, pady=5, sticky="e")
radius_entry = tk.Entry(root)
radius_entry.grid(row=2, column=1, padx=10, pady=5)

# Fetch button
fetch_button = tk.Button(root, text="Find Restaurants", command=fetch_nearby_restaurants)
fetch_button.grid(row=3, column=0, columnspan=2, pady=10)

# Results display
results_label = tk.Label(root, text="Nearby Restaurants:", font=("Arial", 12))
results_label.grid(row=4, column=0, columnspan=2, pady=5)

results_list = tk.Listbox(root, width=80, height=10)
results_list.grid(row=5, column=0, columnspan=2, padx=10, pady=5)

# Closest restaurant label
closest_label = tk.Label(root, text="", font=("Arial", 12, "bold"))
closest_label.grid(row=6, column=0, columnspan=2, pady=10)

# Start the GUI event loop
root.mainloop()
