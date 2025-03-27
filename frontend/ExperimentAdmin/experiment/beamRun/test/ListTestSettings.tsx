import { useParams } from "react-router-dom";
import { Datagrid, List, NumberField, useRecordContext } from "react-admin";

export const ListTestSettings = () => {
  const { beamRunId } = useParams();
  const record = useRecordContext();
  // const { isPending } = useListController({ resource: `beam-run/test/${beamRunId}/camera/${record.id}` });
  
  // if (isPending) return null;

  // const handleSubmit = async (data: Partial<TestSettingsData>) => {
  //   if (save) {
  //     await save(data);
  //   }
  // };
  if (!record) return null;
  return(
    <List resource={`settings/beam-run/test/${beamRunId}/camera/${record.id}`}>
      <Datagrid bulkActionButtons={false}>
        <NumberField source="gain" />
        <NumberField source="frame_rate" />
        <NumberField source="lens_position" />
        {/* Other camera settings here */}
      </Datagrid>
    </List>
  )
}