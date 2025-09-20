export const AGENT_COMMUNICATION_TYPES = {
  VOICE: "voice" as const,
  CHAT: "chat" as const,
  HYBRID: "hybrid" as const,
} as const;

export const AGENT_CATEGORIES = {
  ECOMMERCE: "e-commerce" as const,
  CAR_RENTAL: "car-rental" as const,
  HOSPITALITY: "hospitality" as const,
} as const;

// E-commerce platforms for integration (Sadece Shopify)
export const ECOMMERCE_PLATFORMS = [
  {
    id: "shopify",
    name: "Shopify",
    description: "Shopify e-commerce platform integration",
  },
] as const;

// Car rental platforms
export const CAR_RENTAL_PLATFORMS = [
  {
    id: "custom_booking",
    name: "Custom Booking System",
    description: "Custom car rental booking API integration",
  },
] as const;

// Platform fields configuration (Sadece Shopify ve Custom Booking)
export const PLATFORM_FIELDS = {
  shopify: [
    {
      id: "apiKey",
      name: "Admin API Access Token",
      type: "password",
      required: true,
      placeholder: "shpat_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    },
    {
      id: "storeUrl",
      name: "Store URL",
      type: "url",
      required: true,
      placeholder: "yourstore.myshopify.com",
    },
    {
      id: "apiVersion",
      name: "API Version",
      type: "text",
      required: false,
      placeholder: "2024-01",
    },
  ],
  custom_booking: [
    {
      id: "apiEndpoint",
      name: "API Endpoint",
      type: "url",
      required: true,
      placeholder: "https://api.yourcarrental.com",
    },
    {
      id: "apiKey",
      name: "API Key",
      type: "password",
      required: true,
      placeholder: "Enter your booking system API key",
    },
  ],
} as const;
