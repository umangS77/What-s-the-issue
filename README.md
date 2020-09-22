# What's the Issue?

What's the issue is a flask webapp for users to post their issues, much like github.

## Installation

To run the webapp on your local machine

```bash
pip install -r requirements.txt
```
After completing installation
```bash
python3 app.py
```
## Usage

* Users can login using IIIT-CAS email-id and password.
* The homepage has list of issues that users can see about.
* The users are divided into 3 categories:  
1.VIEWER can see the issues  
2.EDITOR can modify the state of the issues + the above  
3.ADMIN can change the role of other users + the above  
* Search filter based on any keywords is provided for issues.  
