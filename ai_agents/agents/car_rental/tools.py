"""
Car rental agent tools for vehicle search, booking, and reservation management.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from core.tools_registry import BaseTool
from utils.logger import get_logger
from utils.helpers import sanitize_input, format_currency, parse_datetime

logger = get_logger(__name__)


class VehicleSearchTool(BaseTool):
    """Tool for searching available rental vehicles."""

    def __init__(self):
        super().__init__(
            name="vehicle_search",
            description="Search for available rental vehicles by type, location, and dates",
        )
        # Mock vehicle database
        self.vehicles = [
            {
                "id": 1,
                "type": "Economy",
                "model": "Toyota Corolla",
                "daily_rate": 35.00,
                "location": "Downtown",
                "available": True,
            },
            {
                "id": 2,
                "type": "Compact",
                "model": "Honda Civic",
                "daily_rate": 40.00,
                "location": "Airport",
                "available": True,
            },
            {
                "id": 3,
                "type": "Mid-size",
                "model": "Toyota Camry",
                "daily_rate": 50.00,
                "location": "Downtown",
                "available": True,
            },
            {
                "id": 4,
                "type": "Full-size",
                "model": "Chevrolet Impala",
                "daily_rate": 60.00,
                "location": "Airport",
                "available": True,
            },
            {
                "id": 5,
                "type": "Premium",
                "model": "BMW 3 Series",
                "daily_rate": 80.00,
                "location": "Downtown",
                "available": True,
            },
            {
                "id": 6,
                "type": "SUV",
                "model": "Toyota RAV4",
                "daily_rate": 70.00,
                "location": "Airport",
                "available": True,
            },
            {
                "id": 7,
                "type": "Luxury",
                "model": "Mercedes E-Class",
                "daily_rate": 120.00,
                "location": "Downtown",
                "available": False,
            },
            {
                "id": 8,
                "type": "Van",
                "model": "Ford Transit",
                "daily_rate": 90.00,
                "location": "Airport",
                "available": True,
            },
        ]

    async def execute(
        self,
        pickup_date: str,
        return_date: str,
        location: Optional[str] = None,
        vehicle_type: Optional[str] = None,
        max_daily_rate: Optional[float] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search for available vehicles.

        Args:
            pickup_date: Pickup date (YYYY-MM-DD format)
            return_date: Return date (YYYY-MM-DD format)
            location: Optional location filter
            vehicle_type: Optional vehicle type filter
            max_daily_rate: Optional maximum daily rate filter

        Returns:
            List of available vehicles
        """
        # Parse dates
        pickup_dt = parse_datetime(pickup_date)
        return_dt = parse_datetime(return_date)

        if not pickup_dt or not return_dt:
            return []

        if return_dt <= pickup_dt:
            return []

        # Calculate rental days
        rental_days = (return_dt - pickup_dt).days

        results = []

        for vehicle in self.vehicles:
            # Check availability
            if not vehicle["available"]:
                continue

            # Apply filters
            if location and vehicle["location"].lower() != location.lower():
                continue

            if vehicle_type and vehicle["type"].lower() != vehicle_type.lower():
                continue

            if max_daily_rate and vehicle["daily_rate"] > max_daily_rate:
                continue

            # Calculate total cost
            total_cost = vehicle["daily_rate"] * rental_days

            # Format vehicle for response
            formatted_vehicle = {
                "id": vehicle["id"],
                "type": vehicle["type"],
                "model": vehicle["model"],
                "daily_rate": format_currency(vehicle["daily_rate"]),
                "daily_rate_numeric": vehicle["daily_rate"],
                "location": vehicle["location"],
                "total_cost": format_currency(total_cost),
                "total_cost_numeric": total_cost,
                "rental_days": rental_days,
                "features": self._get_vehicle_features(vehicle["type"]),
            }
            results.append(formatted_vehicle)

        # Sort by daily rate
        results.sort(key=lambda x: x["daily_rate_numeric"])

        logger.info(
            f"Vehicle search for {pickup_date} to {return_date} returned {len(results)} results"
        )
        return results

    def _get_vehicle_features(self, vehicle_type: str) -> List[str]:
        """Get features based on vehicle type."""
        features_map = {
            "Economy": ["Manual transmission", "Air conditioning", "Radio"],
            "Compact": [
                "Manual transmission",
                "Air conditioning",
                "Bluetooth",
                "Power windows",
            ],
            "Mid-size": [
                "Automatic transmission",
                "Air conditioning",
                "Bluetooth",
                "Cruise control",
            ],
            "Full-size": [
                "Automatic transmission",
                "Air conditioning",
                "Bluetooth",
                "Cruise control",
                "Power seats",
            ],
            "Premium": [
                "Automatic transmission",
                "Climate control",
                "Premium audio",
                "Leather seats",
                "GPS",
            ],
            "SUV": [
                "Automatic transmission",
                "4WD",
                "Climate control",
                "Bluetooth",
                "Cargo space",
            ],
            "Luxury": [
                "Automatic transmission",
                "Premium interior",
                "GPS",
                "Premium audio",
                "Heated seats",
            ],
            "Van": [
                "Automatic transmission",
                "Air conditioning",
                "Multiple seats",
                "Large cargo space",
            ],
        }
        return features_map.get(vehicle_type, ["Air conditioning", "Radio"])


