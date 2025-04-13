import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { useEffect, useState } from "react";
import { useGetList, useRecordContext } from "react-admin";
import { useParams } from "react-router-dom"

interface Plot {
  id: number;
  plot: string;
}

interface ShowPlotsProps {
  isOpen: boolean;
  onOpenChange: (open: boolean) => void;
}

export const ShowPlots = ({ isOpen, onOpenChange }: ShowPlotsProps) => {
  const [imageUrls, setImageUrls] = useState<string[]>([]);
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  const { beamRunId } = useParams();
  const record = useRecordContext();
  console.log("SUPOSED REOCRD: ", record)
  const { data, isPending } = useGetList(
    `camera-analysis/plots/beam-run/${beamRunId}/camera/${record?.id}`
  )
  const plots = data as Plot[] | undefined;

  useEffect(() => {
    console.log('Plots data:', plots);
    if (plots) {
      const urls = plots.map((plot: Plot) => `data:image/jpeg;base64,${plot.plot}`);
      console.log('Generated URLs:', urls);
      console.log('Number of images:', urls.length);
      setImageUrls(urls);
    }
  }, [plots]);

  const nextImage = () => {
    console.log('Next image clicked');
    setCurrentImageIndex((prev) => (prev + 1) % imageUrls.length);
  };

  const previousImage = () => {
    console.log('Previous image clicked');
    setCurrentImageIndex((prev) => (prev - 1 + imageUrls.length) % imageUrls.length);
  };
  if (isPending) return null;
  return (
    <Dialog open={isOpen} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-[90vw] max-h-[90vh]">
        <DialogHeader className="flex flex-row items-center justify-center gap-6">
          {imageUrls.length > 1 ? (
            <Button 
              onClick={previousImage} 
              variant="secondary"
              className="bg-black hover:bg-gray-800 shadow-md h-10 w-[50px] flex items-center justify-center"
            >
              <ChevronLeft className="h-6 w-6 text-white" />
            </Button>
          ) : (
            <div className="w-[50px]" /> /* Spacer for alignment */
          )}
          <DialogTitle className="mx-4">
            Image {currentImageIndex + 1} of {imageUrls.length}
          </DialogTitle>
          {imageUrls.length > 1 ? (
            <Button 
              onClick={nextImage} 
              variant="secondary"
              className="bg-black hover:bg-gray-800 shadow-md h-10 w-[50px] flex items-center justify-center"
            >
              <ChevronRight className="h-6 w-6 text-white" />
            </Button>
          ) : (
            <div className="w-[50px]" /> /* Spacer for alignment */
          )}
        </DialogHeader>
        <div className="relative w-full flex justify-center items-center">
          <img
            src={imageUrls[currentImageIndex]}
            alt={`Full size plot ${currentImageIndex + 1}`}
            className="max-w-full max-h-[70vh] object-contain"
          />
        </div>
        {/* <DialogFooter className="w-full">
          {plots && plots[currentImageIndex] && (
            <DeleteButton
              record={{ id: plots[currentImageIndex].id.toString() }}
              onDelete={handlePlotDelete}
            />
          )}
        </DialogFooter> */}
      </DialogContent>
    </Dialog>
  )
}


{/* <div className="flex flex-col gap-4">
{plots.map((plot, index) => (
  <div key={index} className="w-full">
    <img 
      src={`data:image/svg+xml;base64,${plot}`}
      alt={`Analysis plot ${index + 1}`}
      className="w-full h-auto"
    />
  </div>
))}
</div> */}