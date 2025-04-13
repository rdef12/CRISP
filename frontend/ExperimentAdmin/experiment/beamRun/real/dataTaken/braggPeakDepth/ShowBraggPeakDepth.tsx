import { useParams } from "react-router-dom";
import { NumberField, SimpleShowLayout, useShowController } from "react-admin"

export const ShowBraggPeakDepth = () => {
  const { beamRunId } = useParams(); 
  const { record, isPending, error } = useShowController({
    resource: `beam-run/bragg-peak`,
    id: beamRunId
  })
  if (isPending) return <div>Loading...</div>;
  return (
    <SimpleShowLayout record={record}>
      <NumberField source="bragg_peak_x"/>
      <NumberField source="bragg_peak_y"/>
      <NumberField source="bragg_peak_z"/>
      <NumberField source="bragg_peak_x_unc"/>
      <NumberField source="bragg_peak_y_unc"/>
      <NumberField source="bragg_peak_z_unc"/>
      <NumberField source="bragg_peak_depth"/>
      <NumberField source="bragg_peak_depth_unc"/>
    </SimpleShowLayout>
  )
}