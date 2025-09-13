"use client";

import React, { useState, useCallback } from "react";
import Link from "next/link";
import { useRouter, useParams } from "next/navigation";
import { useTranslations } from "next-intl";
import LanguageSwitcher from "@/components/LanguageSwitcher";
import { Input, Button, Select, Card, StepProgress } from "@/components/ui";
import {
  BusinessRegistrationData,
  BusinessRegistrationStep,
  BusinessRegistrationErrors,
  BusinessCategory,
} from "@/types";

// Constants
const TOTAL_STEPS = 4;
const STEP_IDS = {
  BASIC_INFO: 1,
  CATEGORY: 2,
  PLATFORM: 3,
  API_SETTINGS: 4,
} as const;

// Custom hooks
const useBusinessRegistration = () => {
  const [currentStep, setCurrentStep] = useState<number>(STEP_IDS.BASIC_INFO);
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

  const handleInputChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
      const { name, value } = e.target;
      setFormData((prev) => ({ ...prev, [name]: value }));

      // Clear error when user starts typing
      if (errors[name as keyof BusinessRegistrationErrors]) {
        setErrors((prev) => ({ ...prev, [name]: undefined }));
      }
    },
    [errors]
  );

  const handleAdditionalConfigChange = useCallback(
    (key: string, value: string) => {
      setFormData((prev) => ({
        ...prev,
        additionalConfig: {
          ...prev.additionalConfig,
          [key]: value,
        },
      }));
    },
    []
  );

  const handleCategoryChange = useCallback((category: BusinessCategory) => {
    setFormData((prev) => ({
      ...prev,
      category,
      platform: "", // Reset platform when category changes
    }));
  }, []);

  const handlePlatformChange = useCallback((platform: string) => {
    setFormData((prev) => ({ ...prev, platform }));
  }, []);

  const validateCurrentStep = useCallback(
    (tValidation: any): boolean => {
      const newErrors: BusinessRegistrationErrors = {};

      switch (currentStep) {
        case STEP_IDS.BASIC_INFO:
          if (!formData.businessName.trim())
            newErrors.businessName = tValidation("businessNameRequired");
          if (!formData.phoneNumber.trim())
            newErrors.phoneNumber = tValidation("phoneRequired");
          if (!formData.email.trim())
            newErrors.email = tValidation("emailRequired");
          else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email))
            newErrors.email = tValidation("invalidEmail");
          break;
        case STEP_IDS.CATEGORY:
          if (!formData.category)
            newErrors.category = tValidation("categoryRequired");
          break;
        case STEP_IDS.PLATFORM:
          if (!formData.platform)
            newErrors.platform = tValidation("platformRequired");
          break;
        case STEP_IDS.API_SETTINGS:
          if (!formData.apiKey.trim())
            newErrors.apiKey = tValidation("apiKeyRequired");
          break;
      }

      setErrors(newErrors);
      return Object.keys(newErrors).length === 0;
    },
    [currentStep, formData]
  );

  const handleNext = useCallback(
    (tValidation: any) => {
      if (validateCurrentStep(tValidation) && currentStep < TOTAL_STEPS) {
        setCurrentStep(currentStep + 1);
      }
    },
    [currentStep, validateCurrentStep]
  );

  const handlePrevious = useCallback(() => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  }, [currentStep]);

  const handleSubmit = useCallback(
    async (router: any, locale: string, tValidation: any) => {
      if (!validateCurrentStep(tValidation)) return;

      setIsLoading(true);
      try {
        // Here you would typically send the data to your API
        console.log("Submitting registration data:", formData);

        // Simulate API call
        await new Promise((resolve) => setTimeout(resolve, 2000));

        // Redirect to success page
        router.push(`/${locale}/registration-success`);
      } catch (error) {
        console.error("Registration failed:", error);
      } finally {
        setIsLoading(false);
      }
    },
    [formData, validateCurrentStep]
  );

  return {
    currentStep,
    setCurrentStep,
    isLoading,
    setIsLoading,
    formData,
    setFormData,
    errors,
    setErrors,
    handleInputChange,
    handleAdditionalConfigChange,
    handleCategoryChange,
    handlePlatformChange,
    validateCurrentStep,
    handleNext,
    handlePrevious,
    handleSubmit,
  };
};

