import { useParams } from "react-router-dom";
import { Form, useCreateController } from "react-admin"
import { Button } from "@/components/ui/button";
import { useState, useEffect } from "react";

interface SaveDistortionCalibrationImageButtonProps {
  imageUrl: string;
  onSuccess?: () => void;
}

export const SaveDistortionCalibrationImageButton = ({ imageUrl, onSuccess }: SaveDistortionCalibrationImageButtonProps) => {
  const { setupCameraId } = useParams();
  const { save, isPending } = useCreateController({ 
    resource: `photo/distortion-calibration/save/${setupCameraId}`, 
    redirect: false,
    transform: () => ({
      photo: imageUrl.split(',')[1] // Extract the base64 data without the data URL prefix
    })
  })
  
  if (!imageUrl || isPending) return null;
  
  const handleSubmit = async () => {
    try {
      if (!save) return;
      await save({});
      onSuccess?.();
    } catch (error) {
      console.error('Failed to save calibration image:', error);
    }
  };
  
  return (
    <Form onSubmit={handleSubmit}>
      <Button type="submit"> Add image to calibration </Button>
    </Form>
  )  
}