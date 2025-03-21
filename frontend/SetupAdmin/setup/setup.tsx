import {
  List,
  Create,
  Edit,
  Datagrid,
  TextField,
  DateField,
  Pagination,
  SimpleForm,
  TextInput,
  required,
  NumberInput,
  RaRecord,
  Identifier,
} from "react-admin"



export const SetupList = () => {
  // const setup = useRecordContext();
  const setupRowClick = (id: Identifier, resource: string, record: RaRecord) =>
    `/setup/${record?.id}`
  return (
    <List resource="setup">
      <h1>Setups </h1>
        <Datagrid rowClick={setupRowClick}>
          <TextField source="name" />
          <DateField source="date_created" showTime={true}/>
          <DateField source="date_last_edited" showTime={true}/>
        </Datagrid>
        <Pagination />
      </List>
  );
}

export const SetupCreate = () => (
  <Create>
    <SimpleForm>
      <TextInput source="setup_name" validate={required()} label="Setup name" />
    </SimpleForm>
  </Create>
);


// export const SetupShow = () => (
//   <Show>
//     <SimpleShowLayout>
//       <TextField source="name" />
//       <DateField source="date_created" />
//       <DateField source="date_last_edited" />

//       <NumberField source="block_x_dimension" label="X Dimension" />
//       <NumberField source="block_x_dimension_unc" label="X Dimension Uncertainty" />

//       <NumberField source="block_y_dimension" label="Y Dimension" />
//       <NumberField source="block_y_dimension_unc" label="Y Dimension Uncertainty" />

//       <NumberField source="block_z_dimension" label="Z Dimension" />
//       <NumberField source="block_z_dimension_unc" label="Z Dimension Uncertainty" />

//       <NumberField source="block_refractive_index" label="Refractive Index" />
//       <NumberField source="block_refractive_index_unc" label="Refractive Index Uncertainty" />
//     </SimpleShowLayout>
//     <SetupCameraList />
//   </Show>
// );

export const SetupEdit = () => (
  <Edit>
    <SimpleForm>
      <TextInput source="name" />
      <DateField source="date_created" />
      <DateField source="date_last_edited" />

      <NumberInput source="block_x_dimension" label="X Dimension" />
      <NumberInput source="block_x_dimension_unc" label="X Dimension Uncertainty" />

      <NumberInput source="block_y_dimension" label="Y Dimension" />
      <NumberInput source="block_y_dimension_unc" label="Y Dimension Uncertainty" />

      <NumberInput source="block_z_dimension" label="Z Dimension" />
      <NumberInput source="block_z_dimension_unc" label="Z Dimension Uncertainty" />

      <NumberInput source="block_refractive_index" label="Refractive Index" />
      <NumberInput source="block_refractive_index_unc" label="Refractive Index Uncertainty" />
    </SimpleForm>
  </Edit>
);

