import { useState } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Card } from "@/components/ui/card";

interface ShowAveragedPhotoProps {
  imageUrl: string;
  colourChannel: string
}

export const ShowAveragedPhoto = ({ imageUrl, colourChannel }: ShowAveragedPhotoProps) => {
  const [isDialogOpen, setIsDialogOpen] = useState(false);

  return (
    <div className="p-4 flex flex-col items-start gap-4">
      <Card className="inline-block p-4">
        <figure className="m-0">
          {imageUrl ? (
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
          ) : (
            <div 
              style={{ width: '150px', height: '150px' }}
              className="w-full h-full flex items-center justify-center bg-gray-100"
            >
              <span className="text-gray-500">Loading...</span>
            </div>
          )}
          <figcaption className="text-sm mt-1">Averaged image - {colourChannel} channel</figcaption>
        </figure>
      </Card>

      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        <DialogContent className="max-w-[90vw] max-h-[90vh]">
          <DialogHeader>
            <DialogTitle>Averaged Image - {colourChannel} Channel</DialogTitle>
          </DialogHeader>
          <div className="relative w-full flex justify-center items-center">
            {imageUrl ? (
              <img
                src={imageUrl}
                alt={`Full size averaged beam image - ${colourChannel} channel`}
                className="max-w-full max-h-[70vh] object-contain"
              />
            ) : (
              <div className="w-full h-[70vh] flex items-center justify-center bg-gray-100">
                <span className="text-gray-500">Loading...</span>
              </div>
            )}
          </div>
        </DialogContent>
      </Dialog>
    </div>
  )
}