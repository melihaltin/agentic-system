import { Button } from "@/components/ui";
import { AgentType } from "@/types/admin.types";
import { Bot, Car, ShoppingCart, X } from "lucide-react";

const AgentIcon: React.FC<{ icon: string; className?: string }> = ({
  icon,
  className = "w-5 h-5",
}) => {
  const icons = {
    "shopping-cart": ShoppingCart,
    car: Car,
    support: Bot,
    default: Bot,
  };

  const IconComponent = icons[icon as keyof typeof icons] || icons.default;
  return <IconComponent className={className} />;
};

export const ModalHeader: React.FC<{
  agent: AgentType;
  onClose: () => void;
}> = ({ agent, onClose }) => (
  <div className="flex items-center justify-between p-6 border-b border-gray-100">
    <div className="flex items-center gap-4">
      <div className="p-3 rounded-xl bg-gray-50 border border-gray-100">
        <AgentIcon icon={agent.icon} className="w-5 h-5 text-gray-600" />
      </div>
      <div>
        <h2 className="text-lg font-medium text-gray-900">{agent.name}</h2>
        <p className="text-sm text-gray-500 mt-0.5">{agent.description}</p>
      </div>
    </div>
    <Button
      variant="ghost"
      size="sm"
      onClick={onClose}
      className="h-8 w-8 p-0 hover:bg-gray-50"
    >
      <X className="h-4 w-4 text-gray-400" />
    </Button>
  </div>
);
