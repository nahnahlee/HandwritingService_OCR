// src/App.js
import React, { useState } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import UploadNotes from './components/UploadNotes';
import ProcessingIndicator from './components/ProcessingIndicator';
import VerificationDialog from './components/VerificationDialog';
import TextInput from './components/TextInput';
import PreviewImage from './components/PreviewImage';
import {
  uploadNotes,
  submitCorrections,
  convertText
} from './services/notesService';
import './App.css';

// 메인 추론 페이지 컴포넌트
function InferencePage() {
  const [phase, setPhase] = useState('upload');
  const [files, setFiles] = useState([]);
  const [unrecognized, setUnrecognized] = useState([]);
  const [resultImage, setResultImage] = useState('');

  // 파일 선택 핸들러
  const handleFilesChange = (newFiles) => {
    setFiles(newFiles);
  };

  // 노트 업로드 및 OCR 처리 시작
  const startProcessing = async () => {
    setPhase('processing');
    try {
      const res = await uploadNotes(files);
      if (res.unrecognized && res.unrecognized.length) {
        setUnrecognized(res.unrecognized);
        setPhase('verifying');
      } else {
        setPhase('readyForInput');
      }
    } catch (err) {
      console.error(err);
      alert('노트 업로드 실패: 다시 시도해 주세요.');
      setPhase('upload');
    }
  };

  // 사용자 검증 제출 핸들러
  const handleVerificationSubmit = async (answers) => {
    try {
      await submitCorrections(answers);
      setPhase('readyForInput');
    } catch (err) {
      console.error(err);
      alert('검증 정보 전송 실패: 다시 시도해 주세요.');
    }
  };

  // 텍스트 변환 실행 핸들러
  const handleConvert = async (text) => {
    try {
      const url = await convertText(text);
      setResultImage(url);
      setPhase('complete');
    } catch (err) {
      console.error(err);
      alert('텍스트 변환 실패: 다시 시도해 주세요.');
    }
  };

  return (
    <div className="App">
      {phase === 'upload' && (
        <>
          <UploadNotes files={files} onChange={handleFilesChange} />
          <button
            disabled={!files.length}
            onClick={startProcessing}
          >
            노트 분석 시작
          </button>
        </>
      )}

      {phase === 'processing' && (
        <ProcessingIndicator />
      )}

      {phase === 'verifying' && (
        <VerificationDialog
          items={unrecognized}
          onSubmit={handleVerificationSubmit}
        />
      )}

      {phase === 'readyForInput' && (
        <TextInput onConvert={handleConvert} />
      )}

      {phase === 'complete' && (
        <PreviewImage src={resultImage} />
      )}
    </div>
  );
}

// App 컴포넌트: 라우터 설정
function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/infer" element={<InferencePage />} />
        {/* 필요 시 다른 경로 추가 */}
      </Routes>
    </BrowserRouter>
  );
}

export default App;
