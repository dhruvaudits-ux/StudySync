from app import app, db
from models import User, Activity

def verify_rating_system():
    with app.test_client() as client:
        with app.app_context():
            user = User.query.filter_by(email='student1@example.com').first()
            if not user:
                print("Error: Test user not found.")
                return
                
            with client.session_transaction() as sess:
                sess['_user_id'] = str(user.id)
                sess['_fresh'] = True
            
            # Hit /activity endpoint
            response = client.get('/activity')
            html = response.get_data(as_text=True)
            
            if "barChart" in html and "pieChart" in html:
                print("Success: Chart canvas IDs found in HTML.")
            else:
                print("Error: Chart.js elements missing.")
                
            if "Current Study Rating" in html:
                print("Success: Scorecard header found.")
            else:
                print("Error: Scorecard header missing.")
                
            # Verify the rating is rendering, e.g. finding "/ 10" since the number is dynamic
            if "/ 10" in html:
                print("Success: Score denominator is rendering correctly.")
                
if __name__ == '__main__':
    verify_rating_system()
