import { AgentType } from "@/types/admin.types";

// Sub-components for better organization
export const ModalHeader = ({
  agent,
  onClose,
}: {
  agent: AgentType;
  onClose: () => void;
}) => (
  <div className="bg-gray-50 px-6 py-4 border-b border-gray-200">
    <div className="flex items-center justify-between">
      <div className="flex items-center space-x-3">
        <div
          className={`w-10 h-10 rounded-lg ${agent.color} flex items-center justify-center text-white`}
        >
          <span className="text-lg">
            {agent.icon === "shopping-cart"
              ? "🛒"
              : agent.icon === "car"
              ? "🚗"
              : agent.icon === "support"
              ? "🤖"
              : "🤖"}
          </span>
        </div>
        <div>
          <h3 className="text-lg font-semibold text-gray-900">
            Configure {agent.name}
          </h3>
          <p className="text-sm text-gray-600">{agent.description}</p>
        </div>
      </div>
      <button
        onClick={onClose}
        className="text-gray-400 hover:text-gray-600 transition-colors"
      >
        <svg
          className="w-6 h-6"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M6 18L18 6M6 6l12 12"
          />
        </svg>
      </button>
    </div>
  </div>
);
