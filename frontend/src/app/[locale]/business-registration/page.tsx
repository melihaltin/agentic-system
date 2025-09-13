"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { Input, Button, Select, Card, StepProgress } from "@/components/ui";
import {
  BusinessRegistrationData,
  BusinessRegistrationStep,
  BusinessRegistrationErrors,
  BusinessCategory,
  PlatformType,
} from "@/types";

const BusinessRegistration: React.FC = () => {
  const router = useRouter();
  const [currentStep, setCurrentStep] = useState(1);
  const [isLoading, setIsLoading] = useState(false);

  const [formData, setFormData] = useState<BusinessRegistrationData>({
    businessName: "",
    phoneNumber: "",
    email: "",
    category: "",
    platform: "",
    apiKey: "",
    apiSecret: "",
    additionalConfig: {},
  });

  const [errors, setErrors] = useState<BusinessRegistrationErrors>({});

  const steps: BusinessRegistrationStep[] = [
    {
      id: 1,
      title: "Temel Bilgiler",
      description: "İş bilgileriniz",
      isCompleted: currentStep > 1,
      isActive: currentStep === 1,
    },
    {
      id: 2,
      title: "İş Kategorisi",
      description: "Faaliyet alanınız",
      isCompleted: currentStep > 2,
      isActive: currentStep === 2,
    },
    {
      id: 3,
      title: "Platform Seçimi",
      description: "Kullandığınız platform",
      isCompleted: currentStep > 3,
      isActive: currentStep === 3,
    },
    {
      id: 4,
      title: "API Ayarları",
      description: "Entegrasyon bilgileri",
      isCompleted: currentStep > 4,
      isActive: currentStep === 4,
    },
  ];

  const businessCategories = [
    { value: "e-commerce", label: "E-Ticaret" },
    { value: "car-rental", label: "Araç Kiralama" },
    { value: "restaurant", label: "Restoran" },
    { value: "service-based", label: "Hizmet Tabanlı" },
  ];

  const getPlatformOptions = (category: BusinessCategory) => {
    const platforms = {
      "e-commerce": [
        { value: "shopify", label: "Shopify" },
        { value: "woocommerce", label: "WooCommerce" },
        { value: "magento", label: "Magento" },
        { value: "bigcommerce", label: "BigCommerce" },
        { value: "custom", label: "Özel Sistem" },
      ],
      "car-rental": [
        { value: "turo", label: "Turo" },
        { value: "getaround", label: "Getaround" },
        { value: "zipcar", label: "Zipcar" },
        { value: "custom", label: "Özel Sistem" },
      ],
      restaurant: [
        { value: "ubereats", label: "Uber Eats" },
        { value: "doordash", label: "DoorDash" },
        { value: "grubhub", label: "GrubHub" },
        { value: "custom", label: "Özel Sistem" },
      ],
      "service-based": [
        { value: "calendly", label: "Calendly" },
        { value: "square", label: "Square" },
        { value: "stripe", label: "Stripe" },
        { value: "custom", label: "Özel Sistem" },
      ],
    };
    return platforms[category] || [];
  };

  const getApiFieldsForPlatform = (platform: string) => {
    const apiFields = {
      shopify: {
        apiKey: "Shopify API Key",
        apiSecret: "Shopify Secret Key",
        additionalFields: [{ key: "shopUrl", label: "Shop URL" }],
      },
      woocommerce: {
        apiKey: "Consumer Key",
        apiSecret: "Consumer Secret",
        additionalFields: [{ key: "storeUrl", label: "Store URL" }],
      },
      stripe: {
        apiKey: "Publishable Key",
        apiSecret: "Secret Key",
        additionalFields: [],
      },
      calendly: {
        apiKey: "Personal Access Token",
        apiSecret: "",
        additionalFields: [
          { key: "organizationUri", label: "Organization URI" },
        ],
      },
      default: {
        apiKey: "API Key",
        apiSecret: "API Secret",
        additionalFields: [],
      },
    };
    return apiFields[platform as keyof typeof apiFields] || apiFields.default;
  };

  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    // Clear error when user starts typing
    if (errors[name as keyof BusinessRegistrationErrors]) {
      setErrors((prev) => ({ ...prev, [name]: undefined }));
    }
  };

  const handleAdditionalConfigChange = (key: string, value: string) => {
    setFormData((prev) => ({
      ...prev,
      additionalConfig: {
        ...prev.additionalConfig,
        [key]: value,
      },
    }));
  };

  const validateCurrentStep = (): boolean => {
    const newErrors: BusinessRegistrationErrors = {};

    switch (currentStep) {
      case 1:
        if (!formData.businessName.trim())
          newErrors.businessName = "İşletme adı gereklidir";
        if (!formData.phoneNumber.trim())
          newErrors.phoneNumber = "Telefon numarası gereklidir";
        if (!formData.email.trim()) newErrors.email = "E-posta gereklidir";
        else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email))
          newErrors.email = "Geçerli bir e-posta adresi giriniz";
        break;
      case 2:
        if (!formData.category)
          newErrors.category = "Kategori seçimi gereklidir";
        break;
      case 3:
        if (!formData.platform)
          newErrors.platform = "Platform seçimi gereklidir";
        break;
      case 4:
        if (!formData.apiKey.trim()) newErrors.apiKey = "API Key gereklidir";
        break;
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleNext = () => {
    if (validateCurrentStep() && currentStep < 4) {
      setCurrentStep(currentStep + 1);
    }
  };

  const handlePrevious = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleSubmit = async () => {
    if (!validateCurrentStep()) return;

    setIsLoading(true);
    try {
      // Here you would typically send the data to your API
      console.log("Submitting registration data:", formData);

      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 2000));

      // Redirect to success page or admin dashboard
      router.push("/admin");
    } catch (error) {
      console.error("Registration failed:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const renderStepContent = () => {
    switch (currentStep) {
      case 1:
        return (
          <div className="space-y-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">
              İşletme Bilgileriniz
            </h2>
            <Input
              label="İşletme Adı"
              name="businessName"
              value={formData.businessName}
              onChange={handleInputChange}
              error={errors.businessName}
              placeholder="Örnek: ABC Teknoloji Ltd."
              required
            />
            <Input
              label="Telefon Numarası"
              name="phoneNumber"
              type="tel"
              value={formData.phoneNumber}
              onChange={handleInputChange}
              error={errors.phoneNumber}
              placeholder="+90 555 123 45 67"
              required
            />
            <Input
              label="E-posta Adresi"
              name="email"
              type="email"
              value={formData.email}
              onChange={handleInputChange}
              error={errors.email}
              placeholder="ornek@firma.com"
              required
            />
          </div>
        );

      case 2:
        return (
          <div className="space-y-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">
              İş Kategorinizi Seçin
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {businessCategories.map((category) => (
                <Card
                  key={category.value}
                  isSelected={formData.category === category.value}
                  onClick={() =>
                    setFormData((prev) => ({
                      ...prev,
                      category: category.value as BusinessCategory,
                      platform: "", // Reset platform when category changes
                    }))
                  }
                  className="text-center"
                >
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    {category.label}
                  </h3>
                  <p className="text-sm text-gray-600">
                    {category.value === "e-commerce" &&
                      "Online satış platformları"}
                    {category.value === "car-rental" &&
                      "Araç kiralama hizmetleri"}
                    {category.value === "restaurant" &&
                      "Yemek servisi ve restoranlar"}
                    {category.value === "service-based" &&
                      "Hizmet tabanlı işletmeler"}
                  </p>
                </Card>
              ))}
            </div>
            {errors.category && (
              <p className="text-sm text-red-600">{errors.category}</p>
            )}
          </div>
        );

      case 3:
        return (
          <div className="space-y-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">
              Platform Seçimi
            </h2>
            {formData.category && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {getPlatformOptions(formData.category as BusinessCategory).map(
                  (platform) => (
                    <Card
                      key={platform.value}
                      isSelected={formData.platform === platform.value}
                      onClick={() =>
                        setFormData((prev) => ({
                          ...prev,
                          platform: platform.value,
                        }))
                      }
                      className="text-center"
                    >
                      <h3 className="text-lg font-semibold text-gray-900 mb-2">
                        {platform.label}
                      </h3>
                    </Card>
                  )
                )}
              </div>
            )}
            {errors.platform && (
              <p className="text-sm text-red-600">{errors.platform}</p>
            )}
          </div>
        );

      case 4:
        const apiConfig = getApiFieldsForPlatform(formData.platform);
        return (
          <div className="space-y-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">
              API Ayarları
            </h2>
            <div className="bg-blue-50 p-4 rounded-lg mb-6">
              <h3 className="font-semibold text-blue-900 mb-2">
                {formData.platform === "custom"
                  ? "Özel Sistem"
                  : formData.platform}{" "}
                - API Bilgileri
              </h3>
              <p className="text-sm text-blue-700">
                Entegrasyonu tamamlamak için gerekli API bilgilerini giriniz.
              </p>
            </div>
            <Input
              label={apiConfig.apiKey}
              name="apiKey"
              value={formData.apiKey}
              onChange={handleInputChange}
              error={errors.apiKey}
              type="password"
              required
            />
            {apiConfig.apiSecret && (
              <Input
                label={apiConfig.apiSecret}
                name="apiSecret"
                value={formData.apiSecret || ""}
                onChange={handleInputChange}
                type="password"
              />
            )}
            {apiConfig.additionalFields.map((field) => (
              <Input
                key={field.key}
                label={field.label}
                name={field.key}
                value={formData.additionalConfig?.[field.key] || ""}
                onChange={(e) =>
                  handleAdditionalConfigChange(field.key, e.target.value)
                }
              />
            ))}
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-lg shadow-sm p-8">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 text-center mb-2">
              İşletme Kaydı
            </h1>
            <p className="text-center text-gray-600">
              AI asistanınızı kullanmaya başlamak için birkaç adımda kayıt olun
            </p>
          </div>

          <StepProgress steps={steps} />

          <div className="mt-8">
            {renderStepContent()}

            <div className="flex justify-between mt-8 pt-6 border-t border-gray-200">
              <Button
                onClick={handlePrevious}
                disabled={currentStep === 1}
                className={`px-6 ${
                  currentStep === 1
                    ? "invisible"
                    : "bg-gray-600 hover:bg-gray-700"
                }`}
              >
                Geri
              </Button>

              {currentStep < 4 ? (
                <Button onClick={handleNext} className="px-8">
                  İleri
                </Button>
              ) : (
                <Button
                  onClick={handleSubmit}
                  isLoading={isLoading}
                  disabled={isLoading}
                  className="px-8 bg-green-600 hover:bg-green-700"
                >
                  {isLoading ? "Kaydediliyor..." : "Kaydı Tamamla"}
                </Button>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default BusinessRegistration;
