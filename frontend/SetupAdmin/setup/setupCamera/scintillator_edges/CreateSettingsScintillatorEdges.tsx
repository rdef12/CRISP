import { Card } from '@/components/ui/card';
import { NumberInput, SimpleForm, useCreateController } from 'react-admin';
import { useParams } from 'react-router-dom';

export const CreateSettingsScintillatorEdges = () => {
  const { setupCameraId } = useParams();
  const { record, save , isPending} = useCreateController({ resource:`settings/scintillator-edges/${setupCameraId}`, redirect: false })

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
