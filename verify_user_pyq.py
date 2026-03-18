from app import app, db
from models import User, PYQ, UserPYQ

def verify_user_pyq():
    with app.app_context():
        # Clean up first if needed
        UserPYQ.query.delete()
        db.session.commit()
        
        # 1. Get a test user
        user = User.query.filter_by(email='student1@example.com').first()
        if not user:
            print("Error: Test user not found.")
            return
            
        # 2. Get a test PYQ (created in the previous step)
        pyq = PYQ.query.filter_by(subject='Physics', year=2023).first()
        if not pyq:
            # Let's create one if it was removed
            pyq = PYQ(subject="Physics", year=2023, type="PYQ", file_name="physics_2023_pyq.pdf")
            db.session.add(pyq)
            db.session.commit()
            
        print(f"Testing with User: {user.email} and PYQ: {pyq.subject} {pyq.year}")
            
        # 3. Create a UserPYQ interaction
        interaction = UserPYQ(user_id=user.id, pyq_id=pyq.id, status='completed')
        db.session.add(interaction)
        db.session.commit()
        
        # 4. Verify through relationships
        # Refresh user from db to get latest relationships
        db.session.refresh(user)
        
        found_interaction = False
        for user_pyq in user.pyq_interactions:
            if user_pyq.pyq_id == pyq.id and user_pyq.status == 'completed':
                found_interaction = True
                print(f"Success: Found interaction in user.pyq_interactions! Status: {user_pyq.status}")
                
        if not found_interaction:
            print("Error: Could not find the interaction through the User relationship.")
            
        # 5. Clean up interaction
        db.session.delete(interaction)
        db.session.commit()
        print("Success: Cleaned up test UserPYQ interaction.")

if __name__ == '__main__':
    verify_user_pyq()
