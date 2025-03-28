import { useParams } from "react-router-dom";
import { NumberInput, RaRecord, SimpleForm, useCreateController } from "react-admin"

interface TestSettingsData {
  frame_rate: number;
  lowest_gain: number;
  highest_gain: number;
  gain_increment: number;
}

interface CreateTestSettingsProps {
  record: RaRecord;
  onSave?: () => void;
}

export const CreateTestSettings = ({ record, onSave }: CreateTestSettingsProps) => {
  const { beamRunId } = useParams();
  const { save, isPending } = useCreateController({ 
    resource: `beam-run/test/${beamRunId}/camera/${record.id}`, 
    redirect: false
  });
  
  if (isPending) return null;

  const handleSubmit = async (data: Partial<TestSettingsData>) => {
    console.log('CreateTestSettings: handleSubmit called');
    try {
      if (save) {
        console.log('CreateTestSettings: save called');
        const response = await save(data);
        console.log('CreateTestSettings: save completed with response:', response);
        onSave?.();
        console.log('CreateTestSettings: onSave called');
      }
    } catch (error) {
      console.error('Error saving settings:', error);
    }
  };

  return(
    <SimpleForm record={record} onSubmit={handleSubmit}>
      <NumberInput source="frame_rate" required/>
      <NumberInput source="lowest_gain" required/>
      <NumberInput source="highest_gain" required/>
      <NumberInput source="gain_increment" required/>
      {/* Other camera settings here */}
    </SimpleForm>
  )
}