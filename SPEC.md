1. Behavior Description (State Flow)
The app operates entirely in the command line and follows this exact flow:
Startup: The app initializes and loads questions.json and the secure user data file.
Authentication: The user is prompted with "Welcome! Choose an option: [1] Login, [2] Register, [3] Quit. If [2] Register is selected, prompt the user for a new username and password. Save these securely. If [1] Login is prompted, ask the user for a username and password. Validate against the secure file.
Main Menu: Once authenticated, prompt the user to select an option: "[1] Take Quiz, [2] View Stats, [3] Logout".
Quiz: Prompt the user with "How may questions would you like to answer?" Then, select the requested number of questions from the question bank, prioritizing "liked" questions and avoiding "disliked" questions. For each question, print the category, question text, and the options. After the user inputs their answer, print "Correct!" if their answer is correct, else "Incorrect. The right answer was X." After displaying the answer result, ask the user "Did you like this question?" with the options "[1] Yes, [2] No, [3] Skip". Save their response to the user's profile.
End: Display the final score and the longest streak achieved. Update these stats to the secure file. Return to the Main Menu.

2. The question bank is stored in questions.json. Every question has a unique id. Here are some example questions.
{
  "questions": [
    {
      "question": "What keyword is used to define a function in Python?",
      "type": "multiple_choice",
      "options": ["func", "define", "def", "function"],
      "answer": "def",
      "category": "Python Basics"
    },
    {
      "question": "A list in Python is immutable.",
      "type": "true_false",
      "answer": "false",
      "category": "Data Structures"
    },
    {
      "question": "What built-in function returns the number of items in a list?",
      "type": "short_answer",
      "answer": "len",
      "category": "Python Basics"
    },
    {
      "question": "Which of these data structures uses key-value pairs?",
      "type": "multiple_choice",
      "options": ["List", "Tuple", "Dictionary", "Set"],
      "answer": "Dictionary",
      "category": "Data Structures"
    },
    {
      "question": "In Python, 'True' and 'False' must always be capitalized.",
      "type": "true_false",
      "answer": "true",
      "category": "Python Basics"
    }
  ]
}

3. File Structure
The project must be split into the following files:
main.py: Contains the main loops for the menus and handles direct user input and output.
auth.py: Contains functions for hashing the passwords and verifying logins.
quiz_engine.py: Contains the code for the quiz logic, streak calculations, evaluating answers, and sorting questions.
data_manager.py: Contains code for reading/writing to the questions.json file and the secure users.dat file.
questions.json: The question bank.
users.dat: The secure, non-readable file containing user logins, scores, and feedback histories.

4. Error Handling
The app must not crash due to unexpected inputs. Implement these methods of error handling:
Missing File: If questions.json is missing, catch the error and print "Error: questions.json not found" and exit the program safely.
Invalid Input: If a prompt expects an integer (like the menu choices) and the user types something that is not an integer, catch the error and print "Invalid input. Please enter a valid number." and reprint the prompt.
Not Enough Questions: If the user types a number larger than the number of questions in the bank, the app should print "Error: Only X questions available. Starting quiz with X questions." and proceed with a quiz of X questions.
Duplicate Username: If a user tries to register as a username that already exists in the secure users.dat file, the app must prevent the account creation and print "Username already taken."

5. Required Features and Implementation Details
Security: Passwords must never be stored in plaintext. Hash passwords before storing them.
Non-readable storage: User data must be saved in an encoded way to ensure it is not easily readable by humans.
Feedback Engine: The user object in users.dat must contain two lists: "liked_ids" and "disliked_ids". When quiz_engine.py generates a quiz, it must filter out any IDs in the user's "disliked_ids" list. It must also try to include as many from the "liked_ids" list as possible.

6. Extension Feature: Streak Bonus
The quiz must have a point multiplier based on consecutive correct answers.
Base score: 10 points per correct answer.
Streak logic: 1st correct answer: 10 points (1x multiplier), 2nd correct answer: 15 points (1.5x multiplier), 3rd correct answer: 20 points(2x multiplier).
Reset: If the user gets a question wrong, the streak multiplier resets to 1x and they earn 0 points for that question.
The view stats menu must display the user's "Highest  All-Time Streak".

7. Acceptance Criteria
1. Running python main.py successfully launches the app without errors.
2. A new user can register, close the app immediately, relaunch the app, and successfully log in with their credentials.
3. Opening users.dat in a text editor reveals unreadable text, no plaintext passwords or data.
4. Entering "five" when asked how many questions the user would like to answer does not crash the app, but prompts the user to enter a valid number.
5. Answering three questions correctly in a row awards exactly 45 points (10 + 15 + 20)
6. If a user marks a question with "No" (dislike), that specific question will not appear in their next quiz (if possible due to number of questions).
7. Running the app with an empty question bank prints a friendly error and exits with code 1.