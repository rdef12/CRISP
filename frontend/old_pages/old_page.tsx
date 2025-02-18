"use client";

import { Switch } from "@/components/ui/switch"
import { Button } from "@/components/ui/button"
import { useState, useEffect } from "react";
import { Input } from "@/components/ui/input"; 

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND
console.log("TEST")

export default function Home() {
  const [message, setMessage] = useState("");
  async function takePictureOnClick() {
    console.log("Attempting to fetch picture from API using URL: ", BACKEND_URL); // Clear context for the log
    try {
      const response = await fetch(`${BACKEND_URL}/take_picture`);
      const data = await response.json();
      setMessage(data.message);
    } catch (error) {
      console.error("Error fetching data:", error);
      setMessage("Something went wrong!");
    }
  };

  // Defined here so it updates after a page reset? We probably want these states to be remembered even after a page refresh.
  // Also, they are specific to this component
  const[loading, setLoading] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const[isConnected, setIsConnected] = useState(false);
  const[wasConnectionError, setWasConnectionError] = useState(false);
  const[switchIsOn, setSwitchIsOn] = useState(false);
  const [mounted, setMounted] = useState(false); // Added for ensuring client-side rendering

  useEffect(() => {
    setMounted(true); // This ensures we're only using client-side logic after the component is mounted
  }, []);

  // Arrow function here
  const connectToRaspi5 = async (checked: boolean) => {
    setSwitchIsOn(checked); // Redefined to the connection status of raspi5
    setLoading(true);
    console.log(loading);

    try {
      if (checked) {
        // Action when switched ON
        setIsConnecting(true)
        console.log("Switch turned ON");
        const response = await fetch(`${BACKEND_URL}/connect_to_raspi5`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ enabled: true }),
        });
        console.log("Response", response)
        const data = await response.json(); // response from FastAPI handler read in as a JSON
        console.log("Is connected: ", data.connectionStatus) // Keys in the JSON can be used to access specific responses

        setIsConnecting(false)
        setIsConnected(data.connectionStatus);
        setWasConnectionError(!data.connectionStatus)
        console.log("Is Raspi5 connected? ", isConnected)

      } else {
        // Action when switched OFF
        if (wasConnectionError)
          console.log("Switch turned OFF");
          setWasConnectionError(false)

        if (isConnected) {
          console.log("Switch turned OFF");
          const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND}/disconnect_from_raspi5`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ enabled: false }),
          });
          console.log("Response", response)
          const data = await response.json(); // response from FastAPI handler read in as a JSON
          console.log("Is connected: ", data.connectionStatus) // Keys in the JSON can be used to access specific responses
          setIsConnected(data.connectionStatus);
          console.log("Is Raspi5 connected? ", isConnected)
        }
      }
    }
     catch (error) {
      console.error("Error updating setting:", error);
      setSwitchIsOn(!checked); // Revert switch if request fails
    } finally {
      setLoading(false);
    }
  };

  if (!mounted) {
    return null; // Prevent server-side render mismatch by waiting for client-side render
  }

  return (

    <section>
      <div>
        <Button onClick={takePictureOnClick}>Click me</Button>
        {message && <p className="mt-4">{message}</p>}
      </div>

      <div>
      <Switch checked={switchIsOn} onCheckedChange={connectToRaspi5} id="Raspberry Pi 5" />
        <span style={{ paddingLeft: '25px' }}>
            {isConnecting ? "CONNECTING" : wasConnectionError ? "CONNECTION ERROR" : isConnected ? "ON" : "OFF"}
        </span>
      </div>

      <form className="space-y-4">
        <Input placeholder="Username" />
        <Input placeholder="Hostname" />
        <Input placeholder="Password" type="password" />
        <Input placeholder="Camera Model (lol)" />
      </form>

    </section>
    );
}