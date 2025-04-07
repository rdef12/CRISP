import { useParams } from "react-router-dom";
import { BooleanField, BooleanInput, Form, NumberField, NumberInput, RaRecord, required, SimpleShowLayout, useCreateController, useEditController } from "react-admin";
import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";

interface NumberOfImagesAndRaw {
  number_of_images: number;
  take_raw_images: boolean;
}

interface EditNumberOfImagesAndRawProps {
  record: RaRecord;
  onSave?: () => void;
  onEditStateChange?: () => void;
  refreshTrigger?: boolean;
}

export const EditNumberOfImagesAndRaw = ({ record, onSave, onEditStateChange, refreshTrigger }: EditNumberOfImagesAndRawProps) => {
  const { beamRunId } = useParams();
  const [isEditing, setIsEditing] = useState(false);
  const { save, record: editRecord } = useEditController({
    resource: `beam-run/real/${beamRunId}/number-of-images/camera`,
    id: record.id,
    redirect: false,
    mutationMode: "optimistic",
    meta: { refresh: refreshTrigger }
  });

  useEffect(() => {
    // If values are null, go straight to edit mode
    if (editRecord && (editRecord.number_of_images === null || editRecord.take_raw_images === null)) {
      setIsEditing(true);
    }
  }, [editRecord]);

  const handleEditStateChange = (newState: boolean) => {
    setIsEditing(newState);
    onEditStateChange?.();
  };

  const handleSubmit = async (data: Record<string, unknown>) => {
    try {
      const settings: NumberOfImagesAndRaw = {
        number_of_images: Number(data.number_of_images),
        take_raw_images: Boolean(data.take_raw_images)
      };

      if (save) {
        await save(settings);
        onSave?.();
        handleEditStateChange(false);
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
            <NumberField source="number_of_images" />
            <BooleanField source="take_raw_images" />
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
            <NumberInput source="number_of_images" />
            <BooleanInput source="take_raw_images" />
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
    </div>
  );
}