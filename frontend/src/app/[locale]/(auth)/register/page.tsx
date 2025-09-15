"use client";

import React, { useState, useCallback, useMemo } from "react";
import Link from "next/link";
import { useRouter, useParams } from "next/navigation";
import { useTranslations } from "next-intl";
import { useAuthStore } from "@/store/auth";
import LanguageSwitcher from "@/components/LanguageSwitcher";
import { Input, Button, Select, Card, StepProgress } from "@/components/ui";
import {
  BusinessRegistrationData,
  BusinessRegistrationStep,
  BusinessRegistrationErrors,
  BusinessCategory,
} from "@/types";
import { BusinessRegistrationData as AuthBusinessRegistrationData } from "@/types/auth.types";

// Constants
const TOTAL_STEPS = 2;
const STEP_IDS = {
  BASIC_INFO: 1,
  CATEGORY: 2,
} as const;

// Types
interface FormData extends BusinessRegistrationData {
  password: string;
}

interface FormErrors extends BusinessRegistrationErrors {
  password?: string;
}

// Custom hook for business registration logic
const useBusinessRegistration = () => {
  const [currentStep, setCurrentStep] = useState<number>(STEP_IDS.BASIC_INFO);
  const [isLoading, setIsLoading] = useState(false);
  const [formData, setFormData] = useState<FormData>({
    businessName: "",
    phoneNumber: "",
    email: "",
    password: "",
    category: "",
  });
  const [errors, setErrors] = useState<FormErrors>({});

  const handleInputChange = useCallback((name: string, value: string) => {
    setFormData((prev) => ({ ...prev, [name]: value }));

    // Clear error when user starts typing
    setErrors((prev) => {
      if (prev[name as keyof FormErrors]) {
        const newErrors = { ...prev };
        delete newErrors[name as keyof FormErrors];
        return newErrors;
      }
      return prev;
    });
  }, []);

  const validateCurrentStep = useCallback(
    (tValidation: any): boolean => {
      const newErrors: FormErrors = {};

      switch (currentStep) {
        case STEP_IDS.BASIC_INFO:
          if (!formData.businessName.trim()) {
            newErrors.businessName = tValidation("businessNameRequired");
          }
          if (!formData.phoneNumber.trim()) {
            newErrors.phoneNumber = tValidation("phoneRequired");
          }
          if (!formData.email.trim()) {
            newErrors.email = tValidation("emailRequired");
          } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
            newErrors.email = tValidation("invalidEmail");
          }
          if (!formData.password.trim()) {
            newErrors.password = "Password is required";
          } else if (formData.password.length < 6) {
            newErrors.password = "Password must be at least 6 characters";
          }
          break;

        case STEP_IDS.CATEGORY:
          if (!formData.category) {
            newErrors.category = tValidation("categoryRequired");
          }
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
        setCurrentStep((prev) => prev + 1);
      }
    },
    [currentStep, validateCurrentStep]
  );

  const handlePrevious = useCallback(() => {
    if (currentStep > 1) {
      setCurrentStep((prev) => prev - 1);
    }
  }, [currentStep]);

  const handleSubmit = useCallback(
    async (
      router: any,
      locale: string,
      tValidation: any,
      registerBusiness: any
    ) => {
      if (!validateCurrentStep(tValidation)) return;

      setIsLoading(true);
      try {
        const businessRegistrationData: AuthBusinessRegistrationData = {
          email: formData.email,
          password: formData.password,
          full_name: formData.businessName,
          company_name: formData.businessName,
          phone_number: formData.phoneNumber,
          business_category: formData.category,
        };

        const result = await registerBusiness(businessRegistrationData);
        router.push(`/${locale}/admin`);
      } catch (error: any) {
        console.error("Registration failed:", error);
        setErrors({ email: error?.message || "Registration failed" });
      } finally {
        setIsLoading(false);
      }
    },
    [formData, validateCurrentStep]
  );

  return {
    currentStep,
    isLoading,
    formData,
    errors,
    handleInputChange,
    handleNext,
    handlePrevious,
    handleSubmit,
  };
};

