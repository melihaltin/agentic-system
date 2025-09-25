import { VoicesResponse, VoiceOption } from "@/types/admin.types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export class VoicesApiService {
  private static instance: VoicesApiService;

  public static getInstance(): VoicesApiService {
    if (!VoicesApiService.instance) {
      VoicesApiService.instance = new VoicesApiService();
    }
    return VoicesApiService.instance;
  }

  /**
   * Fetch all voices from the backend
   */
  async getVoices(isActive?: boolean): Promise<VoicesResponse> {
    try {
      const params = new URLSearchParams();
      if (isActive !== undefined) {
        params.append("is_active", isActive.toString());
      }

      const url = `${API_BASE_URL}/v1/voices/${
        params.toString() ? "?" + params.toString() : ""
      }`;

      const response = await fetch(url, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data: VoicesResponse = await response.json();
      return data;
    } catch (error) {
      console.error("Error fetching voices:", error);
      throw new Error("Failed to fetch voices");
    }
  }

  /**
   * Sync voices from ElevenLabs
   */
  async syncVoicesFromElevenLabs(): Promise<{
    success: boolean;
    message: string;
    synced_count: number;
  }> {
    try {
      const response = await fetch(`${API_BASE_URL}/v1/voices/sync`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error("Error syncing voices:", error);
      throw new Error("Failed to sync voices from ElevenLabs");
    }
  }

  /**
   * Play voice preview
   */
  async playVoicePreview(voice: VoiceOption): Promise<void> {
    if (!voice.sample_url) {
      throw new Error("No preview URL available for this voice");
    }

    try {
      // Create audio element and play
      const audio = new Audio(voice.sample_url);
      audio.preload = "metadata";

      return new Promise((resolve, reject) => {
        audio.addEventListener("canplaythrough", () => {
          audio
            .play()
            .then(() => resolve())
            .catch((error) => reject(new Error("Failed to play audio")));
        });

        audio.addEventListener("error", () => {
          reject(new Error("Failed to load audio"));
        });

        // Load the audio
        audio.load();
      });
    } catch (error) {
      console.error("Error playing voice preview:", error);
      throw new Error("Failed to play voice preview");
    }
  }
}

// Export singleton instance
export const voicesApi = VoicesApiService.getInstance();
