🗺️ Intelligent Travel Itinerary Planner
This project is an intelligent travel agent that generates personalized, day-by-day travel itineraries. It takes a user's destination, budget, and travel dates as input, and uses various tools to create a comprehensive plan.

🚀 How It Works
- The core of the project is a planning agent that orchestrates a series of tools to create a cohesive itinerary. It follows these steps:
- Tourist Database (RAG): The agent first queries a local database (attractions.db) containing information about tourist attractions in various cities. This acts as a simplified Retrieval-Augmented Generation (RAG) tool to get initial information.
- Web Search Simulation: The agent then uses a simulated "web search" tool to find placeholder data for flight and hotel prices, as well as general pricing information for the destination (e.g., average meal cost, local transport).
- Planning Engine: With all the data gathered, a planning tool assembles a detailed, day-by-day itinerary. It distributes activities, calculates daily and total estimated costs, and provides recommendations for flights and hotels.
- Output Generation: Finally, the agent generates a formatted itinerary, a budget breakdown, and local tips, which are then saved to a travel_itineraries.json file.

📦 Project Structure
- The project is contained within a single Python script, travel_planner.py.
- TravelRequest, Attraction, etc.: Data classes used to structure the input and output.
- SimpleTouristDatabase: Manages a SQLite database to store and retrieve attraction information. It includes a basic relevance scoring system to match attractions with user interests.
- SimpleWebSearchTool: A mock class that simulates web searches for flights and hotels with hardcoded data.
- SimpleItineraryPlanner: The main class that orchestrates the entire process, from data gathering to itinerary generation.
- main(): An example function that demonstrates how to use the SimpleItineraryPlanner for multiple cities and prints the results to the console.

📋 Requirements
- This project requires Python 3.6 or higher. The only external dependency is the built-in sqlite3 module.

🛠️ Setup and Usage
- Clone the repository (if applicable) or save the travel_planner.py file.
- Run the script:
- python travel_planner.py
- The script will automatically create a database (attractions.db) and populate it with sample data on the first run.
- The generated itineraries will be printed to the console and saved to travel_itineraries.json.
- To customize your travel request, edit the main() function in travel_planner.py with your desired destination, dates, budget, and interests.

🤝 Contributing
- Fork the repository
- Create a feature branch (git checkout -b feature/amazing-feature)
- Commit your changes (git commit -m 'Add amazing feature')
- Push to the branch (git push origin feature/amazing-feature)
- Open a Pull Request


Update pricing: Adjust the hardcoded data in the SimpleWebSearchTool's flight_data, hotel_data, and pricing_data dictionaries.

Change logic: Modify the plan_daily_activities method to alter how the planner selects and organizes activities.