class ReservationManagementTool(BaseTool):
    """Tool for managing car rental reservations."""

    def __init__(self):
        super().__init__(
            name="reservation_management",
            description="Create, modify, cancel, or view car rental reservations",
        )
        self.reservations: Dict[str, Dict[str, Any]] = {}
        self.reservation_counter = 2000

    async def execute(self, action: str, customer_id: str, **kwargs) -> Dict[str, Any]:
        """
        Manage reservation operations.

        Args:
            action: Action to perform (create, view, modify, cancel)
            customer_id: Customer identifier
            **kwargs: Additional parameters based on action

        Returns:
            Reservation operation result
        """
        if action == "create":
            reservation_id = f"RES-{self.reservation_counter}"
            self.reservation_counter += 1

            reservation = {
                "reservation_id": reservation_id,
                "customer_id": customer_id,
                "vehicle_id": kwargs.get("vehicle_id"),
                "pickup_date": kwargs.get("pickup_date"),
                "return_date": kwargs.get("return_date"),
                "pickup_location": kwargs.get("pickup_location", "Downtown"),
                "return_location": kwargs.get("return_location"),
                "driver_info": kwargs.get("driver_info", {}),
                "total_cost": kwargs.get("total_cost", 0.0),
                "status": "confirmed",
                "created_at": datetime.now().isoformat(),
                "insurance_options": kwargs.get("insurance_options", []),
            }

            self.reservations[reservation_id] = reservation

            result = {
                "success": True,
                "reservation_id": reservation_id,
                "status": "confirmed",
                "message": f"Reservation {reservation_id} created successfully",
                "reservation": reservation,
            }

        elif action == "view":
            customer_reservations = {
                res_id: res
                for res_id, res in self.reservations.items()
                if res["customer_id"] == customer_id
            }

            result = {
                "success": True,
                "reservations": customer_reservations,
                "count": len(customer_reservations),
            }

        elif action == "cancel":
            reservation_id = kwargs.get("reservation_id")
            if not reservation_id:
                return {"success": False, "error": "Reservation ID is required"}

            reservation = self.reservations.get(reservation_id)
            if reservation and reservation["customer_id"] == customer_id:
                if reservation["status"] in ["confirmed", "pending"]:
                    reservation["status"] = "cancelled"
                    reservation["cancelled_at"] = datetime.now().isoformat()
                    result = {
                        "success": True,
                        "message": f"Reservation {reservation_id} cancelled successfully",
                    }
                else:
                    result = {
                        "success": False,
                        "error": f"Cannot cancel reservation with status: {reservation['status']}",
                    }
            else:
                result = {"success": False, "error": "Reservation not found"}

        elif action == "modify":
            reservation_id = kwargs.get("reservation_id")
            if not reservation_id:
                return {"success": False, "error": "Reservation ID is required"}

            reservation = self.reservations.get(reservation_id)
            if reservation and reservation["customer_id"] == customer_id:
                # Update allowed fields
                updatable_fields = [
                    "pickup_date",
                    "return_date",
                    "pickup_location",
                    "return_location",
                ]
                updated_fields = []

                for field in updatable_fields:
                    if field in kwargs:
                        reservation[field] = kwargs[field]
                        updated_fields.append(field)

                if updated_fields:
                    reservation["modified_at"] = datetime.now().isoformat()
                    result = {
                        "success": True,
                        "message": f"Reservation {reservation_id} updated successfully",
                        "updated_fields": updated_fields,
                    }
                else:
                    result = {"success": False, "error": "No valid fields to update"}
            else:
                result = {"success": False, "error": "Reservation not found"}

        else:
            return {"success": False, "error": f"Unknown action: {action}"}

        logger.info(f"Reservation {action} for customer {customer_id}")
        return result


