# Coding I - Web Application Encryption and Authentication Project

**Due date:** 4/10

When you finish, add your names and a demo video link here, then submit one link to your project repository.

**Group Members:** Sam and Henry
* [Demo Video (1 per group)](http://includeyourlinkhere)

In this project, you will design and build an app of your own choosing in Python using Flask, with a focus on secure authentication and protecting user content. The project is broken into four major phases, each teaching key skills for building a functional and secure application. At the end, you and your classmates will playtest each other’s apps, with the goal of exposing security weaknesses.

#### [Please Fork this Repo to begin](https://github.com/rlj0713/coding-1-game/fork)
---
### Helpful Links for This Unit:
* [Flask Documentation](https://flask.palletsprojects.com/en/2.3.x/)
* [SQLite Documentation](https://www.sqlite.org/docs.html)
* [Bcrypt Documentation](https://pypi.org/project/bcrypt/)
* [Regex Tutorial for Python](https://docs.python.org/3/library/re.html)
* [GitHub Cheat-Sheet](https://education.github.com/git-cheat-sheet-education.pdf)

---

## Project Requirements:

| Part I: Planning & Design (10 pts) |
|----------|
- Decide on an app idea — it can be anything you want, but the app needs to display content unique to each user.
- Write or sketch out how your app will work and what features it will include.
- Complete the `planning_and_design.txt` file showing your step-by-step plan.
- Do not move forward until you’ve checked your plan with Mr. Jackson.

| Phase II: Build Login & Registration Structure (15 pts) |
|----------|
- Create a basic Flask app with login and registration pages.
- Include fields for username and password.
- Display messages for successful login and errors for incorrect login attempts.
- Add navigation between login and registration pages.
- Add a “secret page” that displays the user’s name after login.

| Phase III: Store Passwords in a Database (20 pts) |
|----------|
- Set up an SQLite database (or other approved database) to store user data.
- Ensure user data persists even when the app is restarted.
- Verify that registration adds users correctly and login checks credentials against the database.

| Phase IV: Encrypt Passwords with Bcrypt (20 pts) |
|----------|
- Use bcrypt to hash passwords before storing them in the database.
- Update login logic to verify passwords against the hashed values.
- Ensure that passwords are never stored in plain text.
- Test registration and login with multiple users.

| Phase V: Require Password Complexity (15 pts) |
|----------|
- Implement password validation rules:
  - At least 1 uppercase letter
  - At least 1 lowercase letter
  - At least 1 number
  - At least 1 special character
- Display a clear error message if the password does not meet the requirements.
- Ensure registration only succeeds if the password passes validation.
- Test with multiple password examples.

| Phase VI: Reflection + Demo Video (20 pts) |
|----------|
- Swap apps with classmates and try to find weaknesses in each other’s authentication or secret content.
- Identify potential security issues (weak passwords, unauthorized access, session bypasses) in a safe, controlled environment.
- Discuss what worked, what failed, and how you would fix vulnerabilities.
- Discuss lessons learned about secure app design and protecting user data.

| Optional Bonus (+10 pts / each) |
|----------|
- Style the pages with CSS to improve the user interface.
- Implement a “Reset Database” button for easy testing.
- Add additional security features (e.g., session timeouts, email verification).
