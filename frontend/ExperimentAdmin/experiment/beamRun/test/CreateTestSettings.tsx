import { useParams } from "react-router-dom";
import { NumberInput, RaRecord, SimpleForm, useCreateController } from "react-admin"

interface TestSettingsData {
  frame_rate: number;
  lowest_gain: number;
  highest_gain: number;
  gain_increment: number;
}

export const CreateTestSettings = ({ record }: { record: RaRecord}) => {
  const { beamRunId } = useParams();
  const { save, isPending } = useCreateController({ resource: `beam-run/test/${beamRunId}/camera/${record.id}`, redirect: false});
  
  if (isPending) return null;

  const handleSubmit = async (data: Partial<TestSettingsData>) => {
    if (save) {
      await save(data);
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