import React, { useState } from "react";
import { cn } from "@/lib/utils";

export const ModalTabs = ({
  tabs,
  activeTab,
  onTabChange,
}: {
  tabs: Array<{ id: string; label: string; icon: string }>;
  activeTab: string;
  onTabChange: (tab: string) => void;
}) => {
  return (
    <div className="w-full">
      <div className="border-b border-border">
        <nav className="flex space-x-8 px-6" aria-label="Tabs">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => onTabChange(tab.id)}
              className={cn(
                "group inline-flex items-center py-4 px-1 border-b-2 font-medium text-sm transition-all duration-200 ease-in-out",
                activeTab === tab.id
                  ? "border-primary text-primary"
                  : "border-transparent text-muted-foreground hover:text-foreground hover:border-muted-foreground/50"
              )}
              aria-current={activeTab === tab.id ? "page" : undefined}
            >
              <span
                className={cn(
                  "mr-2 text-base transition-transform duration-200",
                  activeTab === tab.id ? "scale-110" : "group-hover:scale-105"
                )}
              >
                {tab.icon}
              </span>
              <span className="whitespace-nowrap">{tab.label}</span>
            </button>
          ))}
        </nav>
      </div>
    </div>
  );
};
