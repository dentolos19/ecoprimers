import shelve
import re

class User:
    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password

# add new user
def add_user(username, email, password):

    # email validation
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        print("Invalid email format! Please enter a valid email.")
        return

    # password validation
    if not re.match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$", password):
        print("Password must be at least 8 characters long, include at least one lowercase letter, "
              "one uppercase letter, one number, and one special character.")
        return

    # open storage file
    with shelve.open('data/accounts') as db:
        
        # checking first if user exists already
        if username in db:
            print("User already exists! Click below to login")
        
        else:
            new_user = User(username, email, password)
            db[username] = new_user
            print(f"Account created for {username}")

# authentication for login
def login(username, password):
    
    with shelve.open("data/accounts") as db:
        if username in db:
            user = db[username]

            if user.password == password:
                print(f"Welcome back {username}")
            
            else:
                print("Incorrect password. Try again!")
        
        else:
            print("User not found!")

# testing
if __name__ == "__main__":

    # Example usage
    add_user("zuhair123", "zuhair@gmail.com", "Password@123")
    login("zuhair123", "Password@123")
    login("zuhair123", "wrongpassword")
    login("buddy", "password")
