export const ModalFooter = ({
  onClose,
  onSave,
  isSaving,
  isActivating = false,
}: {
  onClose: () => void;
  onSave: () => void;
  isSaving: boolean;
  isActivating?: boolean; // Yeni prop - activation durumu
}) => (
  <div className="bg-gray-50 px-6 py-4 border-t border-gray-200 flex justify-end space-x-3">
    <button
      onClick={onClose}
      disabled={isSaving}
      className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50"
    >
      Cancel
    </button>
    <button
      onClick={onSave}
      disabled={isSaving}
      className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 flex items-center space-x-2"
    >
      {isSaving && (
        <svg
          className="animate-spin h-4 w-4 text-white"
          fill="none"
          viewBox="0 0 24 24"
        >
          <circle
            className="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            strokeWidth="4"
          ></circle>
          <path
            className="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
          ></path>
        </svg>
      )}
      <span>
        {isSaving
          ? isActivating
            ? "Activating..."
            : "Saving..."
          : isActivating
          ? "Activate Agent"
          : "Save Changes"}
      </span>
    </button>
  </div>
);