class LocationServicesTool(BaseTool):
    """Tool for location-based services like pickup/dropoff locations."""

    def __init__(self):
        super().__init__(
            name="location_services",
            description="Find pickup/dropoff locations and get directions",
        )
        self.locations = [
            {
                "id": 1,
                "name": "Downtown Office",
                "address": "123 Main St, Downtown",
                "type": "office",
                "hours": "Mon-Fri: 8AM-6PM, Sat-Sun: 9AM-5PM",
                "services": ["pickup", "dropoff", "fuel_service"],
            },
            {
                "id": 2,
                "name": "Airport Counter",
                "address": "Airport Terminal 1, Level 2",
                "type": "airport",
                "hours": "24/7",
                "services": ["pickup", "dropoff", "after_hours"],
            },
            {
                "id": 3,
                "name": "Mall Kiosk",
                "address": "City Mall, Ground Floor",
                "type": "mall",
                "hours": "Mon-Sun: 10AM-10PM",
                "services": ["pickup", "dropoff"],
            },
        ]

    async def execute(self, action: str, **kwargs) -> Dict[str, Any]:
        """
        Handle location services.

        Args:
            action: Action to perform (find_locations, get_directions, check_hours)
            **kwargs: Additional parameters

        Returns:
            Location service result
        """
        if action == "find_locations":
            location_type = kwargs.get("type")
            service_type = kwargs.get("service")

            filtered_locations = self.locations.copy()

            if location_type:
                filtered_locations = [
                    loc for loc in filtered_locations if loc["type"] == location_type
                ]

            if service_type:
                filtered_locations = [
                    loc for loc in filtered_locations if service_type in loc["services"]
                ]

            return {
                "success": True,
                "locations": filtered_locations,
                "count": len(filtered_locations),
            }

        elif action == "get_directions":
            location_id = kwargs.get("location_id")
            location = next(
                (loc for loc in self.locations if loc["id"] == location_id), None
            )

            if location:
                # Mock directions (in production, integrate with maps API)
                return {
                    "success": True,
                    "location": location,
                    "directions": f"Navigate to {location['address']}",
                    "estimated_time": "15 minutes",
                    "distance": "5.2 miles",
                }
            else:
                return {"success": False, "error": "Location not found"}

        elif action == "check_hours":
            location_id = kwargs.get("location_id")
            location = next(
                (loc for loc in self.locations if loc["id"] == location_id), None
            )

            if location:
                return {
                    "success": True,
                    "location": location["name"],
                    "hours": location["hours"],
                    "is_open": True,  # Mock - would check current time
                }
            else:
                return {"success": False, "error": "Location not found"}

        else:
            return {"success": False, "error": f"Unknown action: {action}"}


class InsuranceServicesTool(BaseTool):
    """Tool for insurance and protection options."""

    def __init__(self):
        super().__init__(
            name="insurance_services",
            description="Get information about insurance options and coverage",
        )
        self.insurance_options = [
            {
                "id": "basic",
                "name": "Basic Coverage",
                "daily_cost": 15.00,
                "description": "Basic collision damage waiver",
                "coverage": ["Collision damage", "Theft protection"],
            },
            {
                "id": "premium",
                "name": "Premium Protection",
                "daily_cost": 25.00,
                "description": "Comprehensive protection package",
                "coverage": [
                    "Collision damage",
                    "Theft protection",
                    "Personal accident",
                    "Personal effects",
                ],
            },
            {
                "id": "full",
                "name": "Full Coverage",
                "daily_cost": 35.00,
                "description": "Maximum protection with zero deductible",
                "coverage": [
                    "Zero deductible",
                    "Roadside assistance",
                    "Personal accident",
                    "Personal effects",
                    "Additional driver",
                ],
            },
        ]

    async def execute(self, action: str, **kwargs) -> Dict[str, Any]:
        """
        Handle insurance services.

        Args:
            action: Action to perform (get_options, calculate_cost)
            **kwargs: Additional parameters

        Returns:
            Insurance service result
        """
        if action == "get_options":
            return {"success": True, "insurance_options": self.insurance_options}

        elif action == "calculate_cost":
            rental_days = kwargs.get("rental_days", 1)
            selected_options = kwargs.get("selected_options", [])

            total_cost = 0.0
            selected_details = []

            for option_id in selected_options:
                option = next(
                    (opt for opt in self.insurance_options if opt["id"] == option_id),
                    None,
                )
                if option:
                    option_cost = option["daily_cost"] * rental_days
                    total_cost += option_cost
                    selected_details.append(
                        {
                            "name": option["name"],
                            "daily_cost": format_currency(option["daily_cost"]),
                            "total_cost": format_currency(option_cost),
                            "coverage": option["coverage"],
                        }
                    )

            return {
                "success": True,
                "selected_insurance": selected_details,
                "total_insurance_cost": format_currency(total_cost),
                "total_insurance_cost_numeric": total_cost,
                "rental_days": rental_days,
            }

        else:
            return {"success": False, "error": f"Unknown action: {action}"}
