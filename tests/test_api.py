from fastapi.testclient import TestClient

import main

client = TestClient(main.app)


def test_homepage():
    response = client.get('/')
    assert response.status_code == 200
    assert 'EduGenie' in response.text


def test_health():
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json()['status'] == 'ok'


def test_qa(monkeypatch):
    monkeypatch.setattr(main, 'answer_question', lambda question, context='': f'Answer: {question}')
    response = client.post('/qa', json={'text': 'What is photosynthesis?'})
    assert response.status_code == 200
    assert response.json()['result'].startswith('Answer:')


def test_explain(monkeypatch):
    monkeypatch.setattr(main, 'explain_concept', lambda topic: f'Explanation: {topic}')
    response = client.post('/explain', json={'text': 'gravity'})
    assert response.status_code == 200
    assert 'gravity' in response.json()['result']


def test_quiz(monkeypatch):
    monkeypatch.setattr(
        main,
        'generate_quiz',
        lambda passage, num_questions: {
            'questions': [
                {
                    'question': '2 + 2?',
                    'options': ['3', '4', '5', '6'],
                    'correct_answer': '4',
                    'explanation': 'Basic addition.',
                }
            ] * num_questions
        },
    )
    response = client.post('/quiz', json={'text': 'Addition', 'num_questions': 3})
    assert response.status_code == 200
    assert len(response.json()['questions']) == 3


def test_summary(monkeypatch):
    monkeypatch.setattr(main, 'summarize_text', lambda text: 'Short summary')
    response = client.post('/summarize', json={'text': 'Long passage'})
    assert response.status_code == 200
    assert response.json()['result'] == 'Short summary'


def test_learning_path(monkeypatch):
    monkeypatch.setattr(
        main,
        'get_learning_recommendations',
        lambda topic, level, timeframe: f'{topic}-{level}-{timeframe}',
    )
    response = client.post(
        '/learn/recommendations',
        json={'text': 'SQL', 'level': 'beginner', 'timeframe': '8 weeks'},
    )
    assert response.status_code == 200
    assert response.json()['result'] == 'SQL-beginner-8 weeks'


def test_empty_input_rejected():
    response = client.post('/summarize', json={'text': '   '})
    assert response.status_code == 422
