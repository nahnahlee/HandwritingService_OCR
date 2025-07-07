// backend/server.js
import express from 'express';
import multer from 'multer';
import cors from 'cors';
import fs from 'fs';
import path from 'path';
import { writeFile } from 'fs/promises';
import { createWorker } from 'tesseract.js';
import sharp from 'sharp';
import { execFile } from 'child_process';

const app = express();
const PORT = process.env.PORT || 3001;

// Ensure upload and result directories exist
['uploads', 'results'].forEach((dir) => {
  const dirPath = path.join(process.cwd(), dir);
  if (!fs.existsSync(dirPath)) fs.mkdirSync(dirPath, { recursive: true });
});

// Middlewares
app.use(cors());
app.use(express.json());

// Static file serving
app.use('/uploads', express.static(path.join(process.cwd(), 'uploads')));
app.use('/results', express.static(path.join(process.cwd(), 'results')));

// Multer setup for file uploads
const upload = multer({ dest: 'uploads/' });

// OCR processing function
async function performOcrAndExtract(files) {
  // Load both English and Korean models
  const worker = await createWorker('eng+kor');
  const THRESHOLD = 60;
  const unrecognized = [];

  for (const file of files) {
    // Recognize text in symbol (character) level
    const { data: { symbols } } = await worker.recognize(file.path);
    // Filter out low-confidence symbols
    const lowConf = (symbols || []).filter(sym => sym.confidence < THRESHOLD);

    for (const sym of lowConf) {
      const { x0, y0, x1, y1 } = sym.bbox;
      const snippetName = `${file.filename}_${sym.symbol}_${Date.now()}.png`;
      const outPath = path.join(process.cwd(), 'uploads', snippetName);
      await sharp(file.path)
        .extract({ left: x0, top: y0, width: x1 - x0, height: y1 - y0 })
        .toFile(outPath);
      unrecognized.push({ id: snippetName, imageURL: `/uploads/${snippetName}` });
    }
  }

  await worker.terminate();
  return unrecognized;
}

// 1) Note upload & OCR processing
app.post(
  '/api/notes/upload',
  upload.array('notes'),
  async (req, res, next) => {
    try {
      const unrecognized = await performOcrAndExtract(req.files);
      return res.json({ unrecognized });
    } catch (err) {
      return next(err);
    }
  }
);

// 2) Receive user corrections and save to annotations.json
app.post(
  '/api/notes/corrections',
  async (req, res, next) => {
    try {
      const { corrections } = req.body;
      await writeFile(
        path.join(process.cwd(), 'annotations.json'),
        JSON.stringify(corrections, null, 2)
      );
      return res.json({ success: true });
    } catch (err) {
      return next(err);
    }
  }
);


// ─── 3) Text-to-handwriting conversion via FUNIT inference ─────────────────
app.post(
  '/api/notes/convert',
  async (req, res, next) => {
    try {
      const { text } = req.body;
      // 1) 먼저 skeleton 텍스트 이미지를 만듭      // convert_cli.py는 이미 백엔드 루트에 있다고 가정
      const skeletonPath = path.join(process.cwd(), 'data', 'scratch', 'skeleton.png');
      await new Promise((r, j) =>
        execFile(
          'python',
          ['convert_cli.py', '--text', text, '--out', skeletonPath],
          { cwd: process.cwd() },
          (err) => (err ? j(err) : r())
        )
      );

      // 2) style reference (사용자 손글씨 샘플) 경로 지정
      const styleSample = path.join(process.cwd(), 'data', 'hand', 'B', 'sample1.png');

      // 3) FUNIT test_funit.py 스크립트 실행
      const outName = `hw_${Date.now()}.png`;
      const outPath = path.join(process.cwd(), 'results', outName);

      await new Promise((r, j) =>
        execFile(
          'python',
          [
            'test_funit.py',
            '--dataroot',  path.join(process.cwd(), 'data', 'hand'),
            '--name',      'handwriting_funit',
            '--n_shot',    '5',
            '--phase',     'test',
            '--num_test',  '1',
            '--content_path', skeletonPath,   // 스크립트에서 --content_path 옵션으로 받도록 수정 필요
            '--style_path',   styleSample,
            '--output_path',  outPath         // 마찬가지로 옵션으로 받도록 inference 스크립트 수정
          ],
          { cwd: path.join(process.cwd(), 'FUNIT') },
          (err) => (err ? j(err) : r())
        )
      );

      // 4) 결과 URL 반환
      return res.json({ imageURL: `/results/${outName}` });
    } catch (err) {
      return next(err);
    }
  }
);

// Global error handler
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({ error: 'Internal Server Error' });
});

// Start server
app.listen(PORT, () => console.log(`API listening on port ${PORT}`));
