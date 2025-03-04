// An interface needs to be defined with the associated pydantic base class model
export interface ClientSidePiStatus {
    username: string;
    IPAddress: string;
    cameraModel: string;
    connectionStatus: boolean;
  }

  const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND
  
  export const getPiStatuses = async (): Promise<ClientSidePiStatus[]> => {
    try {
      const response = await fetch(`${BACKEND_URL}/get_raspberry_pi_statuses`, {
        method: "GET",
        cache: "no-cache", // Bypass the cache
      });
      return await response.json();
    } catch (error) {
      console.error("Error fetching Pi statuses:", error);
      return [];
    }
  };
  