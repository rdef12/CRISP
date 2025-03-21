import { Datagrid, DateField, Identifier, List, Pagination, RaRecord, TextField } from "react-admin";

export const ExperimentList = () => {
  const setupRowClick = (id: Identifier, resource: string, record: RaRecord) =>
    `/experiment/${record?.id}`
  return (
    <List resource="experiment">
      <h1>Experiments </h1>
        <Datagrid rowClick={setupRowClick}>
          <TextField source="name" />
          <DateField source="date_created" />
          <DateField source="date_last_edited" />
        </Datagrid>
        <Pagination />
      </List>
  );
}
