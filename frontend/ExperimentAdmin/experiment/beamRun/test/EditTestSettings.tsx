import { useParams } from "react-router-dom";
import { NumberInput, RaRecord, SimpleForm, useEditController } from "react-admin"
import { ListTestSettings } from './ListTestSettings'

// interface TestSettingsData {
//   frame_rate?: number;
//   lowest_gain?: number;
//   highest_gain?: number;
//   gain_increment?: number;
// }

export const EditTestSettings = ({ record }: { record: RaRecord}) => {
  const { beamRunId } = useParams();
  const { save, record: editRecord, isPending } = useEditController({ 
    resource: `beam-run/test/${beamRunId}/camera`,
    id: record.id, 
    redirect: false 
  });
  if (isPending) return null;
  return(
    <SimpleForm record={editRecord} onSubmit={save}>
      <NumberInput source="frame_rate" />
      <NumberInput source="lowest_gain" />
      <NumberInput source="highest_gain" />
      <NumberInput source="gain_increment" />
      {/* Other camera settings here */}
    </SimpleForm>     
  )
} 