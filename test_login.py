from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

email = input("Enter email: ")
password = input("Enter password: ")

response = supabase.auth.sign_in_with_password({
    "email": email,
    "password": password
})

print("\nLogin successful!")
print("User ID:", response.user.id)

print("\nACCESS TOKEN:")
print(response.session.access_token)