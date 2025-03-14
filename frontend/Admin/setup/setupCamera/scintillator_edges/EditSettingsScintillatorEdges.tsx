import { Card } from '@/components/ui/card';
import { NumberInput, SimpleForm, useEditController } from 'react-admin';
import { useParams } from 'react-router-dom';

export const EditSettingsScintillatorEdges = () => {
  const { setupCameraId } = useParams();
  const { record, save , isPending} = useEditController({ resource:`settings/scintillator-edges`, id: setupCameraId, redirect: false})
  if (isPending) return null;
  return(
    <Card>
      <SimpleForm record={record} onSubmit={save}>
        <NumberInput source="gain"/>
        <NumberInput source="frame_rate"/>
        <NumberInput source="lens_position"/>
      </SimpleForm>
    </Card>
  )
}
