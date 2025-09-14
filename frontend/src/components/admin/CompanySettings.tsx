"use client";

import React, { useState } from "react";
import { useParams } from "next/navigation";
import { useTranslations } from "next-intl";
import { useAuthStore } from "@/store/auth";
import { Input, Button } from "@/components/ui";
import { UserProfile } from "@/types/auth.types";

const ProfileSettings: React.FC = () => {
  const params = useParams();
  const locale = params.locale as string;
  const { profile, updateProfile, loading } = useAuthStore();
  const t = useTranslations("admin.profileSettings");
  const tValidation = useTranslations("auth.validation");

  const [formData, setFormData] = useState<Partial<UserProfile>>({
    full_name: profile?.full_name || "",
    email: profile?.email || "",
  });

  const [errors, setErrors] = useState<Partial<UserProfile>>({});
  const [isEditing, setIsEditing] = useState(false);
  const [successMessage, setSuccessMessage] = useState("");

  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    const { name, value } = e.target;
    setFormData((prev: Partial<UserProfile>) => ({ ...prev, [name]: value }));
    // Clear error when user starts typing
    if (errors[name as keyof UserProfile]) {
      setErrors((prev: Partial<UserProfile>) => ({
        ...prev,
        [name]: undefined,
      }));
    }
    // Clear success message when user makes changes
    if (successMessage) {
      setSuccessMessage("");
    }
  };

  const validateForm = (): boolean => {
    const newErrors: Partial<UserProfile> = {};

    if (!formData.full_name?.trim()) {
      newErrors.full_name = tValidation("required", { field: "Full Name" });
    }

    if (!formData.email?.trim()) {
      newErrors.email = tValidation("required", { field: "Email" });
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = tValidation("invalidEmail");
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) return;

    try {
      await updateProfile(formData);
      setIsEditing(false);
      setSuccessMessage("Profile updated successfully!");
      setTimeout(() => setSuccessMessage(""), 5000);
    } catch (error) {
      console.error("Update failed:", error);
    }
  };

  const handleCancel = () => {
    // Reset form data to original profile data
    setFormData({
      full_name: profile?.full_name || "",
      email: profile?.email || "",
    });
    setErrors({});
    setIsEditing(false);
    setSuccessMessage("");
  };

  return (
    <div className="bg-white shadow-sm rounded-lg">
      <div className="px-6 py-4 border-b border-gray-200">
        <div className="flex justify-between items-center">
          <h2 className="text-xl font-semibold text-gray-900">
            Profile Settings
          </h2>
          {!isEditing && (
            <Button
              onClick={() => setIsEditing(true)}
              variant="primary"
              size="sm"
            >
              Edit Profile
            </Button>
          )}
        </div>
      </div>

      <div className="p-6">
        {successMessage && (
          <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-md">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg
                  className="h-5 w-5 text-green-400"
                  viewBox="0 0 20 20"
                  fill="currentColor"
                >
                  <path
                    fillRule="evenodd"
                    d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                    clipRule="evenodd"
                  />
                </svg>
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium text-green-800">
                  {successMessage}
                </p>
              </div>
            </div>
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="grid grid-cols-1 gap-6 mb-6">
            <Input
              label="Full Name"
              name="full_name"
              value={formData.full_name || ""}
              onChange={handleInputChange}
              error={errors.full_name}
              disabled={!isEditing}
              required
            />

            <Input
              label="Email"
              name="email"
              type="email"
              value={formData.email || ""}
              onChange={handleInputChange}
              error={errors.email}
              disabled={!isEditing}
              required
            />
          </div>

          {/* Profile Creation Date */}
          {profile?.created_at && (
            <div className="mb-6 p-4 bg-gray-50 rounded-lg">
              <h3 className="text-sm font-medium text-gray-900 mb-2">
                System Information
              </h3>
              <p className="text-sm text-gray-600">
                Registration Date:{" "}
                {new Date(profile.created_at).toLocaleDateString(
                  locale === "tr" ? "tr-TR" : "en-US",
                  {
                    year: "numeric",
                    month: "long",
                    day: "numeric",
                    hour: "2-digit",
                    minute: "2-digit",
                  }
                )}
              </p>
            </div>
          )}

          {isEditing && (
            <div className="flex justify-end space-x-3">
              <Button
                type="button"
                variant="secondary"
                onClick={handleCancel}
                disabled={loading}
              >
                Cancel
              </Button>
              <Button type="submit" isLoading={loading} disabled={loading}>
                {loading ? "Saving..." : "Save"}
              </Button>
            </div>
          )}
        </form>
      </div>
    </div>
  );
};

export default ProfileSettings;
