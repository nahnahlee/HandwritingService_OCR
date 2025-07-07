// src/components/ProcessingIndicator.js
import React from 'react';

export default function ProcessingIndicator() {
  return (
    <div className="processing">
      <div className="spinner" />
      <p>노트를 분석 중입니다… 잠시만 기다려 주세요.</p>
    </div>
  );
}
