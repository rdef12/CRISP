import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import {
  List,
  Datagrid,
  TextField,
  ReferenceInput,
  NumberField,
  DateField,
  SelectInput,
  Identifier,
  RaRecord,
  ShowBase,
  useRecordContext,
  SimpleForm,
  CreateBase,
  SimpleShowLayout,
  NumberInput,
  TextInput,
  DateInput,
  useEditController,
} from 'react-admin';
import { Link, useParams } from 'react-router-dom';
import DistortionPage from './DistortionCalibration';
import HomograpyCalibration from './HomographyCalibration';
import ManualROI from './scintillator_edges/ScintillatorEdges';
import { DialogContent, DialogHeader } from '@/components/ui/dialog';
import { Dialog, DialogDescription, DialogTitle, DialogTrigger } from '@radix-ui/react-dialog';


// export const SetupCameraList = () => {
//   const { id } = useParams();
//   const createPath = useCreatePath();
//   const setupCameraPath = createPath({ resource: 'camera-setup', type: 'show'});
//   return (
//       <List resource="camera-setup" filter={{ setup_id: id }}>
//           <Datagrid rowClick={ setupCameraPath }>
//               <TextField source="id" />
//               <TextField source="camera_id" />
//               <TextField source="setup_id" />
//           </Datagrid>
//       </List>
//   );
// };

export const AddSetupCameraDropDown = () => {
  const { setupId } = useParams();
  console.log("Setup id")
  console.log(setupId)
  return (
    <CreateBase resource={`setup/${setupId}`}>
      <SimpleForm>
        <ReferenceInput source="camera_id" reference="camera" label="Camera Id">
            <SelectInput />
        </ReferenceInput>
      </SimpleForm>
    </CreateBase>
  );
}

export const SetupCameraList = () => {
  const { setupId } = useParams();
  const cameraSetupRowClick = (id: Identifier, resource: string, record: RaRecord) =>
    `/setup/${record.setup_id}/setup-camera/${record.id}`
  return (
    <List resource="setup-camera" 
    filter={{ setup_id: setupId }}
    >
      <Datagrid rowClick={cameraSetupRowClick} >
        <TextField source="id" />
        <TextField source="camera_id" />
        <TextField source="setup_id" />
      </Datagrid>
    </List>
  );
};

// export const BoxParametersContent = () => {
//   const record = useRecordContext();
//   if (!record) return null;
//   return (
//       <TabbedShowLayout>
//       <TabbedShowLayout.Tab label="Main">
//         <TextField source="name" />
//         <DateField source="date_created" />
//         <DateField source="date_last_edited" />
//       </TabbedShowLayout.Tab>
//       <TabbedShowLayout.Tab label="x dimensions">
//         <NumberField source="block_x_dimension" />
//         <NumberField source="block_x_dimension_unc" />
//       </TabbedShowLayout.Tab>
//       <TabbedShowLayout.Tab label="y dimensions">
//         <NumberField source="block_y_dimension" />
//         <NumberField source="block_y_dimension_unc" />
//       </TabbedShowLayout.Tab>
//       <TabbedShowLayout.Tab label="z dimensions">
//         <NumberField source="block_z_dimension" />
//         <NumberField source="block_z_dimension_unc" />
//       </TabbedShowLayout.Tab>
//       <TabbedShowLayout.Tab label="refractive index">
//         <NumberField source="block_refractive_index" />
//         <NumberField source="block_refractive_index_unc" />
//       </TabbedShowLayout.Tab>
//     </TabbedShowLayout>
//   );
// }


export const BoxParametersContent = () => {
  const record = useRecordContext();
  if (!record) return null;
  return (
      <SimpleShowLayout >
        <TextField source="name" />
        <DateField source="date_created" />
        <DateField source="date_last_edited" />
        <NumberField source="block_x_dimension" />
        <NumberField source="block_x_dimension_unc" />
        <NumberField source="block_y_dimension" />
        <NumberField source="block_y_dimension_unc" />
        <NumberField source="block_z_dimension" />
        <NumberField source="block_z_dimension_unc" />
        <NumberField source="block_refractive_index" />
        <NumberField source="block_refractive_index_unc" />
      </SimpleShowLayout>
  );
}



// export const BoxParameters = () => {
//   const  { setupId } = useParams();
//   return (
//     <ShowBase resource='setup' id={setupId}>
//       <BoxParametersContent />
//       <EditButton/>
//     </ShowBase>
//   );
// }


// export const BoxParameters = () => {
//   const { setupId } = useParams();
//   const [isEditing, setIsEditing] = useState(false);
//   // const redirect = useRedirect();
//   // const record = useRecordContext();  // Get the current record

//   // if (!record) return null;  // Prevent rendering if no data is available

//   return (<div>
//           {isEditing ? (
//             <EditBase resource="setup" id={setupId}>
//               <SimpleForm sanitizeEmptyValues>
//                   <TextInput source="name" />
//                   <DateInput source="date_created" disabled />
//                   <DateInput source="date_last_edited" disabled />
//                   <NumberInput source="block_x_dimension" />
//                   <NumberInput source="block_x_dimension_unc" />
//                   <NumberInput source="block_y_dimension" />
//                   <NumberInput source="block_y_dimension_unc" />
//                   <NumberInput source="block_z_dimension" />
//                   <NumberInput source="block_z_dimension_unc" />
//                   <NumberInput source="block_refractive_index" />
//                   <NumberInput source="block_refractive_index_unc" />
                  
