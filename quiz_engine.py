import random


def select_questions(all_questions, count, user):
    # Filter out disliked
    disliked = set(user.get('disliked_ids', []))
    liked = set(user.get('liked_ids', []))
    available = [q for q in all_questions if q.get('id') not in disliked]

    if len(available) == 0:
        return []

    # Try to include liked questions first
    liked_questions = [q for q in available if q.get('id') in liked]
    other_questions = [q for q in available if q.get('id') not in liked]

    # Shuffle both lists so ordering isn't deterministic
    random.shuffle(liked_questions)
    random.shuffle(other_questions)

    chosen = []
    for q in liked_questions:
        if len(chosen) < count:
            chosen.append(q)

    # Fill remaining slots randomly from other_questions
    for q in other_questions:
        if len(chosen) < count:
            chosen.append(q)

    return chosen


def evaluate_answer(question, user_input):
    qtype = question.get('type')
    correct = question.get('answer')
    if qtype == 'multiple_choice' or qtype == 'short_answer' or qtype == 'true_false':
        # normalize
        if isinstance(user_input, str):
            ui = user_input.strip()
        else:
            ui = str(user_input).strip()
        return ui.lower() == str(correct).lower()
    return False


def calculate_score(results):
    # results: list of booleans whether each answer was correct
    total = 0
    streak = 0
    highest_streak = 0
    for correct in results:
        if correct:
            streak += 1
            if streak == 1:
                points = 10
            elif streak == 2:
                points = 15
            else:
                points = 20
            total += points
            if streak > highest_streak:
                highest_streak = streak
        else:
            streak = 0
    return total, highest_streak
