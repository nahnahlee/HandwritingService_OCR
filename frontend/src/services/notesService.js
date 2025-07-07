export async function uploadNotes(files) {
  const form = new FormData();
  files.forEach(f => form.append('notes', f));
  const res = await fetch('/api/notes/upload', {
    method: 'POST',
    body: form,
  });
  return res.json(); // { unrecognized: [ { id, imageURL } ], … }
}


// src/services/notesService.js – corrections API 뼈대 추가
export async function submitCorrections(answers) {
  // answers: { id: label, … }
  const res = await fetch('/api/notes/corrections', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ corrections: answers }),
  });
  return res.json();
}


// src/services/notesService.js
export async function convertText(text) {
  const res = await fetch('/api/notes/convert', {       // <-- leading "/api/notes/convert"
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text }),
  });
  if (!res.ok) {
    throw new Error(`Convert failed: ${res.statusText}`);
  }
  const { imageURL } = await res.json();
  return imageURL;
}