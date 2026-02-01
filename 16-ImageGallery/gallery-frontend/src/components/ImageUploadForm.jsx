import API from "../api";

export default function ImageUploadForm({ onUpload }) {

  const uploadImage = async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);

    try {
      await API.post("images/", formData);
      e.target.reset();
      onUpload();
    } catch (err) {
      console.error(err);
      alert("Upload failed!");
    }
  };

  return (
    <form onSubmit={uploadImage} className="mb-6 p-4 bg-white shadow rounded flex flex-col gap-2">
      <input name="title" placeholder="Title" required className="border p-2 rounded"/>
      <input name="description" placeholder="Description" className="border p-2 rounded"/>
      <input type="file" name="image" required className="border p-2 rounded"/>
      <button type="submit" className="bg-blue-500 text-white p-2 rounded hover:bg-blue-600">Upload</button>
    </form>
  );
}
