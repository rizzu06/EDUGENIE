const task = document.querySelector('#task');
const input = document.querySelector('#input');
const submit = document.querySelector('#submit');
const clear = document.querySelector('#clear');
const resultCard = document.querySelector('#result-card');
const result = document.querySelector('#result');
const count = document.querySelector('#count');
const status = document.querySelector('#status');
const quizRow = document.querySelector('#quiz-row');
const levelRow = document.querySelector('#level-row');
const copy = document.querySelector('#copy');

const endpoints = {
  qa: '/qa',
  explain: '/explain',
  quiz: '/quiz',
  summarize: '/summarize',
  learn: '/learn/recommendations'
};

function updateTaskUI() {
  quizRow.classList.toggle('hidden', task.value !== 'quiz');
  levelRow.classList.toggle('hidden', task.value !== 'learn');
  const placeholders = {
    qa: 'Example: Why is the sky blue?',
    explain: 'Example: Pythagoras theorem',
    quiz: 'Paste a passage or topic you want to turn into a quiz.',
    summarize: 'Paste a long educational passage for quick revision.',
    learn: 'Example: SQL, machine learning, digital electronics, or Python.'
  };
  input.placeholder = placeholders[task.value];
}

task.addEventListener('change', updateTaskUI);
input.addEventListener('input', () => { count.textContent = input.value.length.toLocaleString(); });

function escapeHtml(value) {
  return value.replace(/[&<>'"]/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[char]));
}

function renderQuiz(data) {
  result.innerHTML = data.questions.map((item, index) => `
    <article class="quiz-item" data-question="${index}">
      <h3>${index + 1}. ${escapeHtml(item.question)}</h3>
      ${item.options.map((option, i) => `
        <label class="quiz-option">
          <input type="radio" name="q-${index}" value="${escapeHtml(option)}">
          <span><strong>${String.fromCharCode(65 + i)}.</strong> ${escapeHtml(option)}</span>
        </label>
      `).join('')}
      <div class="answer hidden"></div>
    </article>
  `).join('') + '<button id="check-quiz" type="button">Check answers</button>';

  document.querySelector('#check-quiz').addEventListener('click', () => {
    let score = 0;
    data.questions.forEach((item, index) => {
      const card = document.querySelector(`[data-question="${index}"]`);
      const selected = card.querySelector(`input[name="q-${index}"]:checked`);
      const answer = card.querySelector('.answer');
      answer.classList.remove('hidden');
      if (selected && selected.value === item.correct_answer) {
        score += 1;
        answer.innerHTML = `<strong>Correct.</strong> ${escapeHtml(item.explanation)}`;
      } else {
        answer.innerHTML = `<strong>Correct answer:</strong> ${escapeHtml(item.correct_answer)}<br>${escapeHtml(item.explanation)}`;
      }
    });
    document.querySelector('#check-quiz').textContent = `Score: ${score}/${data.questions.length}`;
  });
}
function getPayload() {
  const payload = { text: input.value.trim() };
  if (task.value === 'quiz') payload.num_questions = Number(document.querySelector('#num-questions').value);
  if (task.value === 'learn') {
    payload.level = document.querySelector('#level').value;
    payload.timeframe = document.querySelector('#timeframe').value.trim() || '8 weeks';
  }
  return payload;
}

async function run() {
  const text = input.value.trim();
  if (!text) {
    resultCard.hidden = false;
    result.textContent = 'Please enter something to work with.';
    return;
  }

  submit.disabled = true;
  submit.textContent = 'Thinking…';
  resultCard.hidden = false;
  result.textContent = 'EduGenie is generating your result…';

  try {
    const response = await fetch(endpoints[task.value], {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(getPayload())
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || 'The server returned an error.');
    if (task.value === 'quiz') renderQuiz(data);
    else result.textContent = data.result;
  } catch (error) {
    result.textContent = `Error: ${error.message}`;
  } finally {
    submit.disabled = false;
    submit.textContent = 'Generate answer';
  }
}

submit.addEventListener('click', run);
clear.addEventListener('click', () => {
  input.value = '';
  count.textContent = '0';
  resultCard.hidden = true;
  result.textContent = '';
});
copy.addEventListener('click', async () => {
  await navigator.clipboard.writeText(result.innerText);
  copy.textContent = 'Copied';
  setTimeout(() => { copy.textContent = 'Copy'; }, 1200);
});

async function checkHealth() {
  try {
    const response = await fetch('/health');
    const data = await response.json();
    status.textContent = data.gemini_configured ? 'AI service ready' : 'Add GEMINI_API_KEY';
  } catch {
    status.textContent = 'Backend unavailable';
  }
}

updateTaskUI();
checkHealth();
