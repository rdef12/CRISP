"use client";

import { Switch } from "@/components/ui/switch";
import { useState, useEffect } from "react";
import { HoverCard, HoverCardContent, HoverCardTrigger } from "@/components/ui/hover-card";
import { ClientSidePiStatus, getPiStatuses } from "@/pi_functions/pi-status";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND;

export function PiStatusBar() {
  const [switchStates, setSwitchStates] = useState<Record<string, boolean>>({});
  const [piStatuses, setPiStatuses] = useState<ClientSidePiStatus[]>([]);
  const [isAlreadyFetching, setAlreadyFetching] = useState<boolean>(false);

  const fetchPiStatuses = async (isAlreadyFetching: boolean) => {
    try {
      const piArray = await getPiStatuses(isAlreadyFetching);
      setPiStatuses(piArray);

      const initialSwitchStates: Record<string, boolean> = {};
      piArray.forEach((pi) => {
        initialSwitchStates[pi.username] = pi.connectionStatus;
      });
      setSwitchStates(initialSwitchStates);
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
  }, []);

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
      const sshStatus = data.sshStatus;

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

  if (piStatuses.length === 0) {
    return null;
  }

  return (
    <div className="bg-gray-100 p-4 border-b">
      <div className="max-w-7xl mx-auto">
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
              <p className="text-sm min-w-[80px] text-center">
                {!pi.connectionStatus && switchStates[pi.username] ? "Connecting..." : pi.connectionStatus ? "Connected" : "Disconnected"}
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
} 