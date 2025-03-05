"use client";

import { Switch } from "@/components/ui/switch";
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

  const [switchStates, setSwitchStates] = useState<Record<string, boolean>>({});
  const [piStatuses, setPiStatuses] = useState<ClientSidePiStatus[]>([]);
  const [username, setUsername] = useState("");
  const [isAlreadyFetching, setAlreadyFetching] = useState<boolean>(false);
  const [IPAddress, setIPAddress] = useState("");
  const [password, setPassword] = useState("");
  const [cameraModel, setCameraModel] = useState("");

  const fetchPiStatuses = async (isAlreadyFetching: boolean) => {
    try {
      console.log("Fetching Pi Statuses...")
      const piArray = await getPiStatuses(isAlreadyFetching);
      setPiStatuses(piArray);

      const initialSwitchStates: Record<string, boolean> = {};
      piArray.forEach((pi) => {
        initialSwitchStates[pi.username] = pi.connectionStatus; // Set initial value based on connection status
      });
      setSwitchStates(initialSwitchStates);

    } catch (error) {
      console.error("Failed to fetch Pi statuses", error);
    }
  };

  useEffect(() => {
    fetchPiStatuses(false);
    const intervalId =  setInterval(() => {
      fetchPiStatuses(isAlreadyFetching); // Fetch every 5 seconds
    }, 5000); 
  
    return () => {
      clearInterval(intervalId); // Cleanup on unmount
    };
  }, []); // Dependency array ensures it runs only once
  

  // Will get periodically rendered by React when getPiStatuses updated piStatuses
  const piDivs = piStatuses.length === 0 ? (
    <div className="text-center">Please configure a raspberry pi below</div>
  ) : (
      piStatuses.map((pi, index) => (
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
            checked={switchStates[pi.username]}
            onCheckedChange={(checked) => {
              update_ssh(checked, pi);
            }}
          />
          <p className="min-w-[100px] text-center">
            {!pi.connectionStatus && switchStates[pi.username] ? "Connecting..." : pi.connectionStatus ? "Connected" : "Disconnected"}
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
  )));

  const update_ssh = async (checked: boolean, pi: ClientSidePiStatus) => {

    setSwitchStates((prevStates) => {
      const newStates = { ...prevStates };
      newStates[pi.username] = checked;
      return newStates;
    });

    setAlreadyFetching(true);
    try {
        let response;
        if (checked) {
            response = await fetch(`${BACKEND_URL}/connect_over_ssh/${pi.username}`, {
                method: "POST",
                body: JSON.stringify({ enabled: true }),
                headers: { "Content-Type": "application/json" }
            });

        } else {
            response = await fetch(`${BACKEND_URL}/disconnect_from_ssh/${pi.username}`, {
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
          const newStates = { ...prevStates };
          newStates[pi.username] = sshStatus; 
          return newStates;
        });

    } catch (error) {
        console.error("Error updating SSH connection:", error);
    } finally {
      setAlreadyFetching(false);
    }
};

// Handle deletion of a Pi
const handleDelete = async (username: string, index: number) => {

  const isConfirmed = window.confirm(`Are you sure you want to delete the "${username}" configuration?`);
  if (isConfirmed) {
    try {
      setAlreadyFetching(true);
      const response = await fetch(`${BACKEND_URL}/remove_pi_${username}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
      });
  
      // response.ok just checks that it gets a response
      if (response.ok) {
        console.log("Pi successfully deleted from config file");
        
        // If i = index of deleted pi, it is excluded from the filtered arrays...
        setPiStatuses((prevPiStatuses) => prevPiStatuses.filter((_, i) => i !== index));
        setSwitchStates((prevStates) => {
          const newStates = { ...prevStates };
          delete newStates[username]; // Remove from switchStates
          return newStates;
        });

      } else {
        console.error("Failed to delete the configured pi");
      }
    } catch (error) {
      console.error("Error:", error);
    } finally {
      setAlreadyFetching(false);
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
    setAlreadyFetching(true);
    const response = await fetch(`${BACKEND_URL}/add_pi`, {
      method: "POST",
      body: JSON.stringify(formData), // This is data sent to the backend
      headers: { "Content-Type": "application/json" },
    });

    // response.ok just checks that it gets a response
    if (response.ok) {
      console.log("Pi configured successfully");
      // Reset the form
      setUsername("");
      setIPAddress("");
      setPassword("");
      setCameraModel("");
    } else {
      console.error("Failed to configure Pi");
    }
  } catch (error) {
    console.error("Error submitting form:", error);
  } finally {
    setAlreadyFetching(false);
    fetchPiStatuses(false);
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