import { Datagrid, List, TextField, useShowController } from "react-admin";
import { useParams } from "react-router-dom";

export const ListCamerasInExperiment = () => {
  const { experimentId } = useParams();
  // const { data, isPending, resource } = useListController({ resource: `experiment/cameras/${experimentId}` });
  const { isPending, resource, record } = useShowController({ resource: `experiment`, id: experimentId, queryOptions: { meta: { setup: "setup", cameras: "cameras" }}})
  console.log("RESOURCE: ", resource)
  console.log("RECORD.cameras: ", record)
  // console.log("DATAAAAAAAAAAA", data)
  if (isPending) return null;
  return (
    <List resource={resource} >
      <Datagrid data={record.cameras} >
        <TextField source="username" />
        <TextField source="ip_address" />
      </Datagrid>
    </List>
  )
}