//                   {/* Save and Cancel buttons */}
//                   <SaveButton />
//                   <Button onClick={() => setIsEditing(false)} color="secondary">
//                       <>Cancel</>
//                   </Button>
//               </SimpleForm>
//             </EditBase>
//           ) : (
//       <ShowBase resource="setup" id={setupId}>
//               <SimpleShowLayout>
//                   <TextField source="name" />
//                   <DateField source="date_created" />
//                   <DateField source="date_last_edited" />
//                   <NumberField source="block_x_dimension" />
//                   <NumberField source="block_x_dimension_unc" />
//                   <NumberField source="block_y_dimension" />
//                   <NumberField source="block_y_dimension_unc" />
//                   <NumberField source="block_z_dimension" />
//                   <NumberField source="block_z_dimension_unc" />
//                   <NumberField source="block_refractive_index" />
//                   <NumberField source="block_refractive_index_unc" />

//                   {/* Edit button switches to form mode */}
//                   <Button onClick={() => setIsEditing(true)} color="primary" variant="contained">
//                       <>Edit</>
//                   </Button>
//               </SimpleShowLayout>
//         </ShowBase>
//           )
//     }
//       </div>

//   );
// };

export const EditBoxParameters = () => {
  const { setupId } = useParams();
  console.log("Setup id from useParams: ", setupId)
  console.log(typeof setupId, setupId); // Check the type and value

  const {  record, save, isPending } = useEditController({ resource: "setup", id: setupId });
  if (isPending) return null;
  return (
    <DialogContent>
      <DialogHeader>
        <DialogTitle>Box parameters</DialogTitle>
        <DialogDescription> Edit the specific parameters of your box setup here. </DialogDescription>
      </DialogHeader>
      <SimpleForm record={record} onSubmit={save}>
        <TextInput source="name" />
        <DateInput source="date_created" disabled />
        <DateInput source="date_last_edited" disabled />
        <NumberInput source="block_x_dimension" />
        <NumberInput source="block_x_dimension_unc" />
        <NumberInput source="block_y_dimension" />
        <NumberInput source="block_y_dimension_unc" />
        <NumberInput source="block_z_dimension" />
        <NumberInput source="block_z_dimension_unc" />
        <NumberInput source="block_refractive_index" />
        <NumberInput source="block_refractive_index_unc" />
      </SimpleForm>
    </DialogContent>
  )
}

export const EditBoxParametersButton = () => {
  return (
  <Dialog>
    <DialogTrigger asChild>
      <Button variant="outline">Edit</Button>
    </DialogTrigger>
    <EditBoxParameters />
  </Dialog>
  )
}

export const BoxParameters = () => {
  const { setupId } = useParams()
    return (  
      <ShowBase resource="setup" id={setupId}>
              <SimpleShowLayout>
                  <TextField source="name" />
                  <DateField source="date_created" />
                  <DateField source="date_last_edited" />
                  <NumberField source="block_x_dimension" />
                  <NumberField source="block_x_dimension_unc" />
                  <NumberField source="block_y_dimension" />
                  <NumberField source="block_y_dimension_unc" />
                  <NumberField source="block_z_dimension" />
                  <NumberField source="block_z_dimension_unc" />
                  <NumberField source="block_refractive_index" />
                  <NumberField source="block_refractive_index_unc" />
              </SimpleShowLayout>
              <EditBoxParametersButton />
        </ShowBase>
    )
}

export const SetupShow = () => {
  return (
    <div>
      <Card>
        <AddSetupCameraDropDown />
      </Card>
      <BoxParameters />
      <SetupCameraList />
    </div>
  );
}

// export const SetupCameraCreate = () => {
//   const { id, cameraId } = useParams();
//   return(
//     <Create resource="camera-setup" id={cameraId} redirect={'/setup/${id}/cameras/${cameraId}'}>
//       <SimpleForm defaultValues={{ setup_id: id }}>
//         <ReferenceInput label="Cameras" source="camera_id" reference='camera'> {/* source is db field name, reference is that defined in admin */}
//         </ReferenceInput>
//       </SimpleForm>
//     </Create>
//   )
// };

// export const SetupCameraCreate = () => {
//   const { id } = useParams();
//   return (
//     <Create 
//       resource="setup-camera" 
//       redirect={`/setup/${id}/cameras`}
//     >
//       <SimpleForm defaultValues={{ setup_id: id }}>
//         <ReferenceInput label="Cameras" source="camera_id" reference="camera">
//           <SelectInput optionText="name" />
//         </ReferenceInput>
//       </SimpleForm>
//     </Create>
//   );
// };



//BELOW SHOULD BE SOMEWHERE ELSE
export const NearFaceCalibrationButton = () => (
  <Button>
    <Link to="near-face">Near Face Calibration</Link>
  </Button>
)

export const FarFaceCalibrationButton = () => (
  <Button>
    <Link to="far-face">Far Face Calibration</Link>
  </Button>
)

export const DistortionCalibrationButton = () => (
  <Button>
    <Link to="distortion">Distortion Calibration</Link>
  </Button>
)

export const ScintillatorEdgeSelectionButton = () => (
  <Button>
    <Link to="scintillator-edges">Scintillator Edge Selection</Link>
  </Button>
)

export const NearFaceTestContent = () => (
  <HomograpyCalibration plane={"near"} />
)

export const FarFaceTestContent = () => (
  <HomograpyCalibration plane={"far"} />
)
export const DistortionTestContent = () => (
  <DistortionPage />
)
export const ScintillatorEdgesTestContent = () => (
  <ManualROI />
)

export const SetupCameraShow = () => (
  <div>
    <FarFaceCalibrationButton/>
    <NearFaceCalibrationButton/>
    <DistortionCalibrationButton/>
    <ScintillatorEdgeSelectionButton/>
  </div>
);
