// src/components/PreviewImage.jsx
import React from 'react';

export default function PreviewImage({ src }) {
  if (!src) return null;

  const handleDownload = async () => {
    // 1) 올바른 풀 URL 생성
    const downloadUrl = src.startsWith('http')
      ? src
      : `http://localhost:3001${src}`;

    try {
      // 2) 파일을 fetch → blob 으로 변환
      const res = await fetch(downloadUrl);
      if (!res.ok) throw new Error('파일 가져오기 실패');
      const blob = await res.blob();

      // 3) Blob URL 생성 및 다운로드 트리거
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = downloadUrl.split('/').pop();
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error(err);
      alert('다운로드 실패');
    }
  };

  return (
    <div className="preview">
      <h3>완성된 손글씨 이미지</h3>
      <img
        src={src.startsWith('http') ? src : `http://localhost:3001${src}`}
        alt="handwriting result"
        style={{ maxWidth: '100%' }}
      />
      <button className="btn" onClick={handleDownload}>
        다운로드
      </button>
    </div>
  );
}
