import { useParams } from "react-router-dom"
import { DateField, SimpleShowLayout, TextField, useShowController } from "react-admin"

export const ShowSetupSummary = () => {
  const { experimentId } = useParams()
  const { isPending, record } = useShowController({ resource: "experiment", id: experimentId, queryOptions: { meta: { setup: 'setup' }} })
  if (isPending) return null;
  return (
    <div>
      <h1>Setup summary</h1>
      <SimpleShowLayout record={record}>
        <TextField source="setup.name"/>
        <DateField source="setup.date_created" />
      </SimpleShowLayout>
    </div>
  )
}