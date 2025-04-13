// import { Button } from "@/components/ui/button";
// import { CheckboxGroupInput, Form, SelectInput, useCreate, useGetList } from "react-admin";
// import { useParams } from "react-router-dom";

// const ComplexAnalysisChoices = [
//   {id: 'range', name: 'Range'},
//   {id: 'something_else', name: 'Something Else'}
// ]


export const ComplexAnalysis = () => {
  // const { beamRunId } = useParams();
  // const {
  //   data: topCameras,
  //   isPending: isPendingTopCameras,
  //   error: errorTopCameras,
  //   refetch: refetchTopCameras
  // } = useGetList(
  //   `camera/top/beam-run/${beamRunId}`
  // )

  // const {
  //   data: sideCameras,
  //   isPending: isPendingSideCameras,
  //   error: errorSideCameras,
  //   refetch: refetchSideCameras
  // } = useGetList(
  //   `camera/side/beam-run/${beamRunId}`
  // )

  // const [create,
  //   {
  //     data: analysis,
  //     isPending: isPendingAnalysis,
  //     error: errorAnalysis
  //   }] = useCreate (
  //     `camera-analysis/complex/beam-run/${beamRunId}`
  //   )
  
  // const handleSubmit = () => {
  //   create()
  // }

  // if (isPendingTopCameras|| isPendingSideCameras || isPendingAnalysis) return null;
  // return (
  //   <Form onSubmit={handleSubmit}>
  //     {/* <SelectInput source="side_camera" choices={sideCameras} />
  //     <SelectInput source="top_camera" choices={topCameras} /> */}
  //     <CheckboxGroupInput source="complex_analysis_choices" choices={ComplexAnalysisChoices} />
  //     <Button type="submit"> Perform analysis </Button>
  //   </Form>
  // )
  return (
    <div></div>
  )
}