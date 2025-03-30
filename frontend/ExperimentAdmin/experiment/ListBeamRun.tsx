import { BooleanField, Datagrid, DateField, Identifier, List, NumberField, Pagination, RaRecord, TextField } from "react-admin";
import { useParams } from "react-router-dom";

export const ListBeamRun = () => {
  const { experimentId } = useParams();
  const redirectOnRowClick = (id: Identifier, resource: string, record: RaRecord) => {
    console.log("IS TESTTTTT FOR TABLE: ", record.is_test)
    if (record.is_test) return (`/experiment/${record.experiment_id}/beam-run/test/${record.id}`);
    return (`/experiment/${record.experiment_id}/beam-run/real/${record.id}`)
}
  // const beamRunRowClick = (id: Identifier, resource: string, record: RaRecord) =>
  //   `/experiment/${record.experiment_id}/beam-run/${record.id}`
  return (
    <List resource={`beam-run/${experimentId}`}>
      <Datagrid rowClick={redirectOnRowClick}>
        <TextField source="beam_run_number"/>
        <NumberField source="ESS_beam_energy" label="ESS Beam Energy"/>
        <NumberField source="beam_current" />
        <DateField source="datetime_of_run" showTime={true} showDate={false}/>
        <BooleanField source="is_test"/>
      </Datagrid>
      <Pagination/>
    </List>
  )
}