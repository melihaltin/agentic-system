#!/usr/bin/env python3
"""
Test script to verify configuration extraction for abandoned cart agent
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.ecommerce.abandoned_cart_agent.agent import AbandonedCartAgent
from services.voice_service import VoiceService
from services.tts.elevenlabs import ElevenLabsTTS


def test_config_extraction():
    """Test that business and customer names are extracted correctly from flat config"""

    # Your sample configuration
    sample_config = {
        "agent_id": "d1c671d7-23ae-4582-85df-4bc8d5f7a089",
        "agent_name": "TEST COMPANY",
        "agent_type": "abandoned_cart_recovery",
        "tts_provider": "elevenlabs",
        "voice_id": "pqHfZKP75CvOlQylNhV4",
        "language": "tr-TR",
        "business_name": "TechCorp",
        "business_website": "https://www.medifloy.com/",
        "business_phone": "5378212055",
        "customer_name": "Melih Altin",
        "customer_phone": "+31687611451",
        "customer_email": "melih@example.com",
        "customer_type": "returning",
        "cart_id": "cart_60f8e0cf",
        "cart_total": 499.98,
        "cart_currency": "USD",
        "cart_url": "https://https://www.medifloy.com//cart/recover/3fd4e3d221554208",
        "cart_products": [
            {
                "id": "prod_1708",
                "title": "Smart Fitness Watch",
                "price": "299.99",
                "currency": "USD",
                "image_url": "https://example.com/watch.jpg",
                "variant_id": "var_1350",
            },
            {
                "id": "prod_7909",
                "title": "Premium Wireless Headphones",
                "price": "199.99",
                "currency": "USD",
                "image_url": "https://example.com/headphones.jpg",
                "variant_id": "var_3165",
            },
        ],
        "abandoned_at": "2025-09-20T10:30:00Z",
        "recovery_attempts": 0,
        "personality": "friendly and helpful",
        "conversation_style": "professional yet casual",
        "max_conversation_length": 300,
        "timezone": "America/Denver",
        "template_slug": "ecommerce-abandoned-cart",
    }

    print("🧪 Testing configuration extraction...")
    print(f"📋 Sample config keys: {list(sample_config.keys())}")
    print(f"👤 Expected customer name: {sample_config.get('customer_name')}")
    print(f"🏢 Expected business name: {sample_config.get('business_name')}")
    print(f"🛒 Expected cart total: {sample_config.get('cart_total')}")
    print(
        f"📦 Expected cart products count: {len(sample_config.get('cart_products', []))}"
    )
    print()

    # Create mock voice service
    try:
        # Mock TTS service for testing
        class MockTTS:
            def text_to_speech(self, text, **kwargs):
                return "mock_audio_url"

        mock_voice_service = VoiceService(
            tts_provider=MockTTS(), stt_provider=None, audio_storage=None
        )

        # Create agent with sample config
        agent = AbandonedCartAgent(
            voice_service=mock_voice_service, call_config=sample_config
        )

        print("✅ Agent created successfully!")

        # Test dynamic system prompt creation
        system_prompt = agent._create_dynamic_system_prompt()
        print("📝 Generated system prompt:")
        print("-" * 50)
        print(system_prompt)
        print("-" * 50)
        print()

        # Check if customer name and business name are in the prompt
        customer_name_found = "Melih Altin" in system_prompt
        business_name_found = "TechCorp" in system_prompt
        cart_details_found = "Smart Fitness Watch" in system_prompt
        cart_total_found = "$499.98" in system_prompt

        print("🔍 Verification Results:")
        print(f"✅ Customer name found: {customer_name_found}")
        print(f"✅ Business name found: {business_name_found}")
        print(f"✅ Cart details found: {cart_details_found}")
        print(f"✅ Cart total found: {cart_total_found}")

        if all(
            [
                customer_name_found,
                business_name_found,
                cart_details_found,
                cart_total_found,
            ]
        ):
            print(
                "\n🎉 All tests PASSED! Configuration extraction is working correctly."
            )
        else:
            print(
                "\n❌ Some tests FAILED! Please check the configuration extraction logic."
            )

        # Test promo tool configuration
        print("\n🛠️ Testing promo tool configuration...")
        promo_tool = agent._create_promo_tool()
        print(f"✅ Promo tool created successfully")

        # Test initial greeting generation
        print("\n👋 Testing initial greeting...")
        greeting = agent.get_initial_greeting(sample_config["customer_phone"])
        print(f"Generated greeting: {greeting}")

        greeting_has_customer = "Melih Altin" in greeting
        greeting_has_business = "TechCorp" in greeting
        print(f"✅ Greeting includes customer name: {greeting_has_customer}")
        print(f"✅ Greeting includes business name: {greeting_has_business}")

    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_config_extraction()
