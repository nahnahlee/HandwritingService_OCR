import React from 'react';

export default function UploadNotes({ files, onChange }) {
  return (
    <div className="upload-notes">
      <input 
        type="file" 
        accept="image/*" 
        multiple 
        onChange={e => onChange(Array.from(e.target.files))} 
      />
      <div className="thumbnails">
        {files.map((file, idx) => (
          <img
            key={idx}
            src={URL.createObjectURL(file)}
            alt={`note-${idx}`}
            className="thumb"
          />
        ))}
      </div>
    </div>
  );
}
