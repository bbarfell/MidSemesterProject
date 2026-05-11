import uuid
from data import DataManager

class User:
    """Represents a system user with role-based attributes."""
    def __init__(self, user_data):
        self.id = user_data.get("id")
        self.email = user_data.get("email")
        self.role = user_data.get("role")

class ShopService:
    """Manages the business logic for inventory and authentication."""
    def __init__(self):
        self.inv_path = "flower_inventory.json"
        self.user_path = "shop_users.json"
        
        # Phase 2: Providing visible sample data for immediate testing
        initial_users = [
            {"id": "1", "email": "admin@petals.com", "password": "admin", "role": "Admin"},
            {"id": "2", "email": "florist@petals.com", "password": "staff", "role": "Florist"},
            {"id": "3", "email": "customer@gmail.com", "password": "user123", "role": "Customer"}
        ]
        
        self.users = DataManager.load(self.user_path, initial_users)
        self.inventory = DataManager.load(self.inv_path, [
            {"name": "Red Roses", "price": 45.0, "stock": 50},
            {"name": "Sunflowers", "price": 15.0, "stock": 30},
            {"name": "White Lilies", "price": 25.0, "stock": 20}
        ])

    def validate_login(self, email, password):
        """Service logic to verify credentials and return user data."""
        user = next((u for u in self.users if u["email"].lower() == email.lower() 
                     and u["password"] == password), None)
        return user

    def process_purchase(self, item_name, quantity):
        """Logic to update stock after a purchase is validated."""
        for item in self.inventory:
            if item["name"] == item_name and item["stock"] >= quantity:
                item["stock"] -= quantity
                DataManager.save(self.inv_path, self.inventory)
                return True
        return False

class AIChatAssistant:
    """Handles connection to OpenAI to provide floral support."""
    def __init__(self, api_key):
        from openai import OpenAI
        self.client = OpenAI(api_key=api_key)

    def get_floral_advice(self, prompt):
        """Generates AI responses for customer floral care."""
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert florist for Petals & Blooms."},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"AI Assistant is resting. Error: {str(e)}"