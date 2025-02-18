"use client";

import { Switch } from "@/components/ui/switch";
// import { Button } from "@/components/ui/button"
import { useState, useEffect } from "react";
import { Input } from "@/components/ui/input";
import {
  HoverCard,
  HoverCardContent,
  HoverCardTrigger,
} from "@/components/ui/hover-card";

import { ClientSidePiStatus, getPiStatuses } from "@/pi_functions/pi-status";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND


export default function Home() {

  // Defined here so it updates after a page reset? We probably want these states to be remembered even after a page refresh.
  // Also, they are specific to this component

  const [switchStates, setSwitchStates] = useState<boolean[]>([]); // Empty array
  // const [isConnecting, setIsConnecting] = useState(false);
  const [piStatuses, setPiStatuses] = useState<ClientSidePiStatus[]>([]);
  const [username, setUsername] = useState("");
  const [IPAddress, setIPAddress] = useState("");
  const [password, setPassword] = useState("");
  const [cameraModel, setCameraModel] = useState("");

  const fetchPiStatuses = async () => {
    console.log("STATUS REFRESH");
    const piArray = await getPiStatuses();
    setPiStatuses(piArray);
    setSwitchStates(piArray.map(pi => pi.connectionStatus));
  };

  useEffect(() => {
    fetchPiStatuses(); // Initial fetch
    const intervalId = setInterval(fetchPiStatuses, 5000); // Fetch every 5 seconds
  
    return () => {
      clearInterval(intervalId); // Cleanup on unmount
    };
  }, []); // Dependency array ensures it runs only once
  

  // Will get periodically rendered by React when getPiStatuses updated piStatuses
  const piDivs = piStatuses.map((pi, index) => (
    <div key={index} className="flex items-center justify-between">
      <HoverCard>
        <HoverCardTrigger><p className="text-lg text-green-500 hover:underline">{pi.username}</p></HoverCardTrigger>
        <HoverCardContent>
          IP Address - {pi.IPAddress}
          <br />
          Camera Model - {pi.cameraModel}
        </HoverCardContent>
      </HoverCard>
      
      {/* Wrapper for Switch and Status with consistent width */}
      <div className="flex items-center space-x-4 min-w-[200px]">
        <Switch
          checked={switchStates[index]}
          onCheckedChange={(checked) => {
            update_ssh(checked, index, pi);
          }}
        />
        <p className="min-w-[100px] text-center">
          {pi.connectionStatus ? "Connected" : "Disconnected"}
        </p>

        {/* Delete button */}
        <button
          onClick={() => handleDelete(pi.username, index)}
          className="text-red-500 hover:text-red-700"
        >
          X
        </button>
      </div>
    </div>
  ));

  const update_ssh = async (checked: boolean, index: number, pi: ClientSidePiStatus) => {
    setSwitchStates((prevStates) => {
        const newStates = [...prevStates];
        newStates[index] = checked;
        return newStates;
    });

    try {
        let response;
        if (checked) {
            response = await fetch(`${BACKEND_URL}/connect_over_ssh_${pi.username}`, {
                method: "POST",
                body: JSON.stringify({ enabled: true }),
                headers: { "Content-Type": "application/json" }
            });
        } else {
            response = await fetch(`${BACKEND_URL}/disconnect_from_ssh_${pi.username}`, {
                method: "POST",
                body: JSON.stringify({ enabled: false }),
                headers: { "Content-Type": "application/json" }
            });
        }

        const data = await response.json();
        const sshStatus = data.sshStatus; // Ensure backend returns the updated status
        console.log(`ssh status is ${sshStatus}`)

        // Update state based on actual backend response
        setSwitchStates((prevStates) => {
            const newStates = [...prevStates];
            newStates[index] = sshStatus; 
            return newStates;
        });

        // Refresh Pi statuses
        fetchPiStatuses();
    } catch (error) {
        console.error("Error updating SSH connection:", error);
    }
};

// Handle deletion of a Pi
const handleDelete = async (username: string, index: number) => {

  const isConfirmed = window.confirm(`Are you sure you want to delete the "${username}" configuration?`);
  if (isConfirmed) {
    try {
      const response = await fetch(`${BACKEND_URL}/remove_pi_${username}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
      });
  
      // response.ok just checks that it gets a response
      if (response.ok) {
        console.log("Pi successfully deleted from config file");
        
        // If i = index of deleted pi, it is excluded from the filtered arrays...
        setPiStatuses((prevPiStatuses) => prevPiStatuses.filter((_, i) => i !== index));
        setSwitchStates((prevStates) => prevStates.filter((_, i) => i !== index));
        fetchPiStatuses(); // Update div containing switches

      } else {
        console.error("Failed to delete the configured pi");
      }
    } catch (error) {
      console.error("Error:", error);
    }
  }
};

// Handles Add Pi form submission
const handleSubmit = async (e: React.FormEvent) => {
  e.preventDefault(); // Prevent the default form submission

  const formData = {
    username,
    IPAddress,
    password,
    cameraModel,
  };

  try {
    const response = await fetch(`${BACKEND_URL}/add_pi`, {
      method: "POST",
      body: JSON.stringify(formData), // This is data sent to the backend
      headers: { "Content-Type": "application/json" },
    });

    // response.ok just checks that it gets a response
    if (response.ok) {
      console.log("Pi configured successfully");
      // Reset the form or handle further UI updates
      setUsername("");
      setIPAddress("");
      setPassword("");
      setCameraModel("");

      fetchPiStatuses();
    } else {
      console.error("Failed to configure Pi");
    }
  } catch (error) {
    console.error("Error submitting form:", error);
  }
};

return (
  <div className="flex justify-center items-center min-h-screen bg-grey-100">
    <div className="w-full max-w-lg p-6 bg-white rounded-lg shadow-lg">
      <h1 className="text-2xl font-semibold text-center mb-6">Configured Raspberry Pis</h1>
      
      {/* Render the list of Pi statuses */}
      {piDivs}

      <hr className="my-6" />

      <h2 className="text-2xl font-semibold text-center mb-6">Configure Pi</h2>

      {/* Form with inputs for new data */}
      <form className="space-y-4" onSubmit={handleSubmit}>
        <Input
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
        />
        <Input
          placeholder="IP Address"
          value={IPAddress}
          onChange={(e) => setIPAddress(e.target.value)}
          required
        />
        <Input
          placeholder="Password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
        <Input
          placeholder="Camera Model"
          value={cameraModel}
          onChange={(e) => setCameraModel(e.target.value)}
          required
        />
        <button
          type="submit"
          className="w-full bg-green-500 text-white py-2 px-4 rounded-md hover:bg-green-600 transition duration-200"
        >
          Add Pi
        </button>
      </form>
    </div>
  </div>
  )
}