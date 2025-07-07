// src/components/TextInput.jsx
import React, { useState } from 'react';

export default function TextInput({ onConvert }) {
  const [text, setText] = useState('');
  return (
    <div className="text-input">
      <textarea
        rows={3}
        value={text}
        onChange={e => setText(e.target.value)}
        placeholder="여기에 변환할 문구를 입력하세요"
      />
      <button
        className="btn"
        disabled={!text.trim()}
        onClick={() => onConvert(text)}
      >
        변환하기
      </button>
    </div>
  );
}
