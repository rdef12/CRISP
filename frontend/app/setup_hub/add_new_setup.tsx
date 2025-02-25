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
import { useRouter } from "next/router"


function PostSetupName({ setup_name }) {
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
        // Reset the form
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
}

function SubmitSetup({ setup_name }) {
  const router = useRouter()
  const handleClick = (e) => {
    e.preventDefault()
    router.push(setup_name)
  }
  return (
    <Button onClick={handleClick}>
      Submit new setup
    </Button>

  );
}


export function AddNewSetup() {
  const handleSubmitSetup = async () => {
    try{
      const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND}/get_setups`, {
        method: "POST",
        headers: {
          "Content-Type": "applic,ation/json"
        }
        body: JSON.stringify({ name, setup_name })
      })
    }
  } 
  return(
  <Dialog>
    <DialogTrigger asChild>
      <Button variant="outline">Add new setup</Button>
    </DialogTrigger>
    
    <DialogContent className="sm:max-w-[425px]">
      
      <DialogHeader>
        <DialogTitle>Add new setup</DialogTitle>
        <DialogDescription>
          Give your new setup a name here.
        </DialogDescription>
      </DialogHeader>
      
      <div className="grid gap-4 py-4">
        <Label htmlFor="name" className="text-right">
          Name
        </Label>
        <Input id="Setup name" placeholder="e.g. Christie 4 Camera Setup" className="col-span-3" />
      </div>
      
      <DialogFooter>
        <SubmitSetup setup_name={name}></SubmitSetup>
      </DialogFooter>
    
    </DialogContent>
  </Dialog>
  );
}