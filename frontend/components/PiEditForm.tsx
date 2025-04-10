"use client";

import { useState } from "react";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { ClientSidePiStatus } from "@/pi_functions/pi-status";

interface PiEditFormProps {
  pi: ClientSidePiStatus;
  // eslint-disable-next-line
  onSave: (updatedPi: ClientSidePiStatus) => void;
  onCancel: () => void;
}

export function PiEditForm({ pi, onSave, onCancel }: PiEditFormProps) {
  const [formData, setFormData] = useState({
    IPAddress: pi.IPAddress,
    cameraModel: pi.cameraModel,
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSave({
      ...pi,
      ...formData
    });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="space-y-2">
        <Label htmlFor="username">Username</Label>
        <Input
          id="username"
          value={pi.username}
          disabled
          className="bg-gray-100"
        />
      </div>
      <div className="space-y-2">
        <Label htmlFor="IPAddress">IP Address</Label>
        <Input
          id="IPAddress"
          name="IPAddress"
          value={formData.IPAddress}
          onChange={handleChange}
          placeholder="Enter IP address"
        />
      </div>
      <div className="space-y-2">
        <Label htmlFor="cameraModel">Camera Model</Label>
        <Input
          id="cameraModel"
          name="cameraModel"
          value={formData.cameraModel}
          onChange={handleChange}
          placeholder="Enter camera model"
        />
      </div>
      <div className="flex justify-end space-x-2">
        <Button type="button" variant="outline" onClick={onCancel}>
          Cancel
        </Button>
        <Button type="submit">
          Save Changes
        </Button>
      </div>
    </form>
  );
} 