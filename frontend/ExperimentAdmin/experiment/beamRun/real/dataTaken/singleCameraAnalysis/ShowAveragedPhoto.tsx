import { useState } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";

interface ShowAveragedPhotoProps {
  imageUrl: string;
  colourChannel: string
}

export const ShowAveragedPhoto = ({ imageUrl, colourChannel }: ShowAveragedPhotoProps) => {
  const [isDialogOpen, setIsDialogOpen] = useState(false);

  return (
    <div>
      <figure>
        <img 
          src={imageUrl} 
          alt={`Averaged beam image`}
          style={{ width: '150px', height: '150px', objectFit: 'cover', cursor: 'pointer' }}
          className="w-full h-full"
          onClick={() => setIsDialogOpen(true)}
          onError={(e) => console.error('Image loading error:', e)}
          onLoad={(e) => {
            const img = e.target as HTMLImageElement;
            console.log('Loaded image dimensions:', img.width, 'x', img.height);
          }}
        />
        <figcaption> Averaged image - {colourChannel} channel </figcaption>
      </figure>

      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        <DialogContent className="max-w-[90vw] max-h-[90vh]">
          <DialogHeader>
            <DialogTitle>Averaged Image - {colourChannel} Channel</DialogTitle>
          </DialogHeader>
          <div className="relative w-full flex justify-center items-center">
            <img
              src={imageUrl}
              alt={`Full size averaged beam image - ${colourChannel} channel`}
              className="max-w-full max-h-[70vh] object-contain"
            />
          </div>
        </DialogContent>
      </Dialog>
    </div>
  )
}