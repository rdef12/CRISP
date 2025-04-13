import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import {
  List,
  Datagrid,
  TextField,
  NumberField,
  DateField,
  SelectInput,
  Identifier,
  RaRecord,
  ShowBase,
  useRecordContext,
  SimpleForm,
  SimpleShowLayout,
  NumberInput,
  TextInput,
  DateInput,
  useEditController,
  useListController,
  useShowController,
  BooleanInput,
  Form,
  useGetList,
  useCreateController,
  useDelete,
  useRefresh,
  required,
} from 'react-admin';
import { Link, useParams } from 'react-router-dom';
import HomograpyCalibration from './OldHomographyCalibration';
// import ManualROI from './scintillator_edges/ScintillatorEdges';
import { DialogContent, DialogHeader } from '@/components/ui/dialog';
import { Dialog, DialogDescription, DialogTitle, DialogTrigger } from '@radix-ui/react-dialog';
import { CalibrationRouting } from './CalibrationRouting';
import { FieldValues } from 'react-hook-form';
import React from 'react';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";


export const AddSetupCameraDropDown = ({ onSuccess }: { onSuccess: () => void }) => {
  const { setupId } = useParams();
  console.log("Setup id")
  console.log(setupId)
  const { data, isPending: pendingUnaddedCameras, refetch } = useGetList( `setup/unadded-cameras/${setupId}`)
  const { save, isPending } = useCreateController({ resource: `setup/${setupId}`, redirect: false })
  console.log("FASCINATING DATAAAA", data)
  if (pendingUnaddedCameras) return null;

  const handleSubmit = async (formData: FieldValues) => {
    if (!save) return;
    await save(formData);
    refetch();
    onSuccess();
  };

  return (
    <Form onSubmit={handleSubmit}>
      <SelectInput source="camera_id" optionText="username" choices={data} validate={required()} />
      <Button> Add camera </Button>
    </Form>
  );
}

const DeleteButton = ({ record }: { record: RaRecord }) => {
  const [deleteOne] = useDelete();
  const refresh = useRefresh();

  const handleDelete = async (e: React.MouseEvent) => {
    e.stopPropagation(); // Stop the event from bubbling up to the row
    await deleteOne(
      'setup-camera',
      { id: record.id },
      {
        onSuccess: () => {
          refresh();
        },
      }
    );
  };

  return (
    <AlertDialog>
      <AlertDialogTrigger asChild>
        <Button 
          variant="destructive" 
          className="h-8 px-2"
          onClick={(e) => e.stopPropagation()}
        >
          Delete
        </Button>
      </AlertDialogTrigger>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>Are you sure?</AlertDialogTitle>
          <AlertDialogDescription>
            This will remove the camera from the setup. This action cannot be undone.
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel onClick={(e) => e.stopPropagation()}>Cancel</AlertDialogCancel>
          <AlertDialogAction onClick={handleDelete}>Delete</AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
};

const DeleteButtonField = () => {
  const record = useRecordContext();
  if (!record) return null;
  return <DeleteButton record={record} />;
};

export const SetupCameraList = () => {
  const { setupId } = useParams();
  const refresh = useRefresh();
  const { resource, data, isPending } = useListController({ 
    resource:`setup-camera/${setupId}`, 
    queryOptions: {meta: { camera: "camera"}}
  });
  
  const cameraSetupRowClick = (id: Identifier, resource: string, record: RaRecord) =>
    `/setup/${record.setup_id}/setup-camera/${record.id}`

  // Refresh when data changes
  React.useEffect(() => {
    if (data) {
      refresh();
    }
  }, [data, refresh]);

  console.log("DATAAA: ", data)
  if (isPending) return null;
  return (
    <List resource={resource}>
      <Datagrid data={data} rowClick={cameraSetupRowClick} bulkActionButtons={false} >
        <TextField source="camera.username" />
        <DeleteButtonField />
      </Datagrid>
    </List>
  );
};


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
  const { setupId } = useParams();
  const listController = useListController({ resource:`setup-camera/${setupId}`, queryOptions: {meta: { camera: "camera"}}});
  const { refetch: refetchDropdown } = useGetList(`setup/unadded-cameras/${setupId}`);

  const handleRefetch = () => {
    listController.refetch();
    refetchDropdown();
  };

  return (
    <div>
      <Card>
        <AddSetupCameraDropDown onSuccess={handleRefetch} />
      </Card>
      <BoxParameters />
      <SetupCameraList />
    </div>
  );
}

