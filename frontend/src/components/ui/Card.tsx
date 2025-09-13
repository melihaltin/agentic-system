import React from "react";

interface CardProps {
  children: React.ReactNode;
  className?: string;
  isSelected?: boolean;
  onClick?: () => void;
  hoverable?: boolean;
}

export const Card: React.FC<CardProps> = ({
  children,
  className = "",
  isSelected = false,
  onClick,
  hoverable = false,
}) => {
  const baseClasses = "bg-white rounded-lg shadow-sm border p-6";
  const selectableClasses = onClick
    ? "cursor-pointer transition-all duration-200 transform hover:scale-105"
    : "";
  const hoverClasses =
    hoverable || onClick ? "hover:shadow-lg hover:border-blue-300" : "";
  const selectedClasses = isSelected
    ? "border-blue-500 ring-2 ring-blue-200 shadow-md"
    : "border-gray-200";

  return (
    <div
      className={`${baseClasses} ${selectableClasses} ${hoverClasses} ${selectedClasses} ${className}`}
      onClick={onClick}
      role={onClick ? "button" : undefined}
      tabIndex={onClick ? 0 : undefined}
      onKeyDown={
        onClick
          ? (e) => {
              if (e.key === "Enter" || e.key === " ") {
                e.preventDefault();
                onClick();
              }
            }
          : undefined
      }
    >
      {children}
    </div>
  );
};
