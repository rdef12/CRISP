import { Button } from "@/components/ui/button"
import { useParams } from "react-router-dom";
import { Form, useCreateController } from "react-admin"
import { FlagDisconnectedCameras } from "../../real/takeData/FlagDisconnectedCameras";
import { Breadcrumbs } from "@/ExperimentAdmin/components/Breadcrumbs";
import { Timer } from "./Timer";
import { useTestData } from "../TestDataContext";


// const LoadingBar = ({ onComplete }) => {
//   const [progress, setProgress] = useState(0);
//   const [isLoading, setIsLoading] = useState(true);

//   useEffect(() => {
//     const timerDuration = 5000; // total duration in ms
//     const intervalDuration = 100; // interval duration in ms
//     const increment = (100 / (timerDuration / intervalDuration));

//     const interval = setInterval(() => {
//       setProgress((prevProgress) => {
//         if (prevProgress >= 100) {
//           clearInterval(interval);
//           setIsLoading(false);
//           onComplete(); // Trigger onComplete callback when finished
//           return 100;
//         }
//         return prevProgress + increment;
//       });
//     }, intervalDuration);

//     // Cleanup the interval when the component is unmounted or when done
//     return () => clearInterval(interval);
//   }, [onComplete]);

//   return (
//     <div style={{ width: '100%', backgroundColor: '#e0e0e0', height: '10px', borderRadius: '5px' }}>
//       <div
//         style={{
//           width: `${progress}%`,
//           height: '100%',
//           backgroundColor: '#3b82f6',
//           borderRadius: '5px',
//           transition: 'width 0.1s ease-out',
//         }}
//       />
//       {isLoading && <p>Loading...</p>}
//     </div>
//   );
// };

// // Finished Component
// const FinishedComponent = () => {
//   return <div><h2>Loading Complete!</h2></div>;
// };



  // const [isLoadingComplete, setIsLoadingComplete] = useState(false);

  // const handleLoadingComplete = () => {
  //   // This function is called once the loading is complete
  //   setIsLoadingComplete(true);
  // };

    // <div>
    // {!isLoadingComplete ? (
    //   <LoadingBar onComplete={handleLoadingComplete} />
    // ) : (
    //   <FinishedComponent />
    // )}
    // </div>

export const TakeTestData = () => {
  const { experimentId, beamRunId } = useParams();
  const { save, saving, isPending } = useCreateController({
    resource: `photo/beam-run/test/${beamRunId}`,
    redirect: `/experiment/${experimentId}/beam-run/test/${beamRunId}`
  });
  const { duration } = useTestData();
  console.log("DURSATION:", duration);
  if (isPending) return null;
  if (saving) return (
    <div className="flex flex-col items-center justify-center space-y-4">
      <h1 className="text-2xl font-bold">Taking data</h1>
      <Timer duration={duration} />
    </div>
  );
  return (
    <div>
      <Breadcrumbs />
      <Form onSubmit={save}>
        <Button>
          Start data collection
        </Button>
      </Form>
      <FlagDisconnectedCameras />
    </div>
  )
}