//BELOW SHOULD BE SOMEWHERE ELSE
export const NearFaceCalibrationButton = () => (
  <Link to="near-face">
    <Button>
      Near Face Calibration
    </Button>
  </Link>
)


export const FarFaceCalibrationButton = () => (
  <Link to="far-face">
    <Button>
      Far Face Calibration
    </Button>
  </Link>
)


export const DistortionCalibrationButton = () => (
  <Link to="distortion-calibration">
    <Button>
      Distortion Calibration
    </Button>
  </Link>
)

export const ScintillatorEdgeSelectionButton = () => (
  <Link to="scintillator-edges">
    <Button>
      Scintillator Edge Selection
    </Button>
  </Link>
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

const opticalAxes = [
  { id : 'x', name : "x" },
  { id : 'y', name : "y" },
  { id : 'z', name : "z" }, 
]

const imageBeamDirections = [
  { id : 'top', name : "Top" },
  { id : 'right', name : "Right" },
  { id : 'bottom', name : "Bottom" }, 
  { id : 'left', name : "Left" }, 
]

const depthDirections = [
  { id : 1, name : "Positive"},
  { id : -1, name : "Negative"}
]


export const EditSetupCamera = () => {
  const { setupCameraId } = useParams();
  const { record, save, isPending } = useEditController({ resource: "setup-camera/calibration", id: setupCameraId, redirect: false, mutationMode: "optimistic"})
  if (isPending) return null;
  console.log("RECORD.lens pos: ", record?.lens_position)
  return (
    <Card className="p-6">
      <div className="space-y-6">
        <div>
          <h2 className="text-lg font-semibold mb-4">Camera Setup Configuration</h2>
          <p className="text-sm text-muted-foreground mb-4">Configure the lens position and calibration settings for this camera setup.</p>
        </div>
        <Form record={record} onSubmit={save} className="space-y-4">
          <div className="space-y-2">
            <NumberInput source="lens_position"/>
          </div>
          <div className="space-y-2">
            <SelectInput source="optical_axis" validate={required()} choices={opticalAxes} />
          </div>
          <div className="space-y-2">
            <SelectInput source="depth_direction" validate={required()} choices={depthDirections} />
          </div>
          <div className="space-y-2">
            <SelectInput source="image_beam_direction" validate={required()} choices={imageBeamDirections} />            
          </div>
          <div className="space-y-2">
            <BooleanInput source="do_distortion_calibration" label="Enable Distortion Calibration" />
          </div>
          <div className="pt-4">
            <Button className="w-full sm:w-auto">Continue</Button>
          </div>
        </Form>
      </div>
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
  console.log("DO DIST CAL:", record?.do_distortion_calibration)
  console.log("Stuff", record?.do_distortion_calibration === null, record?.lens_position === null, record?.optical_axis === null, record?.depth_direction === null, record?.image_beam_direction === null)
  if (record?.do_distortion_calibration === null || record?.lens_position === null || record?.optical_axis === null || record?.depth_direction === null || record?.image_beam_direction === null)
    return (
    <EditSetupCamera/>
  )
  if (record?.do_distortion_calibration != null)
    return (
    <CalibrationRouting record={record} />
  )
  //   else return (<HomographyCalibration />)
    // else return (<CalibrationRoutingPage />)
}
