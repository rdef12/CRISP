"use client"

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  DialogFooter,
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import { Input } from "@/components/ui/input"
import { useState } from "react"
// import { useRouter } from "next/router"




export default function AddNewSetup() {
  const [name, setName] = useState("");

  const handleSubmit = async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND}/add_setup`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ setup_name: name }),
      });

      if (!response.ok) {
        throw new Error("Failed to submit");
      }

      console.log("Setup added successfully");
    } catch (error) {
      console.error("Error:", error);
    }
  };
  return (

    <Dialog>
      <DialogTrigger asChild>
        <Button variant="outline">Add new setup</Button>
      </DialogTrigger>
      
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Add new setup</DialogTitle>
          <DialogDescription>
            Give your setup a name. Click submit when you are done.
          </DialogDescription>
        </DialogHeader>
      
        <div className="grid gap-4 py-4">
          <div className="grid grid-cols-4 items-center gap-4">
            <Label htmlFor="name" className="text-right">
              Name
            </Label>
            <Input
              id="name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. Christie PVT 4 camera box"
              className="col-span-3"
            />
          </div>
        </div>
      
        <DialogFooter>
          <Button onClick={handleSubmit}>Submit</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}