import { Card } from '@/components/ui/card';
import { NumberInput, SimpleForm, useEditController } from 'react-admin';
import { useParams } from 'react-router-dom';

export const EditSettingsScintillatorEdges = () => {
  const { setupCameraId } = useParams();
  const { record, save , isPending} = useEditController({ resource:`setup-camera/scintillator-edges`, id: setupCameraId, queryOptions: { meta: { settings: 'settings' } }, redirect: false})
  console.log("Record: ", record)
  if (isPending) return null;
  return(
    <Card>
      <SimpleForm record={record} onSubmit={save}>
        <NumberInput source="settings.gain"/>
        <NumberInput source="settings.frame_rate"/>
        <NumberInput source="settings.lens_position"/>
      </SimpleForm>
    </Card>
  )
}

