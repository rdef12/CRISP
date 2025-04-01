import { useParams } from "react-router-dom";
import { Form, NumberField, NumberInput, RaRecord, SimpleShowLayout, useEditController } from "react-admin";
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

interface EditRealSettingsProps {
  record: RaRecord;
  onSave?: () => void;
  onEditStateChange?: () => void;
}

interface CameraSettings {
  gain: number;
  frame_rate: number;
}

export const EditRealSettings = ({ record, onSave, onEditStateChange }: EditRealSettingsProps) => {
  const { beamRunId } = useParams();
  const [isEditing, setIsEditing] = useState(false);
  const [showConfirmDialog, setShowConfirmDialog] = useState(false);
  const [formData, setFormData] = useState<CameraSettings | null>(null);
  const { save, record: editRecord } = useEditController({
    resource: `beam-run/real/${beamRunId}/camera`,
    id: record.id,
    redirect: false
  });

  const handleEditStateChange = (newState: boolean) => {
    setIsEditing(newState);
    onEditStateChange?.();
  };

  const handleSubmit = async (data: Record<string, unknown>) => {
    console.log('EditTestSettings: handleSubmit called');
    const settings: CameraSettings = {
      gain: Number(data.gain),
      frame_rate: Number(data.frame_rate)
    };
    setFormData(settings);
    setShowConfirmDialog(true);
  };

  const handleConfirmSave = async () => {
    if (!formData) return;
    
    try {
      if (save) {
        console.log('EditTestSettings: save called');
        const response = await save(formData);
        console.log('EditTestSettings: save completed with response:', response);
        onSave?.();
        console.log('EditTestSettings: onSave called');
        handleEditStateChange(false);
        setShowConfirmDialog(false);
      }
    } catch (error) {
      console.error('Error saving settings:', error);
    }
  };

  return (
    <div className="space-y-4">
      {!isEditing ? (
        <>
          <SimpleShowLayout record={editRecord}>
            <NumberField source="lens_position" />
            <NumberField source="gain" />
            <NumberField source="frame_rate" />
          </SimpleShowLayout>
          <div className="flex justify-end">
            <Button 
              onClick={() => handleEditStateChange(true)} 
              variant="default"
            >
              Edit Settings
            </Button>
          </div>
        </>
      ) : (
        <Form record={editRecord} onSubmit={handleSubmit}>
          <div className="space-y-4">
            <NumberInput source="gain" />
            <NumberInput source="frame_rate" />
            <div className="flex justify-end gap-2">
              <Button 
                type="button"
                variant="outline"
                onClick={() => handleEditStateChange(false)}
              >
                Cancel
              </Button>
              <Button type="submit">Save Changes</Button>
            </div>
          </div>
        </Form>
      )}

      <AlertDialog open={showConfirmDialog} onOpenChange={setShowConfirmDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle> WARNING - Settings not Tested!! </AlertDialogTitle>
            <AlertDialogDescription>
              These settings may be untested and could result in poor data quality. <br/>
              RECOMMENDED: Choose new optimal settings in a tested beam run.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel onClick={() => setShowConfirmDialog(false)}>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={handleConfirmSave}>Save</AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}