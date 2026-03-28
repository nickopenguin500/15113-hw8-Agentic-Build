Checklist (requirements extracted from SPEC.md)
Startup loads questions.json and secure user data. (A)
CLI auth menu with Login/Register/Quit. (B)
Main menu after auth with Take Quiz/View Stats/Logout. (C)
Quiz asks number of questions, prioritizes liked and excludes disliked, shows Q/options, evaluates answer, asks feedback, persists feedback. (D)
End-of-quiz shows final score & longest streak, updates stored stats. (E)
Questions in questions.json with unique id. (F)
Error handling: missing file, invalid numeric input, not-enough-questions message, duplicate username. (G)
Security: hashed passwords, non-readable storage for users. (H)
Streak bonus scoring: 10 / 15 / 20, reset on wrong, view shows highest all-time streak. (I)
Acceptance criteria 1–7 from SPEC.md (explicit mapping tested below).
Progress update: I loaded SPEC.md, auth.py, data_manager.py, quiz_engine.py, main.py, questions.json, and users.dat. Next: detailed findings and requirement-status mapping.

Findings (numbered)
[PASS] auth hashing & verification look correct (safe pbkdf2 usage).

File: auth.py lines 6–11 and 14–20.
Notes: uses PBKDF2-HMAC-SHA256 with 100k iterations, salt generated with os.urandom(16), and hmac.compare_digest for timing-safe compare.
[WARN] verify_password swallows all exceptions too broadly.

File: auth.py lines 14–22.
Problem: broad except hides decode/format errors; better to catch specific exceptions (ValueError, TypeError) and log/handle them.
[FAIL] load_questions() does not guard against malformed JSON or missing 'questions' key.

File: data_manager.py lines 8–14.
Problem: it only catches FileNotFoundError and re-raises; a JSON decoding error or missing 'questions' key will raise and crash the program (not caught as intended by the spec).
Suggestion: catch json.JSONDecodeError and KeyError and print friendly error as spec requires.
[WARN] read_users() silently returns empty dict on decode/corruption.

File: data_manager.py lines 16–26.
Problem: when base64 decode / JSON parsing fails the function returns {}, losing existing data without warning. This can hide corruption or accidental truncation.
Suggestion: log an error (or back up corrupted file) instead of silently returning {}.
[WARN] users storage is only base64-encoded (not encrypted).

File: data_manager.py lines 28–33 and users.dat content.
Behavior: write_users() base64-encodes JSON. This satisfies "non-readable" in a cursory sense (file is not plain JSON), but base64 is trivially reversible.
Security note: passwords themselves are hashed and safe, but user data (usernames, likes/dislikes, scores) are recoverable. Also file permissions are not set—file may be world-readable by default.
[PASS] select_questions() filters out disliked and tries to include liked questions first.

File: quiz_engine.py lines 3–27.
Notes: disliked filtering and liked-first logic implemented. If liked count > requested count, the function takes the first N liked questions in existing order.
[WARN] select_questions() does not randomize or prioritize liked questions when liked > count.

File: quiz_engine.py lines 16–19 and 21–25.
Behavior: if liked questions exceed requested count, selection uses the current order (no shuffle). This may be acceptable, but spec asked to "try to include as many from liked_ids as possible" (it does) — consider shuffling liked list when more than needed.
[PASS] Answer evaluation is case-insensitive and supports multiple types.

File: quiz_engine.py lines 29–39 and main.py lines 78–91 and 92–103.
Notes: evaluate_answer lowercases both sides; main maps numeric choices to text for multiple-choice.
[FAIL] take_quiz numeric input handling does not re-prompt; it returns to menu on invalid input.

File: main.py lines 57–63.
Spec required the app to prompt again for a valid number. Code prints "Invalid input..." and returns early (skips the quiz). This fails acceptance criterion #4 which requires re-prompting for numbers like "five".
[PASS] Not-enough-questions behavior implemented.

File: main.py lines 65–71.
Behavior: if requested number > available, prints "Error: Only X questions available. Starting quiz with X questions." and proceeds with X questions.
[PASS] Feedback (like/dislike/skip) is saved to the user object.

File: main.py lines 114–139.
Notes: liked_ids/disliked_ids are appended/removed appropriately and persisted via write_users() at quiz end.
[WARN] Feedback is only flushed at end of the quiz.