// Step Components - Memoized to prevent unnecessary re-renders
const BasicInfoStep = React.memo<{
  formData: FormData;
  errors: FormErrors;
  onInputChange: (name: string, value: string) => void;
  t: any;
}>(({ formData, errors, onInputChange, t }) => (
  <div className="space-y-6">
    <h2 className="text-2xl font-bold text-gray-900 mb-6">
      {t("basicInfo.title")}
    </h2>

    <Input
      label={t("basicInfo.businessName")}
      name="businessName"
      value={formData.businessName}
      onChange={(e) => onInputChange("businessName", e.target.value)}
      error={errors.businessName}
      placeholder={t("basicInfo.businessNamePlaceholder")}
      required
    />

    <Input
      label={t("basicInfo.phoneNumber")}
      name="phoneNumber"
      type="tel"
      value={formData.phoneNumber}
      onChange={(e) => onInputChange("phoneNumber", e.target.value)}
      error={errors.phoneNumber}
      placeholder={t("basicInfo.phoneNumberPlaceholder")}
      required
    />

    <Input
      label={t("basicInfo.email")}
      name="email"
      type="email"
      value={formData.email}
      onChange={(e) => onInputChange("email", e.target.value)}
      error={errors.email}
      placeholder={t("basicInfo.emailPlaceholder")}
      required
    />

    <Input
      label="Password"
      name="password"
      type="password"
      value={formData.password}
      onChange={(e) => onInputChange("password", e.target.value)}
      error={errors.password}
      placeholder="Enter a secure password"
      required
    />
  </div>
));

const CategoryStep = React.memo<{
  formData: FormData;
  errors: FormErrors;
  onCategoryChange: (category: BusinessCategory) => void;
  businessCategories: Array<{
    value: BusinessCategory;
    label: string;
    icon: string;
    description: string;
  }>;
  t: any;
}>(({ formData, errors, onCategoryChange, businessCategories, t }) => (
  <div className="space-y-6">
    <h2 className="text-2xl font-bold text-gray-900 mb-6">
      {t("category.title")}
    </h2>

    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      {businessCategories.map((category) => (
        <Card
          key={category.value}
          isSelected={formData.category === category.value}
          onClick={() => onCategoryChange(category.value)}
          className="text-center cursor-pointer hover:shadow-md transition-shadow"
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
));

// Main Component
const BusinessRegistration: React.FC = () => {
  const router = useRouter();
  const params = useParams();
  const locale = params.locale as string;
  const { registerBusiness } = useAuthStore();
  const t = useTranslations("auth.businessRegistration");
  const tValidation = useTranslations("auth.businessRegistration.validation");

  const {
    currentStep,
    isLoading,
    formData,
    errors,
    handleInputChange,
    handleNext,
    handlePrevious,
    handleSubmit,
  } = useBusinessRegistration();

  // Memoized configurations
  const businessCategories = useMemo(
    () => [
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
    ],
    [t]
  );

  const steps = useMemo(
    () => [
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
    ],
    [currentStep, t]
  );

  // Event handlers
  const handleCategoryChange = useCallback(
    (category: BusinessCategory) => {
      handleInputChange("category", category);
      handleInputChange("platform", ""); // Reset platform when category changes
    },
    [handleInputChange]
  );

  const handlePlatformChange = useCallback(
    (platform: string) => {
      handleInputChange("platform", platform);
    },
    [handleInputChange]
  );

  const handleNextClick = useCallback(() => {
    handleNext(tValidation);
  }, [handleNext, tValidation]);

  const handleSubmitClick = useCallback(() => {
    handleSubmit(router, locale, tValidation, registerBusiness);
  }, [handleSubmit, router, locale, tValidation, registerBusiness]);

  // Render step content
  const renderStepContent = useMemo(() => {
    switch (currentStep) {
      case STEP_IDS.BASIC_INFO:
        return (
          <BasicInfoStep
            formData={formData}
            errors={errors}
            onInputChange={handleInputChange}
            t={t}
          />
        );
      case STEP_IDS.CATEGORY:
        return (
          <CategoryStep
            formData={formData}
            errors={errors}
            onCategoryChange={handleCategoryChange}
            businessCategories={businessCategories}
            t={t}
          />
        );
      default:
        return null;
    }
  }, [
    currentStep,
    formData,
    errors,
    handleInputChange,
    handleCategoryChange,
    businessCategories,
    t,
  ]);

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
            {renderStepContent}

            <div className="flex flex-col sm:flex-row justify-between gap-4 mt-8 pt-6 border-t border-gray-200">
              <Button
                onClick={handlePrevious}
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
