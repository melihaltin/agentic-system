"use client";

import React, { useState, useEffect } from "react";
import { AgentType, VoiceAgentSettings } from "@/types/admin.types";
import {
  isVoiceAgent,
  getAgentConfigTabs,
} from "@/features/admin/utils/agent-helpers";
import { useVoiceOptions } from "@/features/admin/hooks/useVoiceOptions";
import { GeneralSettings } from "./GeneralSettings";
import { IntegrationSettings } from "./IntegrationSettings";
import { ModalFooter } from "./ModalFooter";
import { ModalHeader } from "./ModalHeader";
import { VoiceSettings } from "./VoiceSettings";
import { ModalTabs } from "./ModalTabs";

interface AgentConfigModalProps {
  isOpen: boolean;
  onClose: () => void;
  agent: AgentType;
  onSave: (updatedAgent: AgentType) => void;
}

const AgentConfigModal: React.FC<AgentConfigModalProps> = ({
  isOpen,
  onClose,
  agent,
  onSave,
}) => {
  const [formData, setFormData] = useState(agent);
  const [isSaving, setIsSaving] = useState(false);
  const [activeTab, setActiveTab] = useState("general");
  const [selectedPlatform, setSelectedPlatform] = useState<string>("");
  const [platformConfig, setPlatformConfig] = useState<Record<string, string>>(
    {}
  );
  const {
    voiceOptions,
    isLoading: isLoadingVoices,
    playVoicePreview,
  } = useVoiceOptions();

  useEffect(() => {
    if (isOpen) {
      setFormData(agent);
    }
  }, [isOpen, agent]);

  const tabs = getAgentConfigTabs(agent);

  const handleInputChange = (
    e: React.ChangeEvent<
      HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement
    >
  ) => {
    const { name, value, type } = e.target;

    if (type === "checkbox") {
      const checkbox = e.target as HTMLInputElement;
      setFormData((prev) => ({
        ...prev,
        settings: {
          ...prev.settings,
          [name]: checkbox.checked,
        },
      }));
    } else if (name === "voice") {
      const selectedVoice = voiceOptions.find((v) => v.id === value);
      if (selectedVoice && isVoiceAgent(agent)) {
        setFormData((prev) => ({
          ...prev,
          settings: {
            ...prev.settings,
            voice: selectedVoice,
          } as VoiceAgentSettings,
        }));
      }
    } else if (name === "platform") {
      setSelectedPlatform(value);
      setPlatformConfig({});
    } else if (name.startsWith("platform_")) {
      const fieldName = name.replace("platform_", "");
      setPlatformConfig((prev) => ({
        ...prev,
        [fieldName]: value,
      }));
    } else {
      setFormData((prev) => ({
        ...prev,
        settings: {
          ...prev.settings,
          [name]: type === "number" ? parseInt(value) : value,
        },
      }));
    }
  };

  const handleSave = async () => {
    setIsSaving(true);
    try {
      // Include platform configuration in the agent settings
      const updatedAgent = {
        ...formData,
        settings: {
          ...formData.settings,
          integrationConfigs: {
            ...formData.settings.integrationConfigs,
            [selectedPlatform]: platformConfig,
          },
        },
      };
      await onSave(updatedAgent);
    } finally {
      setIsSaving(false);
    }
  };

  const handleClose = () => {
    setFormData(agent);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex min-h-screen items-end justify-center px-4 pt-4 pb-20 text-center sm:block sm:p-0">
        <div
          className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"
          onClick={handleClose}
        />

        <div className="relative inline-block w-full max-w-4xl my-8 overflow-hidden text-left align-middle bg-white rounded-xl shadow-xl transition-all">
          <ModalHeader agent={agent} onClose={handleClose} />
          <ModalTabs
            tabs={tabs}
            activeTab={activeTab}
            onTabChange={setActiveTab}
          />

          <div className="px-6 py-6 max-h-96 overflow-y-auto">
            {activeTab === "general" && (
              <GeneralSettings
                agent={agent}
                formData={formData}
                onChange={handleInputChange}
              />
            )}

            {activeTab === "voice" && isVoiceAgent(agent) && (
              <VoiceSettings
                agent={agent}
                formData={formData}
                onChange={handleInputChange}
                voiceOptions={voiceOptions}
                isLoadingVoices={isLoadingVoices}
                onPlayPreview={playVoicePreview}
              />
            )}

            {activeTab === "integrations" && (
              <IntegrationSettings
                agent={agent}
                selectedPlatform={selectedPlatform}
                platformConfig={platformConfig}
                onChange={handleInputChange}
              />
            )}
          </div>

          <ModalFooter
            onClose={handleClose}
            onSave={handleSave}
            isSaving={isSaving}
          />
        </div>
      </div>
    </div>
  );
};

export default AgentConfigModal;
