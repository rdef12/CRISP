"use client";

import { Switch } from "@/components/ui/switch";
import { useState, useEffect } from "react";
import { HoverCard, HoverCardContent, HoverCardTrigger } from "@/components/ui/hover-card";
import { ClientSidePiStatus, getPiStatuses } from "@/pi_functions/pi-status";
import { Badge } from "@/components/ui/badge";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND;

export function PiStatusBar() {
  const [switchStates, setSwitchStates] = useState<Record<string, boolean>>({});
  const [piStatuses, setPiStatuses] = useState<ClientSidePiStatus[]>([]);
  const [isAlreadyFetching, setAlreadyFetching] = useState<boolean>(false);

  const fetchPiStatuses = async (isAlreadyFetching: boolean) => {
    try {
      const piArray = await getPiStatuses(isAlreadyFetching);
      console.log("Fetched Pi statuses:", piArray);
      setPiStatuses(piArray);

      // Update switch states based on connection status
      const initialSwitchStates: Record<string, boolean> = {};
      piArray.forEach((pi) => {
        initialSwitchStates[pi.username] = pi.connectionStatus;
      });
      setSwitchStates(initialSwitchStates);
      console.log("Updated switch states:", initialSwitchStates);
    } catch (error) {
      console.error("Failed to fetch Pi statuses", error);
    }
  };

  useEffect(() => {
    fetchPiStatuses(false);
    const intervalId = setInterval(() => {
      fetchPiStatuses(isAlreadyFetching);
    }, 5000);

    return () => {
      clearInterval(intervalId);
    };
  }, [isAlreadyFetching]); // Add isAlreadyFetching to dependency array

  const update_ssh = async (checked: boolean, pi: ClientSidePiStatus) => {
    console.log(`Attempting to ${checked ? 'connect to' : 'disconnect from'} ${pi.username}`);
    
    // Optimistically update UI
    setSwitchStates((prevStates) => {
      const newStates = { ...prevStates };
      newStates[pi.username] = checked;
      return newStates;
    });

    setAlreadyFetching(true);
    try {
      const endpoint = checked ? 
        `${BACKEND_URL}/connect_over_ssh/${pi.username}` : 
        `${BACKEND_URL}/disconnect_from_ssh/${pi.username}`;

      console.log(`Making request to: ${endpoint}`);
      const response = await fetch(endpoint, {
        method: "POST",
        body: JSON.stringify({ enabled: checked }),
        headers: { "Content-Type": "application/json" }
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log("Response from server:", data);

      // Update both switch state and pi status based on response
      setSwitchStates((prevStates) => {
        const newStates = { ...prevStates };
        newStates[pi.username] = data.sshStatus;
        return newStates;
      });

      setPiStatuses((prevStatuses) => {
        return prevStatuses.map(status => {
          if (status.username === pi.username) {
            return {
              ...status,
              connectionStatus: data.sshStatus
            };
          }
          return status;
        });
      });

      // Trigger a fresh fetch after connection attempt
      setTimeout(() => {
        fetchPiStatuses(false);
      }, 1000);

    } catch (error) {
      console.error("Error updating SSH connection:", error);
      // Revert switch state on error
      setSwitchStates((prevStates) => {
        const newStates = { ...prevStates };
        newStates[pi.username] = !checked;
        return newStates;
      });
    } finally {
      setAlreadyFetching(false);
    }
  };

  if (piStatuses.length === 0) {
    return null;
  }

  const getStatusBadge = (pi: ClientSidePiStatus, isConnecting: boolean) => {
    console.log(`Status for ${pi.username}:`, {
      connectionStatus: pi.connectionStatus,
      switchState: switchStates[pi.username],
      isConnecting
    });

    if (!pi.connectionStatus && isConnecting) {
      return <Badge variant="outline" className="bg-orange-100 text-orange-700 hover:bg-orange-100 border-orange-200">Connecting...</Badge>;
    }
    if (pi.connectionStatus) {
      return <Badge variant="outline" className="bg-green-100 text-green-700 hover:bg-green-100 border-green-200">Connected</Badge>;
    }
    return <Badge variant="outline" className="bg-gray-100 text-gray-700 hover:bg-gray-100 border-gray-200">Disconnected</Badge>;
  };

  return (
    <div className="bg-gray-100 p-4 border-b">
      <div className="max-w-7xl mx-auto">
        <h3 className="text-sm font-semibold mb-2">Connected Pis:</h3>
        <div className="flex flex-wrap gap-4">
          {piStatuses.map((pi, index) => (
            <div key={index} className="flex items-center space-x-2 bg-white px-3 py-2 rounded-md shadow-sm">
              <HoverCard>
                <HoverCardTrigger>
                  <p className="text-sm text-green-500 hover:underline">{pi.username}</p>
                </HoverCardTrigger>
                <HoverCardContent>
                  IP Address - {pi.IPAddress}
                  <br />
                  Camera Model - {pi.cameraModel}
                </HoverCardContent>
              </HoverCard>
              <Switch
                checked={switchStates[pi.username]}
                onCheckedChange={(checked) => update_ssh(checked, pi)}
                className="scale-75"
              />
              {getStatusBadge(pi, !pi.connectionStatus && switchStates[pi.username])}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
} 