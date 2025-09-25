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

    <div className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          {t("basicInfo.businessName")} <span className="text-red-500">*</span>
        </label>
        <input
          type="text"
          name="businessName"
          value={formData.businessName}
          onChange={(e) => onInputChange("businessName", e.target.value)}
          placeholder={t("basicInfo.businessNamePlaceholder")}
          className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
            errors.businessName ? "border-red-500" : "border-gray-300"
          }`}
        />
        {errors.businessName && (
          <p className="mt-1 text-sm text-red-600">{errors.businessName}</p>
        )}
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          {t("basicInfo.phoneNumber")} <span className="text-red-500">*</span>
        </label>
        <input
          type="tel"
          name="phoneNumber"
          value={formData.phoneNumber}
          onChange={(e) => onInputChange("phoneNumber", e.target.value)}
          placeholder={t("basicInfo.phoneNumberPlaceholder")}
          className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
            errors.phoneNumber ? "border-red-500" : "border-gray-300"
          }`}
        />
        {errors.phoneNumber && (
          <p className="mt-1 text-sm text-red-600">{errors.phoneNumber}</p>
        )}
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          {t("basicInfo.email")} <span className="text-red-500">*</span>
        </label>
        <input
          type="email"
          name="email"
          value={formData.email}
          onChange={(e) => onInputChange("email", e.target.value)}
          placeholder={t("basicInfo.emailPlaceholder")}
          className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
            errors.email ? "border-red-500" : "border-gray-300"
          }`}
        />
        {errors.email && (
          <p className="mt-1 text-sm text-red-600">{errors.email}</p>
        )}
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Password <span className="text-red-500">*</span>
        </label>
        <input
          type="password"
          name="password"
          value={formData.password}
          onChange={(e) => onInputChange("password", e.target.value)}
          placeholder="Enter a secure password"
          className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
            errors.password ? "border-red-500" : "border-gray-300"
          }`}
        />
        {errors.password && (
          <p className="mt-1 text-sm text-red-600">{errors.password}</p>
        )}
      </div>
    </div>
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
        <div
          key={category.value}
          onClick={() => onCategoryChange(category.value)}
          className={`
            p-6 border rounded-lg cursor-pointer hover:shadow-md transition-all duration-200
            ${
              formData.category === category.value
                ? "border-blue-500 bg-blue-50 ring-2 ring-blue-200"
                : "border-gray-200 hover:border-gray-300"
            }
          `}
        >
          <div className="text-center">
            <div className="text-4xl mb-3">{category.icon}</div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              {category.label}
            </h3>
            <p className="text-sm text-gray-600">{category.description}</p>
          </div>
        </div>
      ))}
    </div>

    {errors.category && (
      <p className="text-sm text-red-600">{errors.category}</p>
    )}
  </div>
));

// Simple StepProgress component if not available
const SimpleStepProgress: React.FC<{
  steps: Array<{
    id: number;
    title: string;
    description: string;
    isCompleted: boolean;
    isActive: boolean;
  }>;
}> = ({ steps }) => (
  <div className="flex justify-between mb-8">
    {steps.map((step, index) => (
      <div key={step.id} className="flex items-center flex-1">
        <div
          className={`flex items-center justify-center w-8 h-8 rounded-full text-sm font-medium ${
            step.isCompleted
              ? "bg-green-600 text-white"
              : step.isActive
              ? "bg-blue-600 text-white"
              : "bg-gray-200 text-gray-600"
          }`}
        >
          {step.id}
        </div>
        <div className="ml-3 flex-1">
          <p
            className={`text-sm font-medium ${
              step.isActive ? "text-blue-600" : "text-gray-600"
            }`}
          >
            {step.title}
          </p>
        </div>
        {index < steps.length - 1 && (
          <div className="flex-1 h-0.5 bg-gray-200 mx-4" />
        )}
      </div>
    ))}
  </div>
);

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
        value: "e-commerce" as BusinessCategory,
        label: t("category.ecommerce"),
        icon: "🛒",
        description: t("category.ecommerceDesc"),
      },
      {
        value: "car-rental" as BusinessCategory,
        label: t("category.carRental"),
        icon: "🚗",
        description: t("category.carRentalDesc"),
      },
      {
        value: "restaurant" as BusinessCategory,
        label: t("category.restaurant"),
        icon: "🍽️",
        description: t("category.restaurantDesc"),
      },
      {
        value: "service-based" as BusinessCategory,
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
      console.log("Category selected:", category); // Debug log
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

          <SimpleStepProgress steps={steps} />

          <div className="mt-8">
            {renderStepContent}

            <div className="flex flex-col sm:flex-row justify-between gap-4 mt-8 pt-6 border-t border-gray-200">
              <button
                onClick={handlePrevious}
                disabled={currentStep === STEP_IDS.BASIC_INFO}
                className={`px-6 py-2 rounded-md font-medium transition-colors order-2 sm:order-1 ${
                  currentStep === STEP_IDS.BASIC_INFO
                    ? "invisible"
                    : "bg-gray-600 hover:bg-gray-700 text-white"
                }`}
              >
                {t("navigation.back")}
              </button>

              {currentStep < TOTAL_STEPS ? (
                <button
                  onClick={handleNextClick}
                  className="px-8 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md font-medium transition-colors order-1 sm:order-2"
                >
                  {t("navigation.next")}
                </button>
              ) : (
                <button
                  onClick={handleSubmitClick}
                  disabled={isLoading}
                  className="px-8 py-2 bg-green-600 hover:bg-green-700 disabled:bg-green-400 text-white rounded-md font-medium transition-colors order-1 sm:order-2"
                >
                  {isLoading
                    ? t("navigation.completing")
                    : t("navigation.complete")}
                </button>
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

// Add displayName for debugging
BasicInfoStep.displayName = "BasicInfoStep";
CategoryStep.displayName = "CategoryStep";

export default BusinessRegistration;
