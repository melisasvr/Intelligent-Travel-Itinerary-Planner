import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class TravelRequest:
    destination: str
    budget: float
    start_date: str
    end_date: str
    travelers: int = 1
    interests: List[str] = None

@dataclass
class Attraction:
    name: str
    description: str
    category: str
    rating: float
    price_range: str
    duration: str
    location: str
    tags: List[str] = None
    city: str = None  # Add city field for explicit matching

@dataclass
class FlightOption:
    airline: str
    departure: str
    arrival: str
    price: float
    duration: str

@dataclass
class HotelOption:
    name: str
    rating: float
    price_per_night: float
    location: str
    amenities: List[str]

@dataclass
class DayItinerary:
    day: int
    date: str
    activities: List[Dict]
    estimated_cost: float
    notes: str

class SimpleTouristDatabase:
    """Simple tourist attraction database without ML dependencies"""
    
    def __init__(self, db_path: str = "attractions.db"):
        self.db_path = db_path
        self.attractions = []
        self.setup_database()
        
    def setup_database(self):
        """Initialize the database and load sample data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS attractions (
                id INTEGER PRIMARY KEY,
                name TEXT,
                city TEXT,
                description TEXT,
                category TEXT,
                rating REAL,
                price_range TEXT,
                duration TEXT,
                location TEXT,
                tags TEXT
            )
        ''')
        
        # Sample data for multiple cities (Tokyo removed)
        sample_attractions = [
            # Paris, France
            ("Eiffel Tower", "Paris", "Iconic iron lattice tower and symbol of Paris", "landmark", 4.5, "$", "2-3 hours", "Champ de Mars", "tower,landmark,romantic,architecture,views"),
            ("Louvre Museum", "Paris", "World's largest art museum housing the Mona Lisa", "museum", 4.6, "$$", "3-4 hours", "Rue de Rivoli", "museum,art,culture,mona lisa,history"),
            ("Notre-Dame Cathedral", "Paris", "Medieval Catholic cathedral with Gothic architecture", "religious", 4.4, "Free", "1-2 hours", "Île de la Cité", "cathedral,gothic,religious,architecture,historic"),
            # London, England
            ("Big Ben", "London", "Iconic clock tower at Palace of Westminster", "landmark", 4.5, "$", "1 hour", "Westminster", "clock,tower,parliament,iconic,historic"),
            ("British Museum", "London", "World-famous museum with historical artifacts", "museum", 4.7, "Free", "3-4 hours", "Bloomsbury", "museum,history,artifacts,culture,education"),
            ("Tower of London", "London", "Historic castle housing the Crown Jewels", "historic", 4.4, "$", "2-3 hours", "Tower Hamlets", "castle,crown jewels,historic,medieval,fortress"),
            # Rome, Italy
            ("Colosseum", "Rome", "Ancient amphitheater and iconic symbol of Rome", "historic", 4.6, "$$", "2-3 hours", "Palatine Hill", "colosseum,gladiators,ancient,roman,amphitheater"),
            ("Vatican City", "Rome", "Papal enclave with Sistine Chapel and St. Peter's", "religious", 4.8, "$$", "4-6 hours", "Vatican", "vatican,sistine chapel,pope,religious,art"),
            ("Trevi Fountain", "Rome", "Baroque fountain where coins bring good luck", "landmark", 4.4, "Free", "30 minutes", "Quirinale", "fountain,baroque,coins,wishes,romantic"),
            # Milan, Italy
            ("Milan Cathedral (Duomo)", "Milan", "Gothic cathedral with elaborate spires", "religious", 4.6, "$", "2-3 hours", "Piazza del Duomo", "duomo,gothic,cathedral,spires,architecture"),
            ("La Scala Opera House", "Milan", "World-famous opera house and museum", "cultural", 4.5, "$$", "1-2 hours", "Brera", "opera,theater,music,culture,performance"),
            # Madrid, Spain
            ("Prado Museum", "Madrid", "Premier art museum with Spanish masterpieces", "museum", 4.7, "$$", "3-4 hours", "Centro", "museum,art,spanish masters,goya,velazquez"),
            ("Royal Palace", "Madrid", "Baroque royal palace with opulent rooms", "historic", 4.4, "$", "2-3 hours", "Centro", "palace,royal,baroque,luxury,spanish royalty"),
            # Barcelona, Spain
            ("Sagrada Familia", "Barcelona", "Gaudi's unfinished basilica masterpiece", "religious", 4.8, "$$", "2-3 hours", "Eixample", "gaudi,basilica,modernist,architecture,unesco"),
            ("Park Güell", "Barcelona", "Whimsical park designed by Antoni Gaudí", "park", 4.6, "$", "2-3 hours", "Gràcia", "gaudi,park,mosaic,architecture,views"),
            # Berlin, Germany
            ("Brandenburg Gate", "Berlin", "18th-century neoclassical monument", "landmark", 4.5, "Free", "30 minutes", "Mitte", "gate,neoclassical,historic,symbol,unity"),
            ("Museum Island", "Berlin", "UNESCO site with five world-class museums", "museum", 4.6, "$$", "4-6 hours", "Mitte", "museums,unesco,art,history,culture"),
            # Cologne, Germany
            ("Cologne Cathedral", "Cologne", "Gothic cathedral and UNESCO World Heritage site", "religious", 4.7, "Free", "1-2 hours", "Innenstadt", "cathedral,gothic,unesco,twin towers,religious"),
            # Amsterdam, Netherlands
            ("Anne Frank House", "Amsterdam", "Museum in Anne Frank's hiding place", "museum", 4.4, "$$", "1-2 hours", "Jordaan", "anne frank,museum,wwii,history,moving"),
            ("Van Gogh Museum", "Amsterdam", "World's largest Van Gogh art collection", "museum", 4.6, "$$", "2-3 hours", "Museumplein", "van gogh,art,paintings,museum,impressionist"),
            # Prague, Czech Republic
            ("Prague Castle", "Prague", "Largest ancient castle complex in the world", "historic", 4.6, "$", "3-4 hours", "Hradčany", "castle,historic,complex,views,royal"),
            ("Charles Bridge", "Prague", "Historic stone bridge with statues", "landmark", 4.5, "Free", "1 hour", "Malá Strana", "bridge,historic,statues,vltava,iconic"),
            ("Old Town Square", "Prague", "Medieval square with astronomical clock", "landmark", 4.4, "Free", "1-2 hours", "Old Town", "square,medieval,astronomical clock,historic,central"),
            # Vienna, Austria
            ("Schönbrunn Palace", "Vienna", "Former imperial summer residence", "historic", 4.7, "$$", "3-4 hours", "Hietzing", "palace,imperial,gardens,unesco,royal"),
            ("St. Stephen's Cathedral", "Vienna", "Gothic cathedral with a distinctive roof", "religious", 4.6, "Free", "1-2 hours", "Innere Stadt", "cathedral,gothic,historic,church,architecture"),
            # New York
            ("Central Park", "New York", "Large public park in Manhattan", "park", 4.7, "Free", "2-4 hours", "Manhattan", "park,nature,walking,picnic,peaceful"),
            ("Statue of Liberty", "New York", "Neoclassical sculpture on Liberty Island", "landmark", 4.5, "$$", "3-4 hours", "Liberty Island", "landmark,statue,liberty,historic,patriotic")
        ]
        
        for attraction in sample_attractions:
            cursor.execute('''INSERT OR IGNORE INTO attractions 
                             (name, city, description, category, rating, price_range, duration, location, tags) 
                             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', attraction)
        
        conn.commit()
        conn.close()
        
        self.load_attractions()
    
    def load_attractions(self):
        """Load attractions from database into memory"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM attractions')
        rows = cursor.fetchall()
        
        self.attractions = []
        for row in rows:
            attraction = Attraction(
                name=row[1],
                city=row[2],  # Store city explicitly
                description=row[3],
                category=row[4],
                rating=row[5],
                price_range=row[6],
                duration=row[7],
                location=row[8],
                tags=row[9].split(',') if row[9] else []
            )
            self.attractions.append(attraction)
        
        conn.close()
    
    def search_attractions(self, city: str, query: str = "", interests: List[str] = None, top_k: int = 10) -> List[Attraction]:
        """Search for attractions using city field and optional query/interests"""
        # Filter by city (case-insensitive exact match on city field)
        city = city.strip().capitalize()  # Normalize city name
        city_attractions = [a for a in self.attractions if a.city.lower() == city.lower()]
        
        if not city_attractions:
            print(f"⚠️ No attractions found for {city}")
            return []
        
        # If no query or interests, return top-rated attractions
        if not query and not interests:
            return sorted(city_attractions, key=lambda x: x.rating, reverse=True)[:top_k]
        
        # Score attractions based on query and interests
        scored_attractions = []
        for attraction in city_attractions:
            score = self.calculate_relevance_score(attraction, query, interests or [])
            scored_attractions.append((attraction, score))
        
        # Sort by score and return top k
        scored_attractions.sort(key=lambda x: x[1], reverse=True)
        return [attraction for attraction, score in scored_attractions[:top_k]]
    
    def calculate_relevance_score(self, attraction: Attraction, query: str, interests: List[str]) -> float:
        """Calculate relevance score for an attraction"""
        score = attraction.rating  # Base score from rating
        
        # Text fields to search in
        searchable_text = " ".join([
            attraction.name,
            attraction.description,
            attraction.category,
            attraction.location,
            " ".join(attraction.tags)
        ]).lower()
        
        # Query matching
        if query:
            query_lower = query.lower()
            query_words = query_lower.split()
            for word in query_words:
                if word in searchable_text:
                    score += 1.0
                elif any(word in text_word for text_word in searchable_text.split()):
                    score += 0.5
        
        # Interest matching
        for interest in interests:
            interest_lower = interest.lower()
            if interest_lower in searchable_text:
                score += 2.0
            elif interest_lower in attraction.category.lower():
                score += 1.5
            elif any(interest_lower in tag for tag in attraction.tags):
                score += 1.0
        
        return score

