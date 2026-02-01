export default function ImageCard({ image }) {
  return (
    <div className="bg-white shadow-md rounded overflow-hidden">
      <img className="w-full h-64 object-cover" src={image.image} alt={image.title} />
      <div className="p-4">
        <h2 className="text-lg font-bold">{image.title}</h2>
        <p className="text-gray-600">{image.description}</p>
      </div>
    </div>
  )
}
