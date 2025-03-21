import { Create, ReferenceInput, required, SelectInput, SimpleForm, TextInput } from "react-admin";

export const ExperimentCreate = () => (
  <Create>
    <SimpleForm>
      <TextInput source="experiment_name" validate={required()} label="Experiment name" />
        <ReferenceInput source="setup_id" reference="setup" label="Setup Name">
            <SelectInput validate={required()}/>
        </ReferenceInput>
    </SimpleForm>
  </Create>
);