File: main.py line 147 (write_users call).
Implication: if program crashes during the quiz, feedback is lost. Consider writing per-question or periodically.
[PASS] Streak scoring follows spec (10, 15, 20) and reset on wrong answer.

File: quiz_engine.py lines 41–60 and main.py lines 141–146.
Example: three consecutive Trues produce 10 + 15 + 20 = 45 (acceptance criterion #5 satisfied).
[PASS] View stats shows total score and highest all-time streak.

File: main.py lines 149–152.
[WARN] Duplicate username check works but empty username/password allowed.

File: main.py lines 26–33.
Problem: register() accepts blank usernames or passwords (user can input empty string). Spec demands prevention of duplicate usernames but doesn't state blank handling—still a quality/security issue.
[WARN] Many input-validation patterns are duplicated; unused helpers exist.

File: main.py lines 6–25 (prompt_int/prompt_choice are defined) but not used consistently (e.g., take_quiz uses int(input(...)) directly). This duplication increases maintenance burden and causes inconsistent behavior (re-prompt vs return).
[WARN] Error messages inconsistent: load_questions() prints "Error: questions.json not found" then re-raises; main() catches and exits but does not print that message itself.

File: data_manager.py lines 8–14 and main.py lines 155–158, 160–162.
Behavior: the message is printed in load_questions(), then main exits; acceptable but a bit indirect.
[WARN] read_users()/write_users() lack file permission management.

File: data_manager.py lines 16–33.
Suggestion: set restrictive mode (e.g., os.open + os.fchmod) or os.chmod after write to reduce exposure on multi-user systems.
[WARN] Broad exception handling hides specific bugs.

Multiple files: auth.py lines 14–22; data_manager.py lines 21–26.
Suggestion: catch and handle specific exceptions and provide diagnostic messages.
[PASS] Acceptance criteria mapping (SPEC 7 items):

Launch python main.py without errors: PASS in normal/expected environment with provided files. (Files: main.py lines 154–204; data_manager.py lines 8–14) — note: malformed questions.json would break (see #3).
New user register → close/relaunch → login: PASS (register writes base64 JSON; auth hashes). (Files: main.py register lines 26–41; data_manager.py write/read lines 28–33 & 16–24)
users.dat unreadable (no plaintext passwords): PASS (file is base64-encoded; passwords hashed). (Files: data_manager.py lines 28–33; users.dat content)
Entering "five" for number of questions does not crash and prompts again: FAIL — code prints error but does not re-prompt (returns early). (File: main.py lines 57–63)
Three correct in a row award exactly 45 points: PASS (quiz_engine.py lines 41–60).
Disliked question removed from next quiz: PASS (quiz_engine.py select filters disliked; main.py feedback lines 127–139 and persistence line 147).
Running with empty question bank prints friendly error and exits with code 1: PASS (main.py lines 160–162 call sys.exit(1)).
Minimal recommended fixes (priority)
Fix numeric re-prompt in take_quiz to loop until valid integer (main.py lines 57–63). (High)
Make load_questions() robust to JSON errors and missing 'questions' key and ensure a single authoritative error message before exit. (High)
Avoid silently returning {} in read_users() when decode fails; surface an error or back up corrupted file. (High)
Replace base64-only obfuscation with at least file-permission hardening and document that base64 is reversible. If stronger protection desired, use encryption (out of scope for small exercise). (Medium)
Disallow blank usernames/passwords in register() (main.py lines 27,31). (Medium)
Reduce broad exception catches and add targeted excepts with informative messages (auth.py/data_manager.py). (Medium)
Consider using prompt_int/prompt_choice consistently to standardize input behavior (main.py lines 6–25). (Low)
Requirements coverage summary
Done: A, B, C, D (mostly), E, F, H (password hashing), I (scoring), Acceptance 1,2,3,5,6,7.
Partial/Fail: Acceptance #4 (numeric re-prompt) — FAIL.
Security/quality issues: base64-only storage, silent corruption handling, broad exception swallowing, blank username acceptance — WARN/needs fix.
Completion summary: The implementation largely implements the spec and scoring logic correctly (notably hashing, streak scoring, liked/disliked filtering, persistence). The main functional failure against acceptance is numeric input behavior in take_quiz (it should re-prompt but currently returns). Several robustness and security improvements are recommended (handle malformed JSON, avoid silent corruption, enforce file permissions, avoid broad exception catches, and disallow empty usernames/passwords).