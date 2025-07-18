// An interface needs to be defined with the associated pydantic base class model
export interface ClientSidePiStatus {
    username: string;
    IPAddress: string;
    cameraModel: string;
    connectionStatus: boolean;
  }

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND

export const getPiStatuses = async (isAlreadyFetching: boolean = false): Promise<ClientSidePiStatus[]> => {
  try {
    if (!isAlreadyFetching) {
    }
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

export const getPiStatus = (username: string, isAlreadyFetching: boolean = false): Promise<boolean> => {
  if (isAlreadyFetching) {
    return Promise.resolve(true);
  }
  return fetch(`${BACKEND_URL}/get_pi_status/${username}`, {
    method: "GET",
    cache: "no-cache", // Bypass the cache
  })
    .then((response) => response.json())  // Directly return the boolean response
    .catch((error) => {
      console.error("Error fetching Pi status:", error);
      return false; // Return false if there's an error
    });
};



  