class SimpleWebSearchTool:
    """Simplified web search tool for flights and hotels"""
    
    def __init__(self):
        self.flight_data = {
            "Paris": [
                FlightOption("Air France", "8:00 AM", "2:00 PM", 485.00, "6h 0m"),
                FlightOption("Delta", "10:30 AM", "4:45 PM", 520.00, "6h 15m"),
            ],
            "London": [
                FlightOption("British Airways", "9:00 AM", "3:00 PM", 380.00, "6h 0m"),
                FlightOption("Virgin Atlantic", "1:30 PM", "7:45 PM", 420.00, "6h 15m"),
            ],
            "Rome": [
                FlightOption("Alitalia", "8:30 AM", "3:15 PM", 420.00, "6h 45m"),
                FlightOption("Delta", "11:00 AM", "5:45 PM", 445.00, "6h 45m"),
            ],
            "Milan": [
                FlightOption("Alitalia", "7:45 AM", "2:30 PM", 395.00, "6h 45m"),
                FlightOption("Lufthansa", "12:30 PM", "7:15 PM", 415.00, "6h 45m"),
            ],
            "Madrid": [
                FlightOption("Iberia", "9:15 AM", "3:30 PM", 365.00, "6h 15m"),
                FlightOption("Air Europa", "1:45 PM", "8:00 PM", 340.00, "6h 15m"),
            ],
            "Barcelona": [
                FlightOption("Vueling", "8:00 AM", "2:15 PM", 320.00, "6h 15m"),
                FlightOption("Iberia", "12:00 PM", "6:15 PM", 345.00, "6h 15m"),
            ],
            "Berlin": [
                FlightOption("Lufthansa", "8:30 AM", "2:00 PM", 410.00, "5h 30m"),
                FlightOption("Air Berlin", "1:15 PM", "6:45 PM", 385.00, "5h 30m"),
            ],
            "Cologne": [
                FlightOption("Lufthansa", "7:00 AM", "12:30 PM", 380.00, "5h 30m"),
                FlightOption("Eurowings", "2:45 PM", "8:15 PM", 295.00, "5h 30m"),
            ],
            "Amsterdam": [
                FlightOption("KLM", "8:15 AM", "1:30 PM", 395.00, "5h 15m"),
                FlightOption("Delta", "12:45 PM", "6:00 PM", 415.00, "5h 15m"),
            ],
            "Prague": [
                FlightOption("Czech Airlines", "9:00 AM", "2:15 PM", 350.00, "5h 15m"),
                FlightOption("Lufthansa", "1:30 PM", "6:45 PM", 385.00, "5h 15m"),
            ],
            "Vienna": [
                FlightOption("Austrian Airlines", "8:45 AM", "2:00 PM", 390.00, "5h 15m"),
                FlightOption("Lufthansa", "12:00 PM", "5:15 PM", 415.00, "5h 15m"),
            ],
            "New York": [
                FlightOption("JetBlue", "7:30 AM", "10:45 AM", 320.00, "3h 15m"),
                FlightOption("Delta", "2:00 PM", "5:20 PM", 380.00, "3h 20m"),
            ]
        }
        
        self.hotel_data = {
            "Paris": [
                HotelOption("Le Grand Hotel Paris", 4.7, 285.00, "Opera District", ["WiFi", "Spa", "Restaurant"]),
                HotelOption("Budget Inn Paris", 3.8, 95.00, "République", ["WiFi", "Breakfast"]),
            ],
            "London": [
                HotelOption("The London Grand", 4.5, 220.00, "Westminster", ["WiFi", "Restaurant", "Bar"]),
                HotelOption("Budget London Central", 3.6, 105.00, "King's Cross", ["WiFi", "Breakfast"]),
            ],
            "Rome": [
                HotelOption("Hotel Rome Splendour", 4.6, 245.00, "Trevi District", ["WiFi", "Restaurant", "Rooftop Terrace"]),
                HotelOption("Budget Rome Central", 3.7, 85.00, "Termini", ["WiFi", "Breakfast"]),
            ],
            "Milan": [
                HotelOption("Milano Fashion Hotel", 4.5, 265.00, "Quadrilatero della Moda", ["WiFi", "Restaurant", "Gym"]),
                HotelOption("Budget Milan", 3.5, 75.00, "Centrale Station", ["WiFi", "Breakfast"]),
            ],
            "Madrid": [
                HotelOption("Hotel Madrid Royal", 4.4, 185.00, "Sol", ["WiFi", "Restaurant", "Flamenco Shows"]),
                HotelOption("Budget Madrid", 3.6, 70.00, "Lavapiés", ["WiFi", "Breakfast"]),
            ],
            "Barcelona": [
                HotelOption("Hotel Barcelona Gaudí", 4.5, 205.00, "Eixample", ["WiFi", "Gaudí Tours", "Restaurant"]),
                HotelOption("Budget Barcelona", 3.8, 85.00, "Gràcia", ["WiFi", "Breakfast"]),
            ],
            "Berlin": [
                HotelOption("Hotel Berlin Mitte", 4.4, 165.00, "Mitte", ["WiFi", "Restaurant", "Modern Design"]),
                HotelOption("Budget Berlin", 3.7, 65.00, "Kreuzberg", ["WiFi", "Breakfast"]),
            ],
            "Cologne": [
                HotelOption("Cathedral View Hotel", 4.5, 155.00, "Dom Area", ["WiFi", "Cathedral Views", "Restaurant"]),
                HotelOption("Budget Cologne", 3.6, 55.00, "Ehrenfeld", ["WiFi", "Breakfast"]),
            ],
            "Amsterdam": [
                HotelOption("Canal House Amsterdam", 4.6, 225.00, "Grachtengordel", ["WiFi", "Canal Views", "Breakfast"]),
                HotelOption("Budget Amsterdam", 3.8, 85.00, "Noord", ["WiFi", "Breakfast"]),
            ],
            "Prague": [
                HotelOption("Golden Prague Hotel", 4.5, 125.00, "Old Town", ["WiFi", "Castle Views", "Restaurant"]),
                HotelOption("Budget Prague", 3.7, 45.00, "New Town", ["WiFi", "Breakfast"]),
            ],
            "Vienna": [
                HotelOption("Imperial Vienna Hotel", 4.7, 235.00, "Ring Road", ["WiFi", "Restaurant", "Opera Tickets"]),
                HotelOption("Budget Vienna", 3.6, 75.00, "Favoriten", ["WiFi", "Breakfast"]),
            ],
            "New York": [
                HotelOption("Manhattan Plaza Hotel", 4.3, 220.00, "Times Square", ["WiFi", "Gym", "Restaurant"]),
                HotelOption("Budget Stay NYC", 3.5, 120.00, "Brooklyn", ["WiFi"]),
            ]
        }
        
        self.pricing_data = {
            "Paris": {"average_meal": 35.00, "local_transport": 2.50, "attraction_avg": 25.00, "currency": "EUR"},
            "London": {"average_meal": 32.00, "local_transport": 4.50, "attraction_avg": 28.00, "currency": "GBP"},
            "Rome": {"average_meal": 22.00, "local_transport": 1.50, "attraction_avg": 18.00, "currency": "EUR"},
            "Milan": {"average_meal": 28.00, "local_transport": 2.00, "attraction_avg": 22.00, "currency": "EUR"},
            "Madrid": {"average_meal": 20.00, "local_transport": 1.50, "attraction_avg": 15.00, "currency": "EUR"},
            "Barcelona": {"average_meal": 22.00, "local_transport": 2.40, "attraction_avg": 18.00, "currency": "EUR"},
            "Berlin": {"average_meal": 18.00, "local_transport": 3.10, "attraction_avg": 16.00, "currency": "EUR"},
            "Cologne": {"average_meal": 20.00, "local_transport": 2.90, "attraction_avg": 18.00, "currency": "EUR"},
            "Amsterdam": {"average_meal": 28.00, "local_transport": 3.20, "attraction_avg": 22.00, "currency": "EUR"},
            "Prague": {"average_meal": 12.00, "local_transport": 1.20, "attraction_avg": 8.00, "currency": "CZK"},
            "Vienna": {"average_meal": 25.00, "local_transport": 2.80, "attraction_avg": 20.00, "currency": "EUR"},
            "New York": {"average_meal": 35.00, "local_transport": 3.50, "attraction_avg": 25.00, "currency": "USD"}
        }
    
    def search_flights(self, origin: str, destination: str, date: str, passengers: int = 1) -> List[FlightOption]:
        return self.flight_data.get(destination, [])
    
    def search_hotels(self, city: str, checkin: str, checkout: str, guests: int = 1) -> List[HotelOption]:
        return self.hotel_data.get(city, [])
    
    def get_current_prices(self, city: str) -> Dict:
        return self.pricing_data.get(city, {
            "average_meal": 25.00,
            "local_transport": 3.50,
            "attraction_avg": 15.00,
            "currency": "USD"
        })

