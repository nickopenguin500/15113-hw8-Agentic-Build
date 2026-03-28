import sys
from data_manager import load_questions, read_users, write_users
from auth import hash_password, verify_password
from quiz_engine import select_questions, evaluate_answer, calculate_score


def prompt_int(prompt):
    while True:
        try:
            val = input(prompt+' ')
            return int(val)
        except ValueError:
            print('Invalid input. Please enter a valid number.')


def prompt_choice(prompt, choices):
    # choices is dict of int->callable
    while True:
        try:
            val = int(input(prompt+' '))
            if val in choices:
                return val
            else:
                print('Invalid input. Please enter a valid number.')
        except ValueError:
            print('Invalid input. Please enter a valid number.')


def register(users):
    while True:
        username = input('Choose a username: ').strip()
        if not username:
            print('Username cannot be empty.')
            continue
        if username in users:
            print('Username already taken.')
            return None
        break
    while True:
        password = input('Choose a password: ').strip()
        if not password:
            print('Password cannot be empty.')
            continue
        break
    users[username] = {
        'password': hash_password(password),
        'score': 0,
        'highest_streak': 0,
        'liked_ids': [],
        'disliked_ids': []
    }
    write_users(users)
    print('Registered successfully.')
    return username


def login(users):
    username = input('Username: ').strip()
    password = input('Password: ').strip()
    user = users.get(username)
    if not user:
        print('Invalid username or password.')
        return None
    if verify_password(user.get('password',''), password):
        print('Login successful.')
        return username
    else:
        print('Invalid username or password.')
        return None


def take_quiz(username, users, questions):
    user = users[username]
    # Ask repeatedly until we get an integer
    while True:
        try:
            n = int(input('How may questions would you like to answer? ').strip())
            break
        except ValueError:
            print('Invalid input. Please enter a valid number.')

    total_available = len([q for q in questions if q.get('id') not in set(user.get('disliked_ids', []))])
    if total_available == 0:
        print('Error: No questions available for your profile.')
        return
    if n > total_available:
        print(f'Error: Only {total_available} questions available. Starting quiz with {total_available} questions.')
        n = total_available

    selected = select_questions(questions, n, user)
    results = []
    for q in selected:
        print('\nCategory:', q.get('category'))
        print('Question:', q.get('question'))
        if q.get('type') == 'multiple_choice':
            for idx, opt in enumerate(q.get('options', []), start=1):
                print(f'  {idx}. {opt}')
            ans = input('Your answer (type the option text or number): ').strip()
            # allow number or text
            if ans.isdigit():
                idx = int(ans)-1
                if 0 <= idx < len(q.get('options', [])):
                    ans_text = q.get('options', [])[idx]
                else:
                    ans_text = ans
            else:
                ans_text = ans
            correct = evaluate_answer(q, ans_text)
        elif q.get('type') == 'true_false':
            print('  1. True')
            print('  2. False')
            ans = input('Your answer (True/False or 1/2): ').strip()
            if ans == '1':
                ans_text = 'true'
            elif ans == '2':
                ans_text = 'false'
            else:
                ans_text = ans
            correct = evaluate_answer(q, ans_text)
        else:
            ans_text = input('Your answer: ').strip()
            correct = evaluate_answer(q, ans_text)

        if correct:
            print('Correct!')
            results.append(True)
        else:
            print(f"Incorrect. The right answer was {q.get('answer')}.")
            results.append(False)

        # feedback
        print('Did you like this question? [1] Yes, [2] No, [3] Skip')
        fb = None
        while True:
            try:
                fb_in = int(input('Choice: ').strip())
                if fb_in in (1,2,3):
                    fb = fb_in
                    break
            except ValueError:
                pass
            print('Invalid input. Please enter a valid number.')

        qid = q.get('id')
        if fb == 1:
            if qid not in user.get('liked_ids', []):
                user.setdefault('liked_ids', []).append(qid)
            # remove from disliked if present
            if qid in user.get('disliked_ids', []):
                user['disliked_ids'].remove(qid)
        elif fb == 2:
            if qid not in user.get('disliked_ids', []):
                user.setdefault('disliked_ids', []).append(qid)
            if qid in user.get('liked_ids', []):
                user['liked_ids'].remove(qid)
    # else skip
    # Persist feedback immediately so it's not lost on crash
    write_users(users)

    points, highest = calculate_score(results)
    print(f'Quiz complete. You scored {points} points.')
    # Update user stats
    user['score'] = user.get('score', 0) + points
    if highest > user.get('highest_streak', 0):
        user['highest_streak'] = highest
    write_users(users)


def view_stats(username, users):
    user = users[username]
    print(f"Total score: {user.get('score',0)}")
    print(f"Highest All-Time Streak: {user.get('highest_streak',0)}")


def main():
    try:
        questions = load_questions()
    except FileNotFoundError:
        sys.exit(1)

    if not questions or len(questions) == 0:
        print('Error: question bank is empty')
        sys.exit(1)

    users = read_users()

    # Startup auth loop
    while True:
        print('\nWelcome! Choose an option: [1] Login, [2] Register, [3] Quit')
        try:
            choice = int(input('Choice: ').strip())
        except ValueError:
            print('Invalid input. Please enter a valid number.')
            continue

        if choice == 2:
            register(users)
        elif choice == 1:
            user = login(users)
            if user:
                # Main menu
                while True:
                    print('\n[1] Take Quiz, [2] View Stats, [3] Logout')
                    try:
                        c = int(input('Choice: ').strip())
                    except ValueError:
                        print('Invalid input. Please enter a valid number.')
                        continue
                    if c == 1:
                        take_quiz(user, users, questions)
                    elif c == 2:
                        view_stats(user, users)
                    elif c == 3:
                        break
                    else:
                        print('Invalid input. Please enter a valid number.')
        elif choice == 3:
            print('Goodbye.')
            break
        else:
            print('Invalid input. Please enter a valid number.')


if __name__ == '__main__':
    main()
