import { Button } from "@/components/ui";
import { Loader2 } from "lucide-react";

export const ModalFooter = ({
  onClose,
  onSave,
  isSaving,
  isActivating = false,
}: {
  onClose: () => void;
  onSave: () => void;
  isSaving: boolean;
  isActivating?: boolean;
}) => (
  <div className="flex items-center justify-end space-x-3 border-t bg-background px-6 py-4">
    <Button
      variant="outline"
      onClick={onClose}
      disabled={isSaving}
      className="text-muted-foreground hover:text-foreground"
    >
      Cancel
    </Button>
    <Button
      onClick={onSave}
      disabled={isSaving}
      className="bg-sky-600 text-white hover:bg-sky-500 dark:bg-sky-700 dark:text-white dark:hover:bg-sky-700"
    >
      {isSaving && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
      {isSaving
        ? isActivating
          ? "Activating..."
          : "Saving..."
        : isActivating
        ? "Activate Agent"
        : "Save Changes"}
    </Button>
  </div>
);
