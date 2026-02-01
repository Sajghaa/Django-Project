import { useEffect, useState } from "react";
import API from "./api";
import ImageCard from "./components/ImageCard";
import ImageUploadForm from "./components/ImageUploadForm";

function App() {
  const [images, setImages] = useState([]);

  const fetchImages = async () => {
    try {
      const res = await API.get("images/");
      setImages(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchImages();
  }, []);

  return (
    <div className="max-w-6xl mx-auto py-8 px-4">
      <h1 className="text-4xl font-bold mb-6 text-center">Lavish Image Gallery</h1>

      <ImageUploadForm onUpload={fetchImages} />

      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
        {images.map(img => (
          <ImageCard key={img.id} image={img} />
        ))}
      </div>
    </div>
  );
}

export default App;
