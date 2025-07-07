// src/components/VerificationDialog.js
import React, { useState } from 'react';

export default function VerificationDialog({ items, onSubmit }) {
  // items = [{ id, imageURL }]
  const [answers, setAnswers] = useState({});

  const handleChange = (id, val) => {
    setAnswers(prev => ({ ...prev, [id]: val }));
  };

  const handleSubmit = () => {
    // 누락된 답변 없으면
    if (items.every(item => answers[item.id])) {
      onSubmit(answers);
    } else {
      alert('모두 입력해 주세요.');
    }
  };

  return (
    <div className="verification-modal">
      <h2>확인해주세요</h2>
      {items.map(item => (
        <div key={item.id} className="verify-item">
          <img src={item.imageURL} alt="unknown" />
          <input
            type="text"
            maxLength={1}
            value={answers[item.id] || ''}
            onChange={e => handleChange(item.id, e.target.value)}
            placeholder="글자 입력"
          />
        </div>
      ))}
      <button onClick={handleSubmit}>제출하기</button>
    </div>
  );
}
