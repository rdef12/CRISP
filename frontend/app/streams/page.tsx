"use client";

// import { useState, useEffect } from "react";
// import { Button } from "@/components/ui/button";
// import {
//   DropdownMenu,
//   DropdownMenuContent,
//   DropdownMenuItem,
//   DropdownMenuLabel,
//   DropdownMenuSeparator,
//   DropdownMenuTrigger,
// } from "@/components/ui/dropdown-menu";
// import { Input } from "@/components/ui/input";
// import { ClientSidePiStatus, getPiStatuses } from "@/pi_functions/pi-status";


const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND

export default function StreamTesting() {

    return (<div>
            <img src={`${BACKEND_URL}/stream_c09796mb`} alt="Video Stream" id="video-element"/>
          </div>
  );
}
