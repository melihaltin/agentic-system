"use client";

import React from "react";
import { useParams } from "next/navigation";
import { useTranslations } from "next-intl";
import {
  Building2,
  Bot,
  BarChart3,
  Settings,
  ChevronLeft,
  ChevronRight,
  LogOut,
  User,
} from "lucide-react";

// Update the import path if the tooltip component exists elsewhere, for example:
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
// If the correct path is different, adjust accordingly to match your project structure.
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Separator } from "@/components/ui/separator";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

import { AdminSection } from "@/types/admin.types";
import { useAuthStore } from "@/store/auth";
import { cn } from "@/lib/utils";
import { Button } from "../ui";
import { useRouter } from "next/navigation";

interface AdminSidebarProps {
  activeSection: AdminSection;
  onSectionChange: (section: AdminSection) => void;
  isCollapsed: boolean;
  onToggleCollapse: () => void;
}

const AdminSidebar: React.FC<AdminSidebarProps> = ({
  activeSection,
  onSectionChange,
  isCollapsed,
  onToggleCollapse,
}) => {
  const params = useParams();
  const locale = params.locale as string;
  const t = useTranslations("admin.sidebar");

  const profile = useAuthStore((state) => state.user);
  const user = useAuthStore((state) => state.profile);
  const logout = useAuthStore((state) => state.logout);
  const router = useRouter();

  const menuItems = [
    {
      id: "business-settings" as AdminSection,
      label: t("businessSettings"),
      icon: Building2,
      color: "text-blue-600",
      bgColor: "bg-blue-50 hover:bg-blue-100",
      activeColor: "bg-blue-100 text-blue-700",
    },
    {
      id: "my-agents" as AdminSection,
      label: t("myAgents"),
      icon: Bot,
      color: "text-green-600",
      bgColor: "bg-green-50 hover:bg-green-100",
      activeColor: "bg-green-100 text-green-700",
    },
    {
      id: "analytics" as AdminSection,
      label: t("analytics"),
      icon: BarChart3,
      color: "text-purple-600",
      bgColor: "bg-purple-50 hover:bg-purple-100",
      activeColor: "bg-purple-100 text-purple-700",
    },
    {
      id: "settings" as AdminSection,
      label: t("settings"),
      icon: Settings,
      color: "text-gray-600",
      bgColor: "bg-gray-50 hover:bg-gray-100",
      activeColor: "bg-gray-100 text-gray-700",
    },
  ];

  const handleSectionClick = (section: AdminSection) => {
    onSectionChange(section);
  };

  const handleLogout = async () => {
    try {
      await logout();
      // navigate to login with nextjs router
      router.push(`/${locale}/login`);
    } catch (error) {
      console.error("Logout error:", error);
    }
  };

  const getUserInitials = () => {
    const companyName = user?.company?.company_name;
    const email = profile?.email;

    if (companyName) {
      return companyName.charAt(0).toUpperCase();
    }
    if (email) {
      return email.charAt(0).toUpperCase();
    }
    return "A";
  };

  return (
    <TooltipProvider>
      <div
        className={cn(
          "bg-background border-r border-border transition-all duration-300 ease-in-out flex flex-col h-screen",
          isCollapsed ? "w-16" : "w-64"
        )}
      >
        {/* Header */}
        <div className="p-4 border-b border-border flex items-center justify-between">
          {!isCollapsed && (
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
                <Bot className="w-5 h-5 text-primary-foreground" />
              </div>
              <div>
                <h2 className="text-lg font-semibold text-foreground">
                  {t("adminPanel")}
                </h2>
              </div>
            </div>
          )}

          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                variant="ghost"
                size="icon"
                onClick={onToggleCollapse}
                className="h-8 w-8"
              >
                {isCollapsed ? (
                  <ChevronRight className="w-4 h-4" />
                ) : (
                  <ChevronLeft className="w-4 h-4" />
                )}
              </Button>
            </TooltipTrigger>
            <TooltipContent>
              {isCollapsed ? t("expandSidebar") : t("collapseSidebar")}
            </TooltipContent>
          </Tooltip>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-4">
          <div className="space-y-2">
            {menuItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeSection === item.id;

              const menuButton = (
                <Button
                  variant="ghost"
                  onClick={() => handleSectionClick(item.id)}
                  className={cn(
                    "w-full transition-all duration-200",
                    isCollapsed ? "h-10 px-2" : "h-10 px-3 justify-start",
                    isActive
                      ? item.activeColor
                      : "hover:bg-accent hover:text-accent-foreground"
                  )}
                >
                  <Icon
                    className={cn(
                      "h-4 w-4 flex-shrink-0",
                      isCollapsed ? "" : "mr-2"
                    )}
                  />
                  {!isCollapsed && (
                    <span className="text-sm font-medium">{item.label}</span>
                  )}
                </Button>
              );

              if (isCollapsed) {
                return (
                  <Tooltip key={item.id}>
                    <TooltipTrigger asChild>{menuButton}</TooltipTrigger>
                    <TooltipContent side="right">{item.label}</TooltipContent>
                  </Tooltip>
                );
              }

              return <div key={item.id}>{menuButton}</div>;
            })}
          </div>
        </nav>

        {/* User Info */}
        <div className="p-4 border-t border-border">
          {isCollapsed ? (
            <DropdownMenu>
              <Tooltip>
                <TooltipTrigger asChild>
                  <DropdownMenuTrigger asChild>
                    <Button
                      variant="ghost"
                      className="h-10 w-10 rounded-full p-0"
                    >
                      <Avatar className="h-8 w-8">
                        <AvatarFallback className="text-xs">
                          {getUserInitials()}
                        </AvatarFallback>
                      </Avatar>
                    </Button>
                  </DropdownMenuTrigger>
                </TooltipTrigger>
                <TooltipContent side="right">
                  {user?.company?.company_name || "Admin User"}
                </TooltipContent>
              </Tooltip>

              <DropdownMenuContent align="end" className="w-56">
                <DropdownMenuLabel className="font-normal">
                  <div className="flex flex-col space-y-1">
                    <p className="text-sm font-medium leading-none">
                      {user?.company?.company_name || "Admin User"}
                    </p>
                    <p className="text-xs leading-none text-muted-foreground">
                      {profile?.email}
                    </p>
                  </div>
                </DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem
                  onClick={handleLogout}
                  className="text-red-600 focus:text-red-600"
                >
                  <LogOut className="mr-2 h-4 w-4" />
                  <span>Çıkış Yap</span>
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          ) : (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button
                  variant="ghost"
                  className="h-auto p-2 justify-start w-full"
                >
                  <div className="flex items-center space-x-3 w-full">
                    <Avatar className="h-8 w-8">
                      <AvatarFallback className="text-sm">
                        {getUserInitials()}
                      </AvatarFallback>
                    </Avatar>
                    <div className="flex-1 min-w-0 text-left">
                      <p className="text-sm font-medium text-foreground truncate">
                        {user?.company?.company_name || "Admin User"}
                      </p>
                      <p className="text-xs text-muted-foreground truncate">
                        {profile?.email}
                      </p>
                    </div>
                  </div>
                </Button>
              </DropdownMenuTrigger>

              <DropdownMenuContent align="end" className="w-56">
                <DropdownMenuLabel className="font-normal">
                  <div className="flex flex-col space-y-1">
                    <p className="text-sm font-medium leading-none">
                      {user?.company?.company_name || "Admin User"}
                    </p>
                    <p className="text-xs leading-none text-muted-foreground">
                      {profile?.email}
                    </p>
                  </div>
                </DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem
                  onClick={handleLogout}
                  className="text-red-600 focus:text-red-600"
                >
                  <LogOut className="mr-2 h-4 w-4" />
                  <span>Log Out</span>
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          )}
        </div>
      </div>
    </TooltipProvider>
  );
};

export default AdminSidebar;
