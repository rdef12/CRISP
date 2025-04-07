interface ShowAveragedPhotoProps {
  imageUrl: string;
  colourChannel: string
}

export const ShowAveragedPhoto = ({ imageUrl, colourChannel }: ShowAveragedPhotoProps) => {
  return (
    <div>
      <figure>
        <img 
          src={imageUrl} 
          alt={`Averaged beam image`}
          style={{ width: '150px', height: '150px', objectFit: 'cover' }}
          className="w-full h-full"
          onError={(e) => console.error('Image loading error:', e)}
          onLoad={(e) => {
            const img = e.target as HTMLImageElement;
            console.log('Loaded image dimensions:', img.width, 'x', img.height);
          }}
        />
        <figcaption> Averaged image - {colourChannel} channel </figcaption>
      </figure>
    </div>
  )
}