class SimpleItineraryPlanner:
    """Main planning agent without ML dependencies"""
    
    def __init__(self):
        self.tourist_db = SimpleTouristDatabase()
        self.web_search = SimpleWebSearchTool()
    
    def create_itinerary(self, request: TravelRequest) -> Dict:
        try:
            start_date = datetime.strptime(request.start_date, "%Y-%m-%d")
            end_date = datetime.strptime(request.end_date, "%Y-%m-%d")
            if end_date < start_date:
                raise ValueError("End date must be after start date")
        except ValueError as e:
            raise ValueError(f"Invalid date format or range: {e}. Use YYYY-MM-DD format.")

        print("🔍 Searching for attractions...")
        interests_query = " ".join(request.interests) if request.interests else ""
        attractions = self.tourist_db.search_attractions(
            request.destination, 
            interests_query, 
            request.interests, 
            top_k=15
        )
        if not attractions:
            print(f"⚠️ No attractions found for {request.destination}")
        
        print("✈️ Searching for flights...")
        flights = self.web_search.search_flights("Home City", request.destination, request.start_date, request.travelers)
        
        print("🏨 Searching for hotels...")
        hotels = self.web_search.search_hotels(request.destination, request.start_date, request.end_date, request.travelers)
        
        print("💰 Getting pricing information...")
        pricing = self.web_search.get_current_prices(request.destination)
        
        trip_days = (end_date - start_date).days
        if trip_days <= 0:
            raise ValueError("Trip duration must be at least one day")
        
        print("📅 Planning daily activities...")
        daily_itineraries = self.plan_daily_activities(
            attractions, trip_days, request.budget, pricing, start_date
        )
        
        print("🎯 Generating recommendations...")
        recommendations = self.generate_recommendations(request, flights, hotels, pricing)
        
        total_cost = self.calculate_total_cost(recommendations, daily_itineraries, trip_days)
        
        return {
            "destination": request.destination,
            "dates": f"{request.start_date} to {request.end_date}",
            "duration": f"{trip_days} days",
            "budget": request.budget,
            "estimated_cost": total_cost,
            "flights": [self.flight_to_dict(f) for f in flights],
            "hotels": [self.hotel_to_dict(h) for h in hotels],
            "daily_itineraries": [self.itinerary_to_dict(day) for day in daily_itineraries],
            "recommendations": recommendations,
            "budget_breakdown": self.create_budget_breakdown(total_cost, trip_days),
            "attractions_found": len(attractions)
        }
    
    def plan_daily_activities(self, attractions: List[Attraction], days: int, 
                            budget: float, pricing: Dict, start_date: datetime) -> List[DayItinerary]:
        """Plan activities for each day"""
        daily_itineraries = []
        daily_budget = budget / days if days > 0 else budget
        
        # Ensure at least one attraction per day if available
        activities_per_day = max(1, len(attractions) // days if days > 0 else len(attractions))
        
        # Distribute attractions across days
        for day in range(days):
            current_date = start_date + timedelta(days=day)
            activities = []
            day_cost = 0
            
            time_slots = ["Morning", "Afternoon", "Evening"]
            
            # Cycle through attractions if fewer than days
            start_idx = (day * activities_per_day) % len(attractions) if attractions else 0
            end_idx = min(start_idx + activities_per_day, len(attractions)) if attractions else 0
            day_attractions = attractions[start_idx:end_idx] if attractions else []
            
            for i, attraction in enumerate(day_attractions):
                time_slot = time_slots[i % len(time_slots)]
                activity_cost = self.parse_price_range(attraction.price_range)
                
                activity = {
                    "time": time_slot,
                    "activity": attraction.name,
                    "description": attraction.description,
                    "duration": attraction.duration,
                    "location": attraction.location,
                    "category": attraction.category,
                    "rating": attraction.rating,
                    "estimated_cost": activity_cost
                }
                activities.append(activity)
                day_cost += activity_cost
            
            # Add meals and transport
            day_cost += pricing["average_meal"] * 3
            day_cost += pricing["local_transport"] * 4
            
            notes = self.generate_day_notes(day + 1, activities, daily_budget, day_cost)
            
            daily_itineraries.append(DayItinerary(
                day=day + 1,
                date=current_date.strftime("%Y-%m-%d"),
                activities=activities,
                estimated_cost=round(day_cost, 2),
                notes=notes
            ))
        
        return daily_itineraries
    
    def parse_price_range(self, price_range: str) -> float:
        price_map = {
            "Free": 0,
            "$": 15,
            "$$": 30,
            "$$$": 50,
            "$$$$": 80
        }
        return price_map.get(price_range, 25)
    
    def generate_recommendations(self, request: TravelRequest, flights: List[FlightOption], 
                               hotels: List[HotelOption], pricing: Dict) -> Dict:
        flight_budget = request.budget * 0.4
        hotel_budget = request.budget * 0.3
        
        affordable_flights = [f for f in flights if f.price <= flight_budget]
        affordable_hotels = [h for h in hotels if h.price_per_night <= hotel_budget / 7]
        
        recommended_flight = min(affordable_flights, key=lambda x: x.price) if affordable_flights else \
                            min(flights, key=lambda x: x.price) if flights else None
        
        recommended_hotel = max(affordable_hotels, key=lambda x: x.rating - (x.price_per_night / 100)) if affordable_hotels else \
                           min(hotels, key=lambda x: x.price_per_night) if hotels else None
        
        return {
            "recommended_flight": self.flight_to_dict(recommended_flight) if recommended_flight else None,
            "recommended_hotel": self.hotel_to_dict(recommended_hotel) if recommended_hotel else None,
            "local_tips": [
                f"Average meal cost: {pricing['currency']} {pricing['average_meal']}",
                f"Local transport: {pricing['currency']} {pricing['local_transport']} per ride",
                "Book attractions in advance for better prices",
                "Consider city tourist cards for discounts",
                f"Currency: {pricing['currency']}",
                "Download offline maps to save on data roaming"
            ]
        }
    
    def calculate_total_cost(self, recommendations: Dict, daily_itineraries: List[DayItinerary], days: int) -> float:
        flight_cost = recommendations["recommended_flight"]["price"] * 2 if recommendations.get("recommended_flight") else 0
        hotel_cost = recommendations["recommended_hotel"]["price_per_night"] * days if recommendations.get("recommended_hotel") else 0
        activities_cost = sum(day.estimated_cost for day in daily_itineraries)
        return round(flight_cost + hotel_cost + activities_cost, 2)
    
    def create_budget_breakdown(self, total_cost: float, days: int) -> Dict:
        return {
            "total_estimated_cost": total_cost,
            "daily_average": round(total_cost / days, 2) if days > 0 else 0,
            "breakdown": {
                "flights": "40%",
                "accommodation": "30%",
                "activities": "20%",
                "meals_transport": "10%"
            },
            "cost_tips": [
                "Book flights early for better deals",
                "Consider staying in neighborhoods outside city center",
                "Look for free walking tours and attractions",
                "Eat at local markets for cheaper meals"
            ]
        }
    
    def generate_day_notes(self, day: int, activities: List[Dict], budget: float, cost: float) -> str:
        if not activities:
            return f"Day {day}: No activities planned. Consider adding free attractions or relaxing."
        if cost > budget * 1.2:
            return f"Day {day}: High cost day. Consider free alternatives or reduce activities."
        elif cost > budget:
            return f"Day {day}: Slightly over daily budget. Good mix of {len(activities)} activities."
        return f"Day {day}: Well within budget! Great day with {len(activities)} activities planned."
    
    def flight_to_dict(self, flight: FlightOption) -> Dict:
        if not flight:
            return None
        return {
            "airline": flight.airline,
            "departure": flight.departure,
            "arrival": flight.arrival,
            "price": flight.price,
            "duration": flight.duration
        }
    
    def hotel_to_dict(self, hotel: HotelOption) -> Dict:
        if not hotel:
            return None
        return {
            "name": hotel.name,
            "rating": hotel.rating,
            "price_per_night": hotel.price_per_night,
            "location": hotel.location,
            "amenities": hotel.amenities
        }
    
    def itinerary_to_dict(self, itinerary: DayItinerary) -> Dict:
        return {
            "day": itinerary.day,
            "date": itinerary.date,
            "activities": itinerary.activities,
            "estimated_cost": itinerary.estimated_cost,
            "notes": itinerary.notes
        }

def main():
    """Example usage of the Travel Itinerary Planner"""
    print("🎉 Starting Travel Itinerary Planner...")
    planner = SimpleItineraryPlanner()
    
    # List of cities to generate itineraries for
    cities = ["Prague", "Paris", "Rome"]  # Add more cities as needed
    
    all_itineraries = {}
    
    for city in cities:
        print(f"\n🚀 Generating itinerary for {city}...")
        travel_request = TravelRequest(
            destination=city,
            budget=1500.00,
            start_date="2024-09-01",
            end_date="2024-09-05",
            travelers=2,
            interests=["historic", "culture", "landmarks", "food"]
        )
        
        print(f"📅 Dates: {travel_request.start_date} to {travel_request.end_date}")
        print(f"💰 Budget: ${travel_request.budget}")
        print(f"👥 Travelers: {travel_request.travelers}")
        print(f"🎨 Interests: {', '.join(travel_request.interests)}")
        
        print("\n" + "="*50)
        print(f"GENERATING ITINERARY FOR {city.upper()}...")
        print("="*50)
        
        try:
            itinerary = planner.create_itinerary(travel_request)
            all_itineraries[city] = itinerary
            
            # Display results
            print(f"\n🌟 TRAVEL ITINERARY FOR {itinerary['destination'].upper()}")
            print("="*60)
            print(f"📅 Dates: {itinerary['dates']}")
            print(f"⏱️ Duration: {itinerary['duration']}")
            print(f"💰 Budget: ${itinerary['budget']}")
            print(f"💸 Estimated Cost: ${itinerary['estimated_cost']}")
            print(f"🎯 Attractions Found: {itinerary['attractions_found']}")
            
            budget_status = "✅ WITHIN BUDGET" if itinerary['estimated_cost'] <= itinerary['budget'] else "⚠️ OVER BUDGET"
            remaining = itinerary['budget'] - itinerary['estimated_cost']
            print(f"📊 Status: {budget_status}")
            print(f"💵 Remaining: ${remaining:.2f}")
            
            if itinerary['recommendations']['recommended_flight']:
                print(f"\n✈️ RECOMMENDED FLIGHT:")
                flight = itinerary['recommendations']['recommended_flight']
                print(f"   🛫 {flight['airline']}: {flight['departure']} → {flight['arrival']}")
                print(f"   💰 Price: ${flight['price']} | Duration: {flight['duration']}")
            
            if itinerary['recommendations']['recommended_hotel']:
                print(f"\n🏨 RECOMMENDED HOTEL:")
                hotel = itinerary['recommendations']['recommended_hotel']
                print(f"   🏩 {hotel['name']} ({hotel['rating']}⭐)")
                print(f"   💰 ${hotel['price_per_night']}/night | 📍 {hotel['location']}")
                print(f"   🎯 Amenities: {', '.join(hotel['amenities'])}")
            
            print(f"\n📋 DAILY ITINERARY:")
            print("-" * 60)
            for day in itinerary['daily_itineraries']:
                print(f"\n📅 DAY {day['day']} ({day['date']}) - ${day['estimated_cost']}")
                for activity in day['activities']:
                    print(f"   🕐 {activity['time']}: {activity['activity']}")
                    print(f"      📝 {activity['description']}")
                    print(f"      📍 {activity['location']} | ⭐ {activity['rating']}")
                    print(f"      ⏰ Duration: {activity['duration']} | 💰 ${activity['estimated_cost']}")
                print(f"   📝 {day['notes']}")
            
            print(f"\n💡 LOCAL TIPS:")
            for tip in itinerary['recommendations']['local_tips']:
                print(f"   • {tip}")
            
            print(f"\n💰 BUDGET BREAKDOWN:")
            breakdown = itinerary['budget_breakdown']
            print(f"   💵 Total: ${breakdown['total_estimated_cost']}")
            print(f"   📊 Daily Average: ${breakdown['daily_average']}")
            print(f"   📈 Spending Distribution:")
            for category, percentage in breakdown['breakdown'].items():
                print(f"      • {category.replace('_', ' ').title()}: {percentage}")
            
            print(f"\n💰 MONEY-SAVING TIPS:")
            for tip in breakdown['cost_tips']:
                print(f"   • {tip}")
        
        except Exception as e:
            print(f"❌ Error generating itinerary for {city}: {e}")
    
    # Save all itineraries to JSON
    with open('travel_itineraries.json', 'w') as f:
        json.dump(all_itineraries, f, indent=2)
    print("\n💾 All itineraries saved to 'travel_itineraries.json'")
    
    return all_itineraries

if __name__ == "__main__":
    try:
        itineraries = main()
        print("\n✅ All itineraries generated successfully!")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Please check your input parameters and try again.")