const BusinessRegistration: React.FC = () => {
  const router = useRouter();
  const params = useParams();
  const locale = params.locale as string;
  const t = useTranslations("auth.businessRegistration");
  const tValidation = useTranslations("auth.businessRegistration.validation");

  const {
    currentStep,
    isLoading,
    formData,
    errors,
    handleInputChange,
    handleAdditionalConfigChange,
    handleCategoryChange,
    handlePlatformChange,
    handleNext,
    handlePrevious,
    handleSubmit,
  } = useBusinessRegistration();

  // Step configuration with better organization
  const steps: BusinessRegistrationStep[] = [
    {
      id: STEP_IDS.BASIC_INFO,
      title: t("steps.basicInfo"),
      description: t("steps.basicInfoDesc"),
      isCompleted: currentStep > STEP_IDS.BASIC_INFO,
      isActive: currentStep === STEP_IDS.BASIC_INFO,
    },
    {
      id: STEP_IDS.CATEGORY,
      title: t("steps.category"),
      description: t("steps.categoryDesc"),
      isCompleted: currentStep > STEP_IDS.CATEGORY,
      isActive: currentStep === STEP_IDS.CATEGORY,
    },
    {
      id: STEP_IDS.PLATFORM,
      title: t("steps.platform"),
      description: t("steps.platformDesc"),
      isCompleted: currentStep > STEP_IDS.PLATFORM,
      isActive: currentStep === STEP_IDS.PLATFORM,
    },
    {
      id: STEP_IDS.API_SETTINGS,
      title: t("steps.apiSettings"),
      description: t("steps.apiSettingsDesc"),
      isCompleted: currentStep > STEP_IDS.API_SETTINGS,
      isActive: currentStep === STEP_IDS.API_SETTINGS,
    },
  ];

  // Business categories configuration
  const businessCategories = [
    {
      value: "e-commerce" as const,
      label: t("category.ecommerce"),
      icon: "🛒",
      description: t("category.ecommerceDesc"),
    },
    {
      value: "car-rental" as const,
      label: t("category.carRental"),
      icon: "🚗",
      description: t("category.carRentalDesc"),
    },
    {
      value: "restaurant" as const,
      label: t("category.restaurant"),
      icon: "🍽️",
      description: t("category.restaurantDesc"),
    },
    {
      value: "service-based" as const,
      label: t("category.serviceBased"),
      icon: "⚙️",
      description: t("category.serviceBasedDesc"),
    },
  ];

  const getPlatformOptions = (category: BusinessCategory) => {
    const platforms = {
      "e-commerce": [
        { value: "shopify", label: t("platforms.shopify"), icon: "🛍️" },
        { value: "woocommerce", label: t("platforms.woocommerce"), icon: "🏪" },
        { value: "magento", label: t("platforms.magento"), icon: "📦" },
        { value: "bigcommerce", label: t("platforms.bigcommerce"), icon: "💼" },
        { value: "custom", label: t("platforms.custom"), icon: "⚡" },
      ],
      "car-rental": [
        { value: "turo", label: t("platforms.turo"), icon: "🚙" },
        { value: "getaround", label: t("platforms.getaround"), icon: "🚘" },
        { value: "zipcar", label: t("platforms.zipcar"), icon: "🔑" },
        { value: "custom", label: t("platforms.custom"), icon: "⚡" },
      ],
      restaurant: [
        { value: "ubereats", label: t("platforms.ubereats"), icon: "🍕" },
        { value: "doordash", label: t("platforms.doordash"), icon: "🥡" },
        { value: "grubhub", label: t("platforms.grubhub"), icon: "🍔" },
        { value: "custom", label: t("platforms.custom"), icon: "⚡" },
      ],
      "service-based": [
        { value: "calendly", label: t("platforms.calendly"), icon: "📅" },
        { value: "square", label: t("platforms.square"), icon: "💳" },
        { value: "stripe", label: t("platforms.stripe"), icon: "💰" },
        { value: "custom", label: t("platforms.custom"), icon: "⚡" },
      ],
    };
    return platforms[category] || [];
  };

  const getApiFieldsForPlatform = (platform: string) => {
    const apiFields = {
      shopify: {
        apiKey: t("apiFields.shopifyApiKey"),
        apiSecret: t("apiFields.shopifySecret"),
        additionalFields: [{ key: "shopUrl", label: t("apiFields.shopUrl") }],
      },
      woocommerce: {
        apiKey: t("apiFields.consumerKey"),
        apiSecret: t("apiFields.consumerSecret"),
        additionalFields: [{ key: "storeUrl", label: t("apiFields.storeUrl") }],
      },
      stripe: {
        apiKey: t("apiFields.publishableKey"),
        apiSecret: t("apiFields.secretKey"),
        additionalFields: [],
      },
      calendly: {
        apiKey: t("apiFields.personalAccessToken"),
        apiSecret: "",
        additionalFields: [
          { key: "organizationUri", label: t("apiFields.organizationUri") },
        ],
      },
      default: {
        apiKey: t("apiFields.apiKey"),
        apiSecret: t("apiFields.apiSecret"),
        additionalFields: [],
      },
    };
    return apiFields[platform as keyof typeof apiFields] || apiFields.default;
  };

  // Navigation handlers with proper parameters
  const handleNextClick = () => handleNext(tValidation);
  const handlePreviousClick = () => handlePrevious();
  const handleSubmitClick = () => handleSubmit(router, locale, tValidation);

  // Step Components
  const BasicInfoStep: React.FC = () => (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">
        {t("basicInfo.title")}
      </h2>
      <Input
        label={t("basicInfo.businessName")}
        name="businessName"
        value={formData.businessName}
        onChange={handleInputChange}
        error={errors.businessName}
        placeholder={t("basicInfo.businessNamePlaceholder")}
        required
      />
      <Input
        label={t("basicInfo.phoneNumber")}
        name="phoneNumber"
        type="tel"
        value={formData.phoneNumber}
        onChange={handleInputChange}
        error={errors.phoneNumber}
        placeholder={t("basicInfo.phoneNumberPlaceholder")}
        required
      />
      <Input
        label={t("basicInfo.email")}
        name="email"
        type="email"
        value={formData.email}
        onChange={handleInputChange}
        error={errors.email}
        placeholder={t("basicInfo.emailPlaceholder")}
        required
      />
    </div>
  );

  const CategoryStep: React.FC = () => (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">
        {t("category.title")}
      </h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {businessCategories.map((category) => (
          <Card
            key={category.value}
            isSelected={formData.category === category.value}
            onClick={() =>
              handleCategoryChange(category.value as BusinessCategory)
            }
            className="text-center"
          >
            <div className="text-4xl mb-3">{category.icon}</div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              {category.label}
            </h3>
            <p className="text-sm text-gray-600">{category.description}</p>
          </Card>
        ))}
      </div>
      {errors.category && (
        <p className="text-sm text-red-600">{errors.category}</p>
      )}
    </div>
  );

  const PlatformStep: React.FC = () => (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">
        {t("platform.title")}
      </h2>
      {formData.category && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {getPlatformOptions(formData.category as BusinessCategory).map(
            (platform) => (
              <Card
                key={platform.value}
                isSelected={formData.platform === platform.value}
                onClick={() => handlePlatformChange(platform.value)}
                className="text-center"
              >
                <div className="text-3xl mb-3">{platform.icon}</div>
                <h3 className="text-lg font-semibold text-gray-900">
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

  const ApiSettingsStep: React.FC = () => {
    const apiConfig = getApiFieldsForPlatform(formData.platform);

    return (
      <div className="space-y-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">
          {t("api.title")}
        </h2>
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 p-6 rounded-lg mb-6 border border-blue-200">
          <div className="flex items-center mb-3">
            <div className="w-10 h-10 bg-blue-500 rounded-lg flex items-center justify-center mr-3">
              <svg
                className="w-6 h-6 text-white"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M13 10V3L4 14h7v7l9-11h-7z"
                />
              </svg>
            </div>
            <div>
              <h3 className="font-semibold text-blue-900 text-lg">
                {formData.platform === "custom"
                  ? t("platforms.custom")
                  : formData.platform}{" "}
                - {t("api.integrationTitle")}
              </h3>
              <p className="text-sm text-blue-700">
                {t("api.integrationDesc")}
              </p>
            </div>
          </div>
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
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-4">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg
                className="h-5 w-5 text-yellow-400"
                viewBox="0 0 20 20"
                fill="currentColor"
              >
                <path
                  fillRule="evenodd"
                  d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
                  clipRule="evenodd"
                />
              </svg>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-yellow-800">
                {t("api.securityTitle")}
              </h3>
              <div className="mt-2 text-sm text-yellow-700">
                <p>{t("api.securityDesc")}</p>
              </div>
            </div>
          </div>
        </div>
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
  };

  const renderStepContent = () => {
    switch (currentStep) {
      case STEP_IDS.BASIC_INFO:
        return <BasicInfoStep />;
      case STEP_IDS.CATEGORY:
        return <CategoryStep />;
      case STEP_IDS.PLATFORM:
        return <PlatformStep />;
      case STEP_IDS.API_SETTINGS:
        return <ApiSettingsStep />;
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      {/* Language Switcher */}
      <div className="absolute top-4 right-4">
        <LanguageSwitcher />
      </div>

      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-lg shadow-sm p-8">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 text-center mb-2">
              {t("title")}
            </h1>
            <p className="text-center text-gray-600">{t("subtitle")}</p>
          </div>

          <StepProgress steps={steps} />

          <div className="mt-8">
            {renderStepContent()}

            <div className="flex flex-col sm:flex-row justify-between gap-4 mt-8 pt-6 border-t border-gray-200">
              <Button
                onClick={handlePreviousClick}
                disabled={currentStep === STEP_IDS.BASIC_INFO}
                className={`px-6 order-2 sm:order-1 ${
                  currentStep === STEP_IDS.BASIC_INFO
                    ? "invisible"
                    : "bg-gray-600 hover:bg-gray-700"
                }`}
              >
                {t("navigation.back")}
              </Button>

              {currentStep < TOTAL_STEPS ? (
                <Button
                  onClick={handleNextClick}
                  className="px-8 order-1 sm:order-2"
                >
                  {t("navigation.next")}
                </Button>
              ) : (
                <Button
                  onClick={handleSubmitClick}
                  isLoading={isLoading}
                  disabled={isLoading}
                  className="px-8 bg-green-600 hover:bg-green-700 order-1 sm:order-2"
                >
                  {isLoading
                    ? t("navigation.completing")
                    : t("navigation.complete")}
                </Button>
              )}
            </div>
          </div>
        </div>

        <div className="text-center mt-8">
          <span className="text-sm text-gray-600">
            {t("footer.haveAccount")}{" "}
            <Link
              href={`/${locale}/login`}
              className="font-medium text-blue-600 hover:text-blue-500 transition-colors"
            >
              {t("footer.signIn")}
            </Link>
          </span>
        </div>
      </div>
    </div>
  );
};

export default BusinessRegistration;
