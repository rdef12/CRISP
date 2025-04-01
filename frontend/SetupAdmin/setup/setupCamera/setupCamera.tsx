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
  useListController,
  useShowController,
  BooleanInput,
} from 'react-admin';
import { Link, useParams } from 'react-router-dom';
import HomograpyCalibration from './HomographyCalibration';
// import ManualROI from './scintillator_edges/ScintillatorEdges';
import { DialogContent, DialogHeader } from '@/components/ui/dialog';
import { Dialog, DialogDescription, DialogTitle, DialogTrigger } from '@radix-ui/react-dialog';
import { CalibrationRouting } from './CalibrationRouting';


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
  const { resource, data, isPending } = useListController({ resource:`setup-camera/${setupId}`, queryOptions: {meta: { camera: "camera"}}})
  const cameraSetupRowClick = (id: Identifier, resource: string, record: RaRecord) =>
    `/setup/${record.setup_id}/setup-camera/${record.id}`
  console.log("DATAAA: ", data)
  if (isPending) return null;
  return (
    <List resource={resource}>
      <Datagrid data={data} rowClick={cameraSetupRowClick} bulkActionButtons={false} >
        {/* <TextField source="camera.id" /> */}
        <TextField source="camera.username" />
        {/* <TextField source="setup_id" /> */}
      </Datagrid>
    </List>
  );
};


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
    <Link to="distortion-calibration">Distortion Calibration</Link>
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
// export const DistortionTestContent = () => (
//   <DistortionPage />
// )

export const EditSetupCamera = () => {
  const { setupCameraId } = useParams();
  const { record, save, isPending } = useEditController({ resource: "setup-camera/calibration", id: setupCameraId, redirect: false })
  if (isPending) return null;
  console.log("RECORD.lens pos: ", record?.lens_position)
  return (
    <Card>
      <SimpleForm record={record} onSubmit={save}>
        <NumberInput source="lens_position" required />
        <BooleanInput source="do_distortion_calibration" />
      </SimpleForm>
    </Card>
  )
}


// export const SetupCameraShow = () => (
//   <div>
//     <FarFaceCalibrationButton/>
//     <NearFaceCalibrationButton/>
//     <DistortionCalibrationButton/>
//     <ScintillatorEdgeSelectionButton/>
//   </div>
// );

export const SetupCameraShow = () => {
  const { setupCameraId } = useParams();
  const {record, isPending} = useShowController({ resource: "setup-camera/calibration", id: setupCameraId });  
  if (isPending) return null;

  if (record?.do_distortion_calibration === null) return (<EditSetupCamera/>)
  if (record?.do_distortion_calibration) return (<CalibrationRouting record={record} />)
  //   else return (<HomographyCalibration />)
    // else return (<CalibrationRoutingPage />)
}
