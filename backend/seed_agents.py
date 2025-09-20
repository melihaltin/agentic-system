#!/usr/bin/env python3

import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

url = os.environ.get("SUPABASE_URL")
service_key = os.environ.get("SUPABASE_SERVICE_KEY")

supabase: Client = create_client(url, service_key)


def seed_agent_data():
    """Mock data'dan agent template'leri veritabanına yükler"""

    try:
        print("🚀 Starting agent data seeding...")

        # İlk olarak sektörleri kontrol edelim
        sectors_response = supabase.table("sectors").select("*").execute()
        print(f"📊 Found {len(sectors_response.data)} sectors")

        if not sectors_response.data:
            print("❌ No sectors found! Please run migrations first.")
            return

        # Integration providers'ı kontrol edelim
        providers_response = (
            supabase.table("integration_providers").select("*").execute()
        )
        print(f"🔌 Found {len(providers_response.data)} integration providers")

        # Agent templates'i kontrol edelim
        templates_response = supabase.table("agent_templates").select("*").execute()
        print(f"🤖 Found {len(templates_response.data)} existing agent templates")

        # Eğer zaten template'ler varsa, kullanıcıya soralım
        if templates_response.data:
            response = input(
                "⚠️ Agent templates already exist. Do you want to continue? (y/N): "
            )
            if response.lower() != "y":
                print("❌ Seeding cancelled by user")
                return

        # Integration Agent Mappings ekleyelim
        print("🔗 Creating integration-agent mappings...")

        # E-commerce agent'lar için Shopify entegrasyonu
        ecommerce_templates = (
            supabase.table("agent_templates")
            .select("*")
            .eq("agent_type", "voice")
            .execute()
        )
        shopify_provider = (
            supabase.table("integration_providers")
            .select("*")
            .eq("slug", "shopify")
            .execute()
        )

        if ecommerce_templates.data and shopify_provider.data:
            for template in ecommerce_templates.data:
                if "ecommerce" in template["slug"] or "shopping" in template["slug"]:
                    mapping_data = {
                        "agent_template_id": template["id"],
                        "provider_id": shopify_provider.data[0]["id"],
                        "is_required": True,
                        "enabled_features": [
                            "read_products",
                            "update_inventory",
                            "create_orders",
                            "track_shipments",
                        ],
                    }

                    # Önce var mı kontrol et
                    existing = (
                        supabase.table("integration_agent_mappings")
                        .select("*")
                        .eq("agent_template_id", template["id"])
                        .eq("provider_id", shopify_provider.data[0]["id"])
                        .execute()
                    )

                    if not existing.data:
                        supabase.table("integration_agent_mappings").insert(
                            mapping_data
                        ).execute()
                        print(f"✅ Created mapping: {template['name']} -> Shopify")

        # Car rental agent için booking system entegrasyonu
        car_rental_templates = (
            supabase.table("agent_templates")
            .select("*")
            .filter("slug", "like", "*car-rental*")
            .execute()
        )
        booking_provider = (
            supabase.table("integration_providers")
            .select("*")
            .eq("slug", "booking-system")
            .execute()
        )

        if car_rental_templates.data and booking_provider.data:
            for template in car_rental_templates.data:
                mapping_data = {
                    "agent_template_id": template["id"],
                    "provider_id": booking_provider.data[0]["id"],
                    "is_required": True,
                    "enabled_features": [
                        "read_vehicles",
                        "create_booking",
                        "cancel_booking",
                        "update_booking",
                    ],
                }

                # Önce var mı kontrol et
                existing = (
                    supabase.table("integration_agent_mappings")
                    .select("*")
                    .eq("agent_template_id", template["id"])
                    .eq("provider_id", booking_provider.data[0]["id"])
                    .execute()
                )

                if not existing.data:
                    supabase.table("integration_agent_mappings").insert(
                        mapping_data
                    ).execute()
                    print(f"✅ Created mapping: {template['name']} -> Booking System")

        # Sector Agent Availability ekleyelim
        print("🎯 Creating sector-agent availability...")

        # E-commerce sektörü için agent'ları ekle
        ecommerce_sector = (
            supabase.table("sectors").select("*").eq("slug", "e-commerce").execute()
        )
        if ecommerce_sector.data:
            sector_id = ecommerce_sector.data[0]["id"]

            ecommerce_templates = (
                supabase.table("agent_templates").select("*").execute()
            )
            for template in ecommerce_templates.data:
                if template["sector_id"] == sector_id:
                    availability_data = {
                        "sector_id": sector_id,
                        "agent_template_id": template["id"],
                        "is_recommended": template.get("is_featured", False),
                        "availability_status": "available",
                    }

                    # Önce var mı kontrol et
                    existing = (
                        supabase.table("sector_agent_availability")
                        .select("*")
                        .eq("sector_id", sector_id)
                        .eq("agent_template_id", template["id"])
                        .execute()
                    )

                    if not existing.data:
                        supabase.table("sector_agent_availability").insert(
                            availability_data
                        ).execute()
                        print(
                            f"✅ Added availability: {template['name']} -> E-commerce"
                        )

        # Car rental sektörü için agent'ları ekle
        car_rental_sector = (
            supabase.table("sectors").select("*").eq("slug", "car-rental").execute()
        )
        if car_rental_sector.data:
            sector_id = car_rental_sector.data[0]["id"]

            car_rental_templates = (
                supabase.table("agent_templates")
                .select("*")
                .eq("sector_id", sector_id)
                .execute()
            )
            for template in car_rental_templates.data:
                availability_data = {
                    "sector_id": sector_id,
                    "agent_template_id": template["id"],
                    "is_recommended": template.get("is_featured", False),
                    "availability_status": "available",
                }

                # Önce var mı kontrol et
                existing = (
                    supabase.table("sector_agent_availability")
                    .select("*")
                    .eq("sector_id", sector_id)
                    .eq("agent_template_id", template["id"])
                    .execute()
                )

                if not existing.data:
                    supabase.table("sector_agent_availability").insert(
                        availability_data
                    ).execute()
                    print(f"✅ Added availability: {template['name']} -> Car Rental")

        print("\n🎉 Agent data seeding completed successfully!")
        print("\n📊 Summary:")

        # Final summary
        final_templates = supabase.table("agent_templates").select("*").execute()
        final_mappings = (
            supabase.table("integration_agent_mappings").select("*").execute()
        )
        final_availability = (
            supabase.table("sector_agent_availability").select("*").execute()
        )

        print(f"   • Agent Templates: {len(final_templates.data)}")
        print(f"   • Integration Mappings: {len(final_mappings.data)}")
        print(f"   • Sector Availability: {len(final_availability.data)}")

    except Exception as e:
        print(f"💥 Error during seeding: {e}")
        import traceback

        traceback.print_exc()


def cleanup_agent_data():
    """Seeded data'yı temizler (test için)"""

    try:
        print("🧹 Cleaning up agent data...")

        # Sırayla temizle (foreign key constraints nedeniyle)
        supabase.table("sector_agent_availability").delete().neq(
            "id", "00000000-0000-0000-0000-000000000000"
        ).execute()
        supabase.table("integration_agent_mappings").delete().neq(
            "id", "00000000-0000-0000-0000-000000000000"
        ).execute()
        supabase.table("agent_templates").delete().neq(
            "id", "00000000-0000-0000-0000-000000000000"
        ).execute()

        print("✅ Cleanup completed!")

    except Exception as e:
        print(f"💥 Error during cleanup: {e}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "cleanup":
        cleanup_agent_data()
    else:
        seed_agent_data()
