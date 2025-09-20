import { Card, Input } from "@/components/ui";
import {
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from "@/components/ui/Card";
import { AgentType } from "@/types/admin.types";
import { Label } from "@radix-ui/react-label";
import { Settings } from "lucide-react";

const GeneralSettings: React.FC<{
  formData: AgentType;
  onChange: (
    e: React.ChangeEvent<
      HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement
    >
  ) => void;
}> = ({ formData, onChange }) => (
  <div className="space-y-6">
    <Card className="border-gray-100 shadow-none">
      <CardHeader className="pb-4">
        <CardTitle className="text-base font-medium text-gray-900 flex items-center gap-2">
          <Settings className="w-4 h-4 text-gray-500" />
          Basic Settings
        </CardTitle>
        <CardDescription className="text-gray-500">
          Configure basic agent information
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          <Label
            htmlFor="customName"
            className="text-sm font-medium text-gray-700"
          >
            Agent Name
          </Label>
          <Input
            id="customName"
            name="customName"
            value={formData.settings.customName || ""}
            onChange={onChange}
            placeholder="Enter agent name"
            className="border-gray-200 focus:border-gray-300 focus:ring-gray-200"
          />
          <p className="text-xs text-gray-400">
            This name will be displayed to your customers
          </p>
        </div>
      </CardContent>
    </Card>
  </div>
);
export default GeneralSettings;
