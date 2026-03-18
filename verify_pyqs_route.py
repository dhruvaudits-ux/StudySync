from app import app
from models import User

def verify_pyqs_route():
    with app.test_client() as client:
        with app.app_context():
            # Get test user
            user = User.query.filter_by(email='student1@example.com').first()
            if not user:
                print("Error: Test user not found.")
                return

            # Simulate login
            with client.session_transaction() as sess:
                sess['_user_id'] = str(user.id)
                sess['_fresh'] = True
            
            # Fetch without filter
            print("Fetching /pyqs...")
            response = client.get('/pyqs')
            if response.status_code == 200:
                print("Success: /pyqs loaded correctly.")
                html = response.get_data(as_text=True)
                if "Question Bank" in html and "physics_2022.pdf" in html:
                    print("Success: Template rendered and paper is visible!")
                else:
                    print("Error: Template content mismatch.")
            else:
                print(f"Error: Status code {response.status_code}")

            # Fetch with filter
            print("\nFetching /pyqs?subject=Physics...")
            response_filtered = client.get('/pyqs?subject=Physics')
            if response_filtered.status_code == 200:
                print("Success: Filtered route loaded correctly.")
            else:
                print(f"Error: Filtered route gave status code {response_filtered.status_code}")

if __name__ == '__main__':
    verify_pyqs_route()
