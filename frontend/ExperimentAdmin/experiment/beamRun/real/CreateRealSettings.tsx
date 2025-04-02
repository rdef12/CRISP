import { useParams } from "react-router-dom";
import { Form, NumberInput, RaRecord, useCreateController } from "react-admin";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";

interface CameraSettings {
  gain: number;
  frame_rate: number;
  number_of_images: number;
}

interface CreateRealSettingsProps {
  record: RaRecord;
  onSave?: () => void;
}

export const CreateRealSettings = ({ record, onSave }: CreateRealSettingsProps) => {
  const { beamRunId } = useParams();
  const [showConfirmDialog, setShowConfirmDialog] = useState(false);
  const [formData, setFormData] = useState<CameraSettings | null>(null);
  const { save } = useCreateController({
    resource: `beam-run/real/${beamRunId}/camera/${record.id}`,
    redirect: false
  });

  const handleSubmit = async (data: Record<string, unknown>) => {
    console.log('CreateRealSettings: handleSubmit called');
    const settings: CameraSettings = {
      gain: Number(data.gain),
      frame_rate: Number(data.frame_rate),
      number_of_images: Number(data.number_of_images)
    };
    setFormData(settings);
    setShowConfirmDialog(true);
  };

  const handleConfirmSave = async () => {
    if (!formData) return;
    
    try {
      if (save) {
        console.log('CreateRealSettings: save called');
        const response = await save(formData);
        console.log('CreateRealSettings: save completed with response:', response);
        setShowConfirmDialog(false);
        onSave?.();
        console.log('CreateRealSettings: onSave called');
      }
    } catch (error) {
      console.error('Error saving settings:', error);
    }
  };

  return (
    <div className="space-y-4">
      <Form onSubmit={handleSubmit}>
        <div className="space-y-4">
          <NumberInput source="gain" />
          <NumberInput source="frame_rate" />
          <NumberInput source="number_of_images" />
          <div className="flex justify-end">
            <Button type="submit">Create Settings</Button>
          </div>
        </div>
      </Form>

      <AlertDialog open={showConfirmDialog} onOpenChange={setShowConfirmDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle> WARNING - Settings not Tested!! </AlertDialogTitle>
            <AlertDialogDescription>
              These settings may be untested and could result in poor data quality. <br/>
              RECOMMENDED: Perform a test run with these beam parameters.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel onClick={() => setShowConfirmDialog(false)}>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={handleConfirmSave}>Create</AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}