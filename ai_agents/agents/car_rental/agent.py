"""
Car rental agent for handling vehicle search, reservations, and rental management.
"""

from typing import Dict, Any, List, Optional
from core.base_agent import BaseAgent
from core.tools_registry import global_tools_registry
from agents.car_rental.tools import (
    VehicleSearchTool,
    ReservationManagementTool,
    LocationServicesTool,
    InsuranceServicesTool,
)
from utils.logger import get_logger

logger = get_logger(__name__)


class CarRentalAgent(BaseAgent):
    """Agent specialized for car rental operations."""

    def __init__(self):
        super().__init__(
            name="car_rental",
            description="AI agent for car rental services including vehicle search, reservations, and rental management",
        )
        self.tools = self._initialize_tools()

    def _initialize_tools(self) -> Dict[str, Any]:
        """Initialize and register car rental specific tools."""
        tools = {}

        # Initialize tools
        vehicle_search = VehicleSearchTool()
        reservation_management = ReservationManagementTool()
        location_services = LocationServicesTool()
        insurance_services = InsuranceServicesTool()

        # Store tools locally
        tools["vehicle_search"] = vehicle_search
        tools["reservation_management"] = reservation_management
        tools["location_services"] = location_services
        tools["insurance_services"] = insurance_services

        # Register with global registry
        global_tools_registry.register_tool(vehicle_search, "car_rental")
        global_tools_registry.register_tool(reservation_management, "car_rental")
        global_tools_registry.register_tool(location_services, "car_rental")
        global_tools_registry.register_tool(insurance_services, "car_rental")

        logger.info("Car rental tools initialized and registered")
        return tools

    def _initialize_graph(self) -> None:
        """Initialize the agent's conversation graph."""
        # In a full implementation, this would set up the LangGraph workflow
        # For now, we'll implement basic message processing
        pass

    def get_tools(self) -> List[Any]:
        """Get the tools available to this agent."""
        return list(self.tools.values())

    async def process_message(
        self, message: str, context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Process a user message and return an appropriate response.

        Args:
            message: User input message
            context: Optional context information

        Returns:
            Agent response
        """
        try:
            customer_id = context.get("customer_id", "guest") if context else "guest"
            message_lower = message.lower()

            # Determine intent and route to appropriate tool
            if any(
                keyword in message_lower
                for keyword in ["search", "find", "available", "rent a car"]
            ):
                return await self._handle_vehicle_search(message, customer_id)

            elif any(
                keyword in message_lower
                for keyword in ["book", "reserve", "reservation", "make a booking"]
            ):
                return await self._handle_reservation_operations(message, customer_id)

            elif any(
                keyword in message_lower
                for keyword in ["location", "pickup", "dropoff", "where", "address"]
            ):
                return await self._handle_location_services(message, customer_id)

            elif any(
                keyword in message_lower
                for keyword in ["insurance", "coverage", "protection", "damage waiver"]
            ):
                return await self._handle_insurance_services(message, customer_id)

            elif any(
                keyword in message_lower
                for keyword in ["my reservation", "my booking", "cancel", "modify"]
            ):
                return await self._handle_manage_reservations(message, customer_id)

            else:
                return await self._handle_general_inquiry(message)

        except Exception as e:
            logger.error(f"Error processing message in car rental agent: {e}")
            return "I apologize, but I encountered an error while processing your request. Please try again."

    async def _handle_vehicle_search(self, message: str, customer_id: str) -> str:
        """Handle vehicle search requests."""
        try:
            # For this example, we'll use default search parameters
            # In a real implementation, we'd extract dates and preferences from the message
            pickup_date = "2024-01-15"  # Mock date
            return_date = "2024-01-20"  # Mock date

            search_tool = self.tools["vehicle_search"]
            results = await search_tool.execute(pickup_date, return_date)

            if not results:
                return """I couldn't find any available vehicles for those dates. Please try different dates or let me know your specific requirements:
                
- Pickup date and time
- Return date and time  
- Preferred location (Downtown, Airport)
- Vehicle type (Economy, SUV, Luxury, etc.)
- Budget range"""

            # Format response
            response = f"I found {len(results)} available vehicle(s) for your rental period:\n\n"

            for i, vehicle in enumerate(results[:5], 1):  # Limit to 5 results
                response += f"{i}. **{vehicle['model']}** ({vehicle['type']})\n"
                response += (
                    f"   📍 {vehicle['location']} | {vehicle['daily_rate']}/day\n"
                )
                response += f"   💰 Total: {vehicle['total_cost']} for {vehicle['rental_days']} days\n"
                response += f"   ✨ Features: {', '.join(vehicle['features'][:3])}\n\n"

            if len(results) > 5:
                response += f"... and {len(results) - 5} more options available.\n\n"

            response += "Would you like to make a reservation for any of these vehicles or need more information?"

            return response

        except Exception as e:
            logger.error(f"Error in vehicle search: {e}")
            return "I'm sorry, I encountered an error while searching for vehicles. Please try again."

    async def _handle_reservation_operations(
        self, message: str, customer_id: str
    ) -> str:
        """Handle reservation creation and booking."""
        try:
            message_lower = message.lower()
            reservation_tool = self.tools["reservation_management"]

            if any(
                word in message_lower for word in ["create", "book", "reserve", "make"]
            ):
                # Create a reservation (simplified - in real implementation, extract details from message)
                result = await reservation_tool.execute(
                    "create",
                    customer_id,
                    vehicle_id=1,
                    pickup_date="2024-01-15",
                    return_date="2024-01-20",
                    pickup_location="Downtown",
                    return_location="Downtown",
                    driver_info={"name": "Customer", "license": "DL123456"},
                    total_cost=175.00,
                )

                if result["success"]:
                    reservation = result["reservation"]
                    response = f"🎉 {result['message']}\n\n"
                    response += "Reservation Details:\n"
                    response += f"- Reservation ID: **{result['reservation_id']}**\n"
                    response += f"- Vehicle: {reservation.get('vehicle_id', 'TBD')}\n"
                    response += f"- Pickup: {reservation['pickup_date']} at {reservation['pickup_location']}\n"
                    response += f"- Return: {reservation['return_date']} at {reservation.get('return_location', reservation['pickup_location'])}\n"
                    response += f"- Total Cost: ${reservation['total_cost']:.2f}\n"
                    response += f"- Status: {result['status']}\n\n"
                    response += "📧 A confirmation email has been sent to you with all the details.\n"
                    response += "💡 Don't forget to bring your driver's license and a credit card for pickup!"
                    return response
                else:
                    return f"Reservation failed: {result.get('error', 'Unknown error')}"

            else:
                return """To make a reservation, I'll need the following information:

📅 **Rental Dates**
- Pickup date and time
- Return date and time

📍 **Location**  
- Pickup location
- Return location (if different)

🚗 **Vehicle Preferences**
- Vehicle type (Economy, Mid-size, SUV, etc.)
- Any special requirements

👤 **Driver Information**
- Driver's name
- Valid driver's license

Would you like to proceed with making a reservation?"""

        except Exception as e:
            logger.error(f"Error in reservation operations: {e}")
            return "I'm sorry, I encountered an error while processing your reservation. Please try again."

    async def _handle_location_services(self, message: str, customer_id: str) -> str:
        """Handle location-related queries."""
        try:
            location_tool = self.tools["location_services"]

            # Get all locations
            result = await location_tool.execute("find_locations")

            if result["success"]:
                locations = result["locations"]

                response = "Here are our rental locations:\n\n"

                for location in locations:
                    response += f"📍 **{location['name']}**\n"
                    response += f"   Address: {location['address']}\n"
                    response += f"   Hours: {location['hours']}\n"
                    response += f"   Services: {', '.join(location['services'])}\n\n"

                response += "Would you like directions to any of these locations or need to check specific hours?"

                return response
            else:
                return "I'm sorry, I couldn't retrieve location information at the moment. Please try again."

        except Exception as e:
            logger.error(f"Error in location services: {e}")
            return "I'm sorry, I encountered an error while getting location information. Please try again."

    async def _handle_insurance_services(self, message: str, customer_id: str) -> str:
        """Handle insurance and protection queries."""
        try:
            insurance_tool = self.tools["insurance_services"]

            # Get insurance options
            result = await insurance_tool.execute("get_options")

            if result["success"]:
                options = result["insurance_options"]

                response = "Here are our insurance and protection options:\n\n"

                for option in options:
                    response += (
                        f"🛡️ **{option['name']}** - ${option['daily_cost']:.2f}/day\n"
                    )
                    response += f"   {option['description']}\n"
                    response += f"   Coverage: {', '.join(option['coverage'])}\n\n"

                response += "💡 **Recommendation**: Premium Protection offers the best value for most customers.\n\n"
                response += "Would you like to calculate the total cost for your rental period or need more details about any option?"

                return response
            else:
                return "I'm sorry, I couldn't retrieve insurance information at the moment. Please try again."

        except Exception as e:
            logger.error(f"Error in insurance services: {e}")
            return "I'm sorry, I encountered an error while getting insurance information. Please try again."

    async def _handle_manage_reservations(self, message: str, customer_id: str) -> str:
        """Handle reservation management (view, modify, cancel)."""
        try:
            reservation_tool = self.tools["reservation_management"]
            message_lower = message.lower()

            if "cancel" in message_lower:
                # For demo purposes, assume they want to cancel a specific reservation
                # In real implementation, we'd extract reservation ID from message
                return """To cancel your reservation, I'll need your reservation ID. You can find it in:

📧 Your confirmation email
💾 Your account dashboard
📱 The reservation SMS

Please provide your reservation ID (format: RES-XXXX) and I'll help you cancel it.

⚠️ **Cancellation Policy**: 
- Free cancellation up to 24 hours before pickup
- Partial refund for cancellations within 24 hours
- No refund for no-shows"""

            elif any(word in message_lower for word in ["modify", "change", "update"]):
                return """To modify your reservation, I can help you change:

📅 Pickup/return dates and times
📍 Pickup/return locations  
🚗 Vehicle type (subject to availability)

Please provide:
1. Your reservation ID (RES-XXXX)
2. What you'd like to change
3. Your new preferences

💡 **Note**: Changes may affect the total cost and are subject to availability."""

            else:
                # View reservations
                result = await reservation_tool.execute("view", customer_id)

                if result["success"]:
                    reservations = result["reservations"]

                    if not reservations:
                        return "You don't have any current reservations. Would you like to make a new reservation?"

                    response = f"You have {result['count']} reservation(s):\n\n"

                    for res_id, reservation in reservations.items():
                        response += f"🎫 **{res_id}**\n"
                        response += f"   Pickup: {reservation['pickup_date']} at {reservation['pickup_location']}\n"
                        response += f"   Return: {reservation['return_date']}\n"
                        response += f"   Status: {reservation['status']}\n"
                        response += f"   Total: ${reservation['total_cost']:.2f}\n\n"

                    response += (
                        "Would you like to modify or cancel any of these reservations?"
                    )

                    return response
                else:
                    return "I couldn't retrieve your reservations at the moment. Please try again."

        except Exception as e:
            logger.error(f"Error in reservation management: {e}")
            return "I'm sorry, I encountered an error while managing your reservation. Please try again."

    async def _handle_general_inquiry(self, message: str) -> str:
        """Handle general car rental inquiries."""
        return """Hello! I'm your car rental assistant. I can help you with:

🔍 **Vehicle Search** - Find available cars for your dates and location
📅 **Reservations** - Make, modify, or cancel bookings  
📍 **Locations** - Find pickup/dropoff locations and hours
🛡️ **Insurance** - Learn about protection and coverage options
📋 **Manage Bookings** - View and update your reservations

**Popular Vehicle Types:**
🚗 Economy (from $35/day) - Perfect for city driving
🚙 SUV (from $70/day) - Great for families and road trips  
💎 Luxury (from $120/day) - Premium comfort and style

What would you like to help you with today?"""

    def get_capabilities(self) -> List[str]:
        """Get a list of the agent's capabilities."""
        return [
            "Vehicle search and availability checking",
            "Reservation creation and management",
            "Location services and directions",
            "Insurance and protection options",
            "Booking modifications and cancellations",
            "Customer support for car rentals",
            "Price comparison and recommendations",
        ]
