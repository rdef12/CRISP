import { useParams } from "react-router-dom";
import { Form, NumberInput, RaRecord, SimpleForm, useEditController } from "react-admin"
import { ListTestSettings } from './ListTestSettings'
import { ScrollArea } from "@/components/ui/scroll-area";
import { Button } from "@/components/ui/button";

// interface TestSettingsData {
//   frame_rate?: number;
//   lowest_gain?: number;
//   highest_gain?: number;
//   gain_increment?: number;
// }

interface EditTestSettingsProps {
  record: RaRecord;
  onSave?: () => void;
}

export const EditTestSettings = ({ record, onSave }: EditTestSettingsProps) => {
  const { beamRunId } = useParams();
  const { save, record: editRecord, isPending } = useEditController({ 
    resource: `beam-run/test/${beamRunId}/camera`,
    id: record.id, 
    redirect: false, 
    mutationMode: "optimistic",
  });

  if (isPending) return null;

  const handleSubmit = async (data: any) => {
    console.log('EditTestSettings: handleSubmit called');
    try {
      if (save) {
        console.log('EditTestSettings: save called');
        const response = await save(data);
        console.log('EditTestSettings: save completed with response:', response);
        onSave?.();
        console.log('EditTestSettings: onSave called');
      }
    } catch (error) {
      console.error('Error saving settings:', error);
    }
  };

  return(
    <Form record={editRecord} onSubmit={handleSubmit}>
      <NumberInput source="frame_rate" />
      <NumberInput source="lowest_gain" />
      <NumberInput source="highest_gain" />
      <NumberInput source="gain_increment" />
      {/* Other camera settings here */}
      <Button> Save </Button>
    </Form>
  )
} 