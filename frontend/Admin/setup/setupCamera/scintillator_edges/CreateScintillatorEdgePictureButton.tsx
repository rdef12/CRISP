// import { Button } from "@/components/ui/button";
// import { useCreateController } from "react-admin";
// import { useParams } from "react-router-dom";

// export const CreateScintillatorEdgePictureButton = () => {
//   const setupCameraId = useParams();
//   const { record, save , isPending} = useCreateController({ resource:`photo/scintillator-edges/${setupCameraId}`, redirect: false })
//   if (isPending) return null;
//   return (
//     <Button onClick={save}>
//       Take picture
//     </Button>
//   )
  
// }