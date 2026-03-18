from app import app, db
from models import User, PYQ, UserPYQ

def verify_interactions():
    with app.test_client() as client:
        with app.app_context():
            # Get test user
            user = User.query.filter_by(email='student1@example.com').first()
            if not user:
                print("Error: Test user not found.")
                return

            # Get test PYQ
            pyq = PYQ.query.first()
            if not pyq:
                print("Error: No PYQs found.")
                return

            # Ensure clean state
            UserPYQ.query.filter_by(user_id=user.id, pyq_id=pyq.id).delete()
            db.session.commit()

            # Simulate login
            with client.session_transaction() as sess:
                sess['_user_id'] = str(user.id)
                sess['_fresh'] = True
            
            # 1. Test Toggle ON (Completed)
            print(f"Testing 'completed' for PYQ {pyq.id}...")
            response = client.post(f'/pyq/{pyq.id}/interaction', data={'status': 'completed'})
            
            # Check DB
            interaction = UserPYQ.query.filter_by(user_id=user.id, pyq_id=pyq.id).first()
            if interaction and interaction.status == 'completed':
                print("Success: Interaction saved in DB as 'completed'.")
            else:
                print("Error: Interaction not saved in DB correctly.")

            # 2. Test rendering on /pyqs
            html_resp = client.get('/pyqs')
            html = html_resp.get_data(as_text=True)
            if "bg-green-100" in html and "text-green-700" in html:
                print("Success: /pyqs template correctly renders 'completed' state styling.")
            else:
                print("Error: /pyqs template did not render styling correctly.")

            # 3. Test Toggle OFF (Completed)
            print(f"\nTesting toggle OFF for PYQ {pyq.id}...")
            response = client.post(f'/pyq/{pyq.id}/interaction', data={'status': 'completed'})
            
            # Check DB
            interaction_removed = UserPYQ.query.filter_by(user_id=user.id, pyq_id=pyq.id).first()
            if not interaction_removed:
                print("Success: Interaction successfully deleted from DB (toggled off).")
            else:
                print("Error: Interaction still exists in DB.")

            # 4. Cleanup
            UserPYQ.query.filter_by(user_id=user.id, pyq_id=pyq.id).delete()
            db.session.commit()

if __name__ == '__main__':
    verify_interactions()
