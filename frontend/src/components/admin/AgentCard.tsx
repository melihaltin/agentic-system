"use client";

import React, { useMemo, useState } from "react";
import { AgentType } from "@/types/admin.types";
import {
  isVoiceAgent,
  getAgentTypeDisplayName,
} from "@/features/admin/utils/agent-helpers";
import {
  FiShoppingCart,
  FiHeadphones,
  FiMonitor,
  FiCheck,
  FiX,
  FiSettings,
  FiCamera,
  FiZap, // İkonu değiştirdik
} from "react-icons/fi";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import VoiceSelector from "./agent-config-modal/VoiceSelector";
import LanguageSelector from "./agent-config-modal/LanguageSelector";
import type { VoiceOption } from "@/types/admin.types";
import { useAuthStore } from "@/store/auth";

interface AgentCardProps {
  agent: AgentType;
  onToggle: (
    agentId: string,
    isActive: boolean,
    agentTemplateId?: string
  ) => void;
  onConfigure: (agent: AgentType) => void;
  onActivate?: (agent: AgentType) => void;
  isLoading?: boolean;
}

const AgentCard: React.FC<AgentCardProps> = ({
  agent,
  onToggle,
  onConfigure,
  onActivate,
  isLoading = false,
}) => {
  const [isTestOpen, setIsTestOpen] = useState(false);

  const [selectedVoice, setSelectedVoice] = useState<VoiceOption | undefined>(
    isVoiceAgent(agent) && "voice" in agent.settings
      ? (agent.settings as any).voice
      : undefined
  );
  const [selectedLanguage, setSelectedLanguage] = useState<string>(
    (isVoiceAgent(agent) && (agent.settings as any).language) ||
      selectedVoice?.language ||
      "en-US"
  );
  const [testPhone, setTestPhone] = useState<string>("");
  const [isSubmittingTest, setIsSubmittingTest] = useState(false);
  const [testResult, setTestResult] = useState<string | null>(null);

  const handleToggle = () => {
    const templateId =
      agent.isCompanyAgent === false
        ? agent.agentTemplateId || agent.id
        : undefined;
    onToggle(agent.id, !agent.isActive, templateId);
  };

  const isVoice = useMemo(() => isVoiceAgent(agent), [agent]);

  const handleOpenTest = () => {
    setIsTestOpen(true);
    setTestResult(null);
  };

  // Düzeltilmiş handleVoiceSelect fonksiyonu - sadece sesi değiştiriyor
  const handleVoiceSelect = (voice: VoiceOption) => {
    setSelectedVoice(voice);
    // Dili otomatik değiştirmiyoruz
  };

  const buildMockPayload = () => {
    const now = new Date().toISOString();

    const user = useAuthStore.getState().user;
    const profile = useAuthStore.getState().profile;

    const mock = {
      agent: {
        id: "d6df8592-cde1-4526-ab49-e1f3ce9b9b48",
        name: "IQRA - Abandoned Cart Recovery Agent",
        type: "abandoned_cart_recovery",
        template_slug: "ecommerce-abandoned-cart",
        is_configured: true,
        total_interactions: 0,
        selected_voice_id: "Xb7hH8MSUJpSbSDYk0k2",
        language: selectedLanguage,
        tts_provider: "elevenlabs",
      },
      company: {
        id: "6d59b8da-8674-48d7-889d-8055a1d6e990",
        name: profile?.company?.company_name || "Demo Company",
        business_category: "e-commerce",
        phone_number: "+1234567890",
        website: null,
        timezone: "UTC",
      },
      voice_config: {
        voice_id: "9fbf13f1-0bcc-44d8-987a-6d474f617e4f",
        name: "Alice",
        provider: "elevenlabs",
        voice_id_external: selectedVoice?.voice_id || "Xb7hH8MSUJpSbSDYk0k2",
        language: selectedLanguage,
      },
      platforms: {
        shopify: {
          platform: "shopify",
          company: "Melih Test Corp",
          abandoned_carts: [
            {
              id: "cart_8b723a6f",
              customer: {
                id: "cust_1001",
                email: "melih@example.com",
                first_name: "Melih",
                last_name: "Altin",
                phone: testPhone || "+1234567890",
                created_at: "2025-09-20T10:00:00Z",
              },
              products: [
                {
                  id: "prod_6486",
                  title: "Organic Coffee Beans",
                  price: "24.99",
                  currency: "USD",
                  image_url: "https://example.com/coffee.jpg",
                  variant_id: "var_2238",
                },
              ],
              total_value: 24.99,
              currency: "USD",
              abandoned_at: "2025-09-20T10:30:00Z",
              recovery_attempts: 0,
              cart_url: "https://None/cart/recover/a8e65d0ad21243dc",
              platform: "shopify",
              status: "abandoned",
            },
          ],
          total_abandoned_carts: 1,
          total_recovery_value: 24.99,
          generated_at: now,
          mock_data: true,
        },
      },
      summary: {
        total_platforms: 1,
        total_abandoned_carts: 1,
        total_recovery_value: 24.99,
        currencies: ["USD"],
      },
      metadata: {
        generated_at: now,
        payload_version: "1.0",
        service: "abandoned_cart_recovery",
      },
    } as const;

    return mock;
  };

  const submitTest = async () => {
    try {
      setIsSubmittingTest(true);
      setTestResult(null);

      if (!selectedVoice) {
        throw new Error("Please select a voice");
      }
      if (!testPhone || testPhone.replace(/\D/g, "").length < 7) {
        throw new Error("Please enter a valid phone number");
      }

      const payload = buildMockPayload();

      console.log("Test payload:", payload);
      const apiUrl =
        process.env.NEXT_PUBLIC_TEST_API_URL || "https://httpbin.org/post";

      // apiUrl/start-call

      const testUrl = `${apiUrl}/start-call`;

      const res = await fetch(testUrl, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const text = await res.text();
        throw new Error(`Request failed: ${res.status} ${text}`);
      }

      setTestResult("Test request sent successfully.");
    } catch (err: any) {
      setTestResult(err?.message || "Failed to send test request");
    } finally {
      setIsSubmittingTest(false);
    }
  };

  return (
    <>
      <div className="bg-white rounded-2xl border border-gray-100 hover:border-gray-200 transition-all duration-300 hover:shadow-lg group flex flex-col">
        <div className="flex-grow">
          {/* Header */}
          <div className="p-6 pb-4">
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center space-x-4">
                <div
                  className={`w-14 h-14 rounded-xl ${agent.color} flex items-center justify-center shadow-sm`}
                >
                  <AgentIcon iconName={agent.icon} />
                </div>
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-gray-900 mb-1">
                    {agent.originalName ?? agent.name}
                  </h3>
                  <p className="text-sm text-gray-500 leading-relaxed">
                    {agent.description}
                  </p>
                </div>
              </div>
              <StatusBadge isActive={agent.isActive} />
            </div>

            <div className="flex items-center space-x-6 text-xs text-gray-400">
              <span className="font-medium">
                {getAgentTypeDisplayName(agent.communicationType)}
              </span>
              <span>
                Updated {new Date(agent.lastUpdated).toLocaleDateString()}
              </span>
            </div>
          </div>

          {/* Settings Preview */}
          <div className="px-6 py-4 bg-gray-50/50">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-xs font-medium text-gray-600 mb-1">
                  Custom Name
                </p>
                <p className="text-sm text-gray-900">
                  {agent.settings.customName}
                </p>
              </div>
              <div>
                <p className="text-xs font-medium text-gray-600 mb-1">
                  Language
                </p>
                <p className="text-sm text-gray-900">
                  {agent.settings.language}
                </p>
              </div>
              {isVoiceAgent(agent) &&
                "voice" in agent.settings &&
                agent.settings.voice && (
                  <div>
                    <p className="text-xs font-medium text-gray-600 mb-1">
                      Voice
                    </p>
                    <p className="text-sm text-gray-900">
                      {agent.settings.voice.name}
                    </p>
                  </div>
                )}
              <div>
                <p className="text-xs font-medium text-gray-600 mb-1">
                  Integrations
                </p>
                <p className="text-sm text-gray-900">
                  {agent.requiredIntegrations.length} configured
                </p>
              </div>
            </div>
          </div>

          {/* Integration Status */}
          {agent.requiredIntegrations.length > 0 && (
            <div className="px-6 py-4 border-t border-gray-100">
              <p className="text-xs font-semibold text-gray-600 mb-3 uppercase tracking-wide">
                Integrations
              </p>
              <div className="flex flex-wrap gap-2">
                {agent.requiredIntegrations.map((integration) => {
                  const isConfigured = Object.keys(
                    agent.settings.integrationConfigs
                  ).includes(integration.id);
                  return (
                    <span
                      key={integration.id}
                      className={`inline-flex items-center px-3 py-1.5 rounded-full text-xs font-medium ${
                        isConfigured
                          ? "bg-emerald-50 text-emerald-700 border border-emerald-200"
                          : "bg-rose-50 text-rose-700 border border-rose-200"
                      }`}
                    >
                      {integration.name}
                      {isConfigured ? (
                        <FiCheck className="ml-1.5 w-3 h-3" />
                      ) : (
                        <FiX className="ml-1.5 w-3 h-3" />
                      )}
                    </span>
                  );
                })}
              </div>
            </div>
          )}
        </div>

        {/* Actions */}
        <div className="p-6 pt-4 border-t border-gray-100">
          <div className="flex items-center justify-between">
            {agent.isActive || agent.isCompanyAgent === true ? (
              <>
                <ToggleSwitch
                  isActive={agent.isActive}
                  onToggle={handleToggle}
                  isLoading={isLoading}
                />
                <button
                  onClick={() => onConfigure(agent)}
                  className="inline-flex items-center px-4 py-2 text-sm font-medium text-blue-600 bg-blue-50 rounded-xl hover:bg-blue-100 transition-colors group-hover:bg-blue-100"
                >
                  <FiSettings className="w-4 h-4 mr-2" />
                  Configure
                </button>
                {isVoice && (
                  <button
                    onClick={handleOpenTest}
                    className="inline-flex items-center px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-xl hover:bg-gray-200 transition-colors"
                  >
                    Test this agent
                  </button>
                )}
              </>
            ) : (
              onActivate && (
                <button
                  onClick={() => onActivate(agent)}
                  disabled={isLoading}
                  className="w-full inline-flex items-center justify-center px-6 py-3 text-sm font-semibold text-white bg-blue-600 rounded-xl hover:bg-blue-700 transition-all duration-300 transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:scale-100"
                >
                  <FiZap className="w-5 h-5 mr-2" />
                  Activate Agent
                </button>
              )
            )}
          </div>
        </div>
      </div>
      {isVoice && (
        <Dialog open={isTestOpen} onOpenChange={setIsTestOpen}>
          <DialogContent className="sm:max-w-xl">
            <DialogHeader>
              <DialogTitle>Test this agent</DialogTitle>
            </DialogHeader>
            <div className="space-y-5">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Select voice
                </label>
                <VoiceSelector
                  selectedVoice={selectedVoice}
                  onVoiceSelect={handleVoiceSelect}
                  className=""
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Language
                </label>
                <LanguageSelector
                  value={selectedLanguage}
                  onValueChange={setSelectedLanguage}
                  placeholder="Select a language"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Phone number to call
                </label>
                <input
                  type="tel"
                  inputMode="tel"
                  placeholder="e.g. +15551234567"
                  value={testPhone}
                  onChange={(e) => setTestPhone(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:border-gray-400 text-sm"
                />
                <p className="mt-1 text-xs text-gray-500">
                  Include country code, e.g. +90, +1
                </p>
              </div>
              {testResult && (
                <div
                  className="text-sm px-3 py-2 rounded border"
                  aria-live="polite"
                >
                  {testResult}
                </div>
              )}
            </div>
            <DialogFooter className="mt-4">
              <button
                onClick={() => setIsTestOpen(false)}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200"
                disabled={isSubmittingTest}
              >
                Cancel
              </button>
              <button
                onClick={submitTest}
                className="px-4 py-2 text-sm font-semibold text-white bg-blue-600 rounded-lg hover:bg-blue-700 disabled:opacity-50"
                disabled={isSubmittingTest}
              >
                {isSubmittingTest ? "Sending..." : "Send test"}
              </button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      )}
    </>
  );
};

// Sub-components
const AgentIcon = ({ iconName }: { iconName: string }) => {
  const iconMap = {
    "shopping-cart": <FiShoppingCart className="w-7 h-7 text-white" />,
    car: <FiCamera className="w-7 h-7 text-white" />,
    support: <FiHeadphones className="w-7 h-7 text-white" />,
  };

  return (
    iconMap[iconName as keyof typeof iconMap] || (
      <FiMonitor className="w-7 h-7 text-white" />
    )
  );
};

const StatusBadge = ({ isActive }: { isActive: boolean }) => (
  <span
    className={`inline-flex items-center px-3 py-1.5 rounded-full text-xs font-medium ${
      isActive
        ? "bg-emerald-50 text-emerald-700 border border-emerald-200"
        : "bg-gray-50 text-gray-600 border border-gray-200"
    }`}
  >
    <div
      className={`w-2 h-2 rounded-full mr-2 ${
        isActive ? "bg-emerald-500" : "bg-gray-400"
      }`}
    />
    {isActive ? "Active" : "Inactive"}
  </span>
);

const ToggleSwitch = ({
  isActive,
  onToggle,
  isLoading,
}: {
  isActive: boolean;
  onToggle: () => void;
  isLoading: boolean;
}) => (
  <div className="flex items-center space-x-3">
    <button
      onClick={onToggle}
      disabled={isLoading}
      className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 ${
        isActive ? "bg-emerald-500" : "bg-gray-200"
      } ${isLoading ? "opacity-50 cursor-not-allowed" : "cursor-pointer"}`}
    >
      <span
        className={`inline-block h-4 w-4 transform rounded-full bg-white shadow-sm transition-transform ${
          isActive ? "translate-x-6" : "translate-x-1"
        }`}
      />
    </button>
    <span className="text-sm font-medium text-gray-700">
      {isActive ? "Active" : "Inactive"}
    </span>
  </div>
);

export default AgentCard;
