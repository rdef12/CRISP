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
  TabbedShowLayout,
  ShowBase,
  useRecordContext,
  SimpleForm,
  CreateBase
} from 'react-admin';
import { Link, useParams } from 'react-router-dom';
import DistortionPage from './DistortionCalibration';
import HomograpyCalibration from './HomographyCalibration';
import ManualROI from './ScintillatorEdges';

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

export const BoxParametersContent = () => {
  const record = useRecordContext();
  if (!record) return null;
  return (
      <TabbedShowLayout>
      <TabbedShowLayout.Tab label="Main">
        <TextField source="name" />
        <DateField source="date_created" />
        <DateField source="date_last_edited" />
      </TabbedShowLayout.Tab>
      <TabbedShowLayout.Tab label="x dimensions">
        <NumberField source="block_x_dimension" />
        <NumberField source="block_x_dimension_unc" />
      </TabbedShowLayout.Tab>
      <TabbedShowLayout.Tab label="y dimensions">
        <NumberField source="block_y_dimension" />
        <NumberField source="block_y_dimension_unc" />
      </TabbedShowLayout.Tab>
      <TabbedShowLayout.Tab label="z dimensions">
        <NumberField source="block_z_dimension" />
        <NumberField source="block_z_dimension_unc" />
      </TabbedShowLayout.Tab>
      <TabbedShowLayout.Tab label="refractive index">
        <NumberField source="block_refractive_index" />
        <NumberField source="block_refractive_index_unc" />
      </TabbedShowLayout.Tab>
    </TabbedShowLayout>
  );
}

export const BoxParameters = () => {
  const  { setupId } = useParams();
  return (
    <ShowBase resource='setup' id={setupId}>
      <BoxParametersContent />
    </ShowBase>
  );
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
