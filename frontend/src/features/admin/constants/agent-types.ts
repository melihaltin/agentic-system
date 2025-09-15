export const AGENT_COMMUNICATION_TYPES = {
  VOICE: 'voice' as const,
  CHAT: 'chat' as const,
  HYBRID: 'hybrid' as const,
} as const;

export const AGENT_CATEGORIES = {
  ECOMMERCE: 'ecommerce' as const,
  CAR_RENTAL: 'car-rental' as const,
  HOSPITALITY: 'hospitality' as const,
} as const;

export const PERSONALITY_OPTIONS = [
  'Helpful and professional',
  'Friendly and casual', 
  'Formal and business-like',
  'Warm and welcoming',
  'Patient and understanding',
] as const;

export const RESPONSE_SPEED_OPTIONS = [
  { value: 'fast', label: 'Fast (1-2 seconds)' },
  { value: 'normal', label: 'Normal (2-4 seconds)' },
  { value: 'slow', label: 'Slow (4-6 seconds)' },
] as const;

export const RESPONSE_STYLE_OPTIONS = [
  { value: 'concise', label: 'Concise and direct' },
  { value: 'detailed', label: 'Detailed explanations' },
  { value: 'conversational', label: 'Natural conversation' },
] as const;

export const LANGUAGE_OPTIONS = [
  'English (US)',
  'English (UK)',
  'Turkish',
  'Spanish',
  'French',
] as const;

// E-commerce platforms for integration
export const ECOMMERCE_PLATFORMS = [
  { id: 'shopify', name: 'Shopify', description: 'Shopify e-commerce platform' },
  { id: 'woocommerce', name: 'WooCommerce', description: 'WordPress WooCommerce plugin' },
  { id: 'magento', name: 'Magento', description: 'Magento e-commerce platform' },
  { id: 'prestashop', name: 'PrestaShop', description: 'PrestaShop e-commerce platform' },
  { id: 'bigcommerce', name: 'BigCommerce', description: 'BigCommerce platform' },
] as const;

// Car rental platforms
export const CAR_RENTAL_PLATFORMS = [
  { id: 'custom_booking', name: 'Custom Booking System', description: 'Custom car rental booking API' },
  { id: 'rentals_united', name: 'Rentals United', description: 'Car rental management system' },
  { id: 'booking_manager', name: 'Booking Manager', description: 'Fleet booking management' },
] as const;

// Platform fields configuration
export const PLATFORM_FIELDS = {
  shopify: [
    { id: 'apiKey', name: 'API Key', type: 'password', required: true, placeholder: 'Enter your Shopify API key' },
    { id: 'storeUrl', name: 'Store URL', type: 'url', required: true, placeholder: 'yourstore.myshopify.com' },
    { id: 'accessToken', name: 'Access Token', type: 'password', required: true, placeholder: 'Enter access token' },
  ],
  woocommerce: [
    { id: 'consumerKey', name: 'Consumer Key', type: 'text', required: true, placeholder: 'ck_...' },
    { id: 'consumerSecret', name: 'Consumer Secret', type: 'password', required: true, placeholder: 'cs_...' },
    { id: 'storeUrl', name: 'Store URL', type: 'url', required: true, placeholder: 'https://yourstore.com' },
  ],
  magento: [
    { id: 'accessToken', name: 'Access Token', type: 'password', required: true, placeholder: 'Enter access token' },
    { id: 'storeUrl', name: 'Store URL', type: 'url', required: true, placeholder: 'https://yourstore.com' },
  ],
  prestashop: [
    { id: 'apiKey', name: 'API Key', type: 'password', required: true, placeholder: 'Enter PrestaShop API key' },
    { id: 'storeUrl', name: 'Store URL', type: 'url', required: true, placeholder: 'https://yourstore.com' },
  ],
  bigcommerce: [
    { id: 'storeHash', name: 'Store Hash', type: 'text', required: true, placeholder: 'Enter store hash' },
    { id: 'accessToken', name: 'Access Token', type: 'password', required: true, placeholder: 'Enter access token' },
  ],
  custom_booking: [
    { id: 'apiEndpoint', name: 'API Endpoint', type: 'url', required: true, placeholder: 'https://api.yourcarrental.com' },
    { id: 'apiKey', name: 'API Key', type: 'password', required: true, placeholder: 'Enter API key' },
  ],
  rentals_united: [
    { id: 'username', name: 'Username', type: 'text', required: true, placeholder: 'Enter username' },
    { id: 'password', name: 'Password', type: 'password', required: true, placeholder: 'Enter password' },
  ],
  booking_manager: [
    { id: 'apiKey', name: 'API Key', type: 'password', required: true, placeholder: 'Enter API key' },
    { id: 'endpoint', name: 'Endpoint', type: 'url', required: true, placeholder: 'https://api.bookingmanager.com' },
  ],
} as const;
