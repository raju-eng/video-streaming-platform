// Frontend React App (React.js)

// 1. Create a new React app (if not already created)
// Run this in the terminal:
// npx create-react-app video-streaming-frontend

// 2. Replace the contents of src/App.js with the following:

import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [videoFile, setVideoFile] = useState(null);
  const [uploadStatus, setUploadStatus] = useState("");
  const [videoUrl, setVideoUrl] = useState("");

  const handleFileChange = (event) => {
    setVideoFile(event.target.files[0]);
  };

  const handleUpload = async () => {
    if (!videoFile) {
      setUploadStatus("Please select a video file.");
      return;
    }

    setUploadStatus("Uploading...");

    const formData = new FormData();
    formData.append("file", videoFile);

    try {
      const response = await axios.post(
        "https://your-api-endpoint/upload", // Replace with your API Gateway or backend endpoint
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );

      setUploadStatus("Upload successful!");
      setVideoUrl(response.data.videoUrl); // Assuming backend returns the processed video URL
    } catch (error) {
      console.error("Error uploading file:", error);
      setUploadStatus("Upload failed. Please try again.");
    }
  };

  return (
    <div className="App">
      <h1>Video Streaming Platform</h1>

      <div className="upload-section">
        <input type="file" accept="video/*" onChange={handleFileChange} />
        <button onClick={handleUpload}>Upload Video</button>
        <p>{uploadStatus}</p>
      </div>

      {videoUrl && (
        <div className="video-section">
          <h2>Stream Your Video</h2>
          <video controls width="600">
            <source src={videoUrl} type="video/mp4" />
            Your browser does not support the video tag.
          </video>
        </div>
      )}
    </div>
  );
}

export default App;

// 3. Add basic styles in src/App.css
/* App.css */
.App {
  text-align: center;
  padding: 20px;
}

.upload-section {
  margin: 20px 0;
}

.video-section {
  margin-top: 30px;
}
