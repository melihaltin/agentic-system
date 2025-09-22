"""
Payload Processor for Voice Agent System
Processes and validates incoming payloads from backend
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime
import json


@dataclass
class ProcessedCustomer:
    """Processed customer information"""

    phone: str
    name: str
    customer_type: str
    email: Optional[str] = None
    cart_value: Optional[float] = None
    cart_items: List[Dict[str, Any]] = None


@dataclass
class ProcessedBusiness:
    """Processed business information"""

    name: str
    description: str
    website: str
    industry: Optional[str] = None
    phone: Optional[str] = None


@dataclass
class ProcessedAgent:
    """Processed agent configuration"""

    name: str
    tts_provider: str
    language: str
    voice_id: Optional[str] = None
    selected_voice_id: Optional[str] = None
    voice_settings: Dict[str, Any] = None
    personality: Optional[str] = None


@dataclass
class ProcessedPayload:
    """Complete processed payload"""

    customer: ProcessedCustomer
    business: ProcessedBusiness
    agent: ProcessedAgent
    cart_data: List[Dict[str, Any]]
    platform_data: Dict[str, Any]
    metadata: Dict[str, Any]
    original_payload: Dict[str, Any]


class PayloadProcessor:
    """
    Processes and validates payloads from backend
    Converts various payload formats to standardized format
    """

    def __init__(self):
        self.supported_platforms = [
            "shopify",
            "woocommerce",
            "magento",
            "bigcommerce",
            "custom",
            "api",
        ]

    def process(self, raw_payload: Dict[str, Any]) -> ProcessedPayload:
        """
        Process raw payload into standardized format

        Args:
            raw_payload: Raw payload from backend

        Returns:
            ProcessedPayload object

        Raises:
            ValueError: If payload is invalid or missing required fields
        """
        try:
            print(
                f"🔄 Processing payload of type: {self._detect_payload_type(raw_payload)}"
            )
            print(f"🔍 DEBUG: Raw payload keys: {list(raw_payload.keys())}")

            # Validate basic structure
            self._validate_payload(raw_payload)

            # Extract components
            print("📞 DEBUG: Extracting customer...")
            customer = self._extract_customer(raw_payload)
            print(f"✅ Customer: {customer.name} ({customer.phone})")

            print("🏢 DEBUG: Extracting business...")
            business = self._extract_business(raw_payload)

            print("🤖 DEBUG: Extracting agent...")
            agent = self._extract_agent(raw_payload)

            print("🛒 DEBUG: Extracting cart data...")
            cart_data = self._extract_cart_data(raw_payload)

            print("📊 DEBUG: Extracting platform data...")
            platform_data = self._extract_platform_data(raw_payload)

            print("📋 DEBUG: Extracting metadata...")
            metadata = self._extract_metadata(raw_payload)

            processed = ProcessedPayload(
                customer=customer,
                business=business,
                agent=agent,
                cart_data=cart_data,
                platform_data=platform_data,
                metadata=metadata,
                original_payload=raw_payload,
            )

            print(
                f"✅ Payload processed successfully for {customer.name} ({customer.phone})"
            )
            return processed

        except Exception as e:
            print(f"❌ Error processing payload: {str(e)}")
            raise ValueError(f"Payload processing failed: {str(e)}")

    def _detect_payload_type(self, payload: Dict[str, Any]) -> str:
        """Detect the type of payload"""
        if "agent" in payload and "business" in payload:
            return "backend_abandoned_cart"
        elif "abandoned_carts" in payload:
            return "abandoned_cart_direct"
        elif "platform_data" in payload:
            return "platform_data"
        elif "phone_number" in payload and "business_info" in payload:
            return "legacy_api"
        else:
            return "unknown"

    def _validate_payload(self, payload: Dict[str, Any]) -> None:
        """Validate payload structure"""
        if not isinstance(payload, dict):
            raise ValueError("Payload must be a dictionary")

        # Check for at least one customer identification method
        has_customer_info = (
            "customer" in payload
            or "abandoned_carts" in payload
            or "phone_number" in payload
            or any(
                "abandoned_carts" in platform_data
                for platform_data in payload.get("platform_data", {}).values()
            )
        )

        if not has_customer_info:
            raise ValueError("No customer information found in payload")

        # Check for business information
        has_business_info = (
            "business" in payload or "business_info" in payload or "agent" in payload
        )

        if not has_business_info:
            raise ValueError("No business information found in payload")

    def _extract_customer(self, payload: Dict[str, Any]) -> ProcessedCustomer:
        """Extract customer information"""
        # Try direct customer object
        if "customer" in payload:
            customer = payload["customer"]
            return ProcessedCustomer(
                phone=self._normalize_phone(customer.get("phone")),
                name=customer.get("name", "Customer"),
                customer_type=customer.get("type", "regular"),
                email=customer.get("email"),
                cart_value=customer.get("cart_value"),
            )

        # Try abandoned carts
        if "abandoned_carts" in payload and payload["abandoned_carts"]:
            cart = payload["abandoned_carts"][0]
            return ProcessedCustomer(
                phone=self._normalize_phone(cart.get("customer_phone")),
                name=cart.get("customer_name", "Customer"),
                customer_type="abandoned_cart",
                email=cart.get("customer_email"),
                cart_value=cart.get("total_value"),
                cart_items=cart.get("items", []),
            )

        # Try platform data (legacy format)
        platform_data = payload.get("platform_data", {})
        for platform, data in platform_data.items():
            if "abandoned_carts" in data and data["abandoned_carts"]:
                cart = data["abandoned_carts"][0]
                return ProcessedCustomer(
                    phone=self._normalize_phone(cart.get("customer_phone")),
                    name=cart.get("customer_name", "Customer"),
                    customer_type="abandoned_cart",
                    email=cart.get("customer_email"),
                    cart_value=cart.get("total_value"),
                    cart_items=cart.get("items", []),
                )

        # Try platforms data (backend format)
        platforms_data = payload.get("platforms", {})
        for platform, data in platforms_data.items():
            if "abandoned_carts" in data and data["abandoned_carts"]:
                cart = data["abandoned_carts"][0]
                customer = cart.get("customer", {})
                return ProcessedCustomer(
                    phone=self._normalize_phone(customer.get("phone")),
                    name=f"{customer.get('first_name', '')} {customer.get('last_name', '')}".strip()
                    or "Customer",
                    customer_type="abandoned_cart",
                    email=customer.get("email"),
                    cart_value=cart.get("total_value"),
                    cart_items=cart.get("products", []),
                )

        # Try legacy format
        if "phone_number" in payload:
            return ProcessedCustomer(
                phone=self._normalize_phone(payload["phone_number"]),
                name=payload.get("customer_name", "Customer"),
                customer_type=payload.get("customer_type", "regular"),
                email=payload.get("customer_email"),
            )

        raise ValueError("Could not extract customer information from payload")

    def _extract_business(self, payload: Dict[str, Any]) -> ProcessedBusiness:
        """Extract business information"""
        # Try direct business object
        if "business" in payload:
            business = payload["business"]
            return ProcessedBusiness(
                name=business.get("name", "Your Business"),
                description=business.get("description", ""),
                website=business.get("website", ""),
                industry=business.get("industry"),
                phone=business.get("phone"),
            )

        # Try company object (backend format)
        if "company" in payload:
            company = payload["company"]
            return ProcessedBusiness(
                name=company.get("name", "Your Business"),
                description=company.get("business_category", ""),
                website=company.get("website", ""),
                industry=company.get("business_category"),
                phone=company.get("phone_number"),
            )

        # Try business_info (legacy)
        if "business_info" in payload:
            business = payload["business_info"]
            return ProcessedBusiness(
                name=business.get("company_name", "Your Business"),
                description=business.get("description", ""),
                website=business.get("website", ""),
                industry=business.get("industry"),
                phone=business.get("phone"),
            )

        # Try agent level business info
        if "agent" in payload:
            agent = payload["agent"]
            return ProcessedBusiness(
                name=agent.get("business_name", "Your Business"),
                description=agent.get("business_description", ""),
                website=agent.get("business_website", ""),
                industry=agent.get("business_industry"),
            )

        # Default fallback
        return ProcessedBusiness(name="Your Business", description="", website="")

    def _extract_agent(self, payload: Dict[str, Any]) -> ProcessedAgent:
        """Extract agent configuration"""
        # Try direct agent object
        if "agent" in payload:
            agent = payload["agent"]

            # Get voice configuration from multiple sources
            voice_id = agent.get("selected_voice_id") or agent.get("voice_id")
            selected_voice_id = agent.get("selected_voice_id")
            tts_provider = agent.get("tts_provider", "elevenlabs")
            language = agent.get("language", "en-US")

            # Check voice_config section for additional voice settings
            voice_config = payload.get("voice_config", {})
            if voice_config:
                # Use voice_id_external from voice_config if available
                if voice_config.get("voice_id_external") and not voice_id:
                    voice_id = voice_config.get("voice_id_external")
                    selected_voice_id = voice_config.get("voice_id_external")

                # Override provider and language if specified in voice_config
                if voice_config.get("provider"):
                    tts_provider = voice_config.get("provider")
                if voice_config.get("language"):
                    language = voice_config.get("language")

            print(
                f"🎤 DEBUG: Voice settings - voice_id: {voice_id}, provider: {tts_provider}, language: {language}"
            )

            return ProcessedAgent(
                name=agent.get("name", "AI Assistant"),
                tts_provider=tts_provider,
                language=language,
                voice_id=voice_id,
                selected_voice_id=selected_voice_id,
                voice_settings=agent.get("voice_settings", {}),
                personality=agent.get("personality"),
            )  # Try legacy format
        return ProcessedAgent(
            name=payload.get("agent_name", "AI Assistant"),
            tts_provider=payload.get("tts_provider", "elevenlabs"),
            language=payload.get("language", "en-US"),
            voice_id=payload.get("voice_id"),
            voice_settings=payload.get("voice_settings", {}),
            personality=payload.get("personality"),
        )

    def _extract_cart_data(self, payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract abandoned cart data"""
        cart_data = []

        # Direct abandoned carts
        if "abandoned_carts" in payload:
            cart_data.extend(payload["abandoned_carts"])

        # Platform specific cart data
        platform_data = payload.get("platform_data", {})
        for platform, data in platform_data.items():
            if "abandoned_carts" in data:
                for cart in data["abandoned_carts"]:
                    cart_with_platform = cart.copy()
                    cart_with_platform["platform"] = platform
                    cart_data.append(cart_with_platform)

        return cart_data

    def _extract_platform_data(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Extract platform-specific data"""
        return payload.get("platform_data", {})

    def _extract_metadata(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Extract metadata and additional information"""
        metadata = {
            "processed_at": datetime.now().isoformat(),
            "payload_type": self._detect_payload_type(payload),
            "source": payload.get("source", "unknown"),
        }

        # Add recovery analytics if available
        if "recovery_analytics" in payload:
            metadata["recovery_analytics"] = payload["recovery_analytics"]

        # Add summary if available
        if "summary" in payload:
            metadata["summary"] = payload["summary"]

        return metadata

    def _normalize_phone(self, phone: str) -> str:
        """Normalize phone number format"""
        if not phone:
            raise ValueError("Phone number is required")

        # Remove non-digit characters except +
        normalized = "".join(c for c in phone if c.isdigit() or c == "+")

        # Add + if not present and looks like international number
        if not normalized.startswith("+") and len(normalized) > 10:
            normalized = "+" + normalized

        # Validate length
        if len(normalized) < 10:
            raise ValueError(f"Invalid phone number: {phone}")

        return normalized

    def validate_processed_payload(self, processed: ProcessedPayload) -> List[str]:
        """
        Validate processed payload and return list of warnings

        Returns:
            List of warning messages (empty if no issues)
        """
        warnings = []

        # Check customer phone
        if not processed.customer.phone:
            warnings.append("Customer phone number is missing")
        elif len(processed.customer.phone) < 10:
            warnings.append("Customer phone number may be invalid")

        # Check business name
        if not processed.business.name or processed.business.name == "Your Business":
            warnings.append("Business name is generic or missing")

        # Check TTS provider
        if processed.agent.tts_provider not in ["elevenlabs", "twilio"]:
            warnings.append(f"Unknown TTS provider: {processed.agent.tts_provider}")

        # Check cart data for abandoned cart scenarios
        if (
            processed.customer.customer_type == "abandoned_cart"
            and not processed.cart_data
        ):
            warnings.append("Abandoned cart customer but no cart data found")

        return warnings

    def to_voice_agent_config(self, processed: ProcessedPayload) -> Dict[str, Any]:
        """
        Convert processed payload to voice agent configuration format

        Returns:
            Configuration dict for voice agent
        """
        return {
            "phone_number": processed.customer.phone,
            "customer_name": processed.customer.name,
            "customer_type": processed.customer.customer_type,
            "customer_email": processed.customer.email,
            "business_info": {
                "company_name": processed.business.name,
                "description": processed.business.description,
                "website": processed.business.website,
                "industry": processed.business.industry,
                "phone": processed.business.phone,
            },
            "agent_name": processed.agent.name,
            "tts_provider": processed.agent.tts_provider,
            "language": processed.agent.language,
            "voice_id": processed.agent.voice_id,
            "selected_voice_id": processed.agent.selected_voice_id,
            "voice_settings": processed.agent.voice_settings or {},
            "cart_data": processed.cart_data,
            "platform_data": processed.platform_data,
            "metadata": processed.metadata,
        }


def create_payload_processor() -> PayloadProcessor:
    """Create and return a PayloadProcessor instance"""
    return PayloadProcessor()
