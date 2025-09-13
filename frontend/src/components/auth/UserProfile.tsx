"use client";

import React from "react";
import { useAuth } from "@/contexts/AuthContext";

const UserProfile: React.FC = () => {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="animate-pulse flex items-center space-x-2">
        <div className="w-8 h-8 bg-gray-300 rounded-full"></div>
        <div className="w-24 h-4 bg-gray-300 rounded"></div>
      </div>
    );
  }

  if (!user) return null;

  return (
    <div className="flex items-center space-x-2">
      <div className="w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center text-sm font-medium">
        {user.email?.[0].toUpperCase()}
      </div>
      <div className="text-sm">
        <div className="font-medium text-gray-900">
          {user.user_metadata?.first_name && user.user_metadata?.last_name
            ? `${user.user_metadata.first_name} ${user.user_metadata.last_name}`
            : user.email}
        </div>
        <div className="text-gray-600">{user.email}</div>
      </div>
    </div>
  );
};

export default UserProfile;
