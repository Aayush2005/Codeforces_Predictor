import requests
import math

def fetch_contest_data(contest_id):
    """
    Fetch contest standings data from Codeforces API.
    """
    url = f"https://codeforces.com/api/contest.standings?contestId={contest_id}&from=1&count=500"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        if data['status'] == 'OK':
            return data['result']['rows'], data['result']['contest']
        else:
            raise Exception("API returned an error: " + data['comment'])
    else:
        raise Exception(f"Failed to fetch data. HTTP Status Code: {response.status_code}")


def adjust_ranks(participants):
    """
    Adjust ranks for participants:
    - Exclude unrated participants.
    - Handle ties based on points.
    """
    # Filter out unrated participants
    rated_participants = [p for p in participants if 'rating' in p['party']['members'][0]]
    
    # Sort participants by points (descending), then by rating (descending)
    rated_participants.sort(key=lambda p: (-p['points'], -p.get('rating', 0)))

    # Assign adjusted ranks, accounting for ties
    rank = 1
    for i, participant in enumerate(rated_participants):
        if i > 0 and participant['points'] == rated_participants[i - 1]['points']:
            participant['adjusted_rank'] = rated_participants[i - 1]['adjusted_rank']
        else:
            participant['adjusted_rank'] = rank
        rank += 1
    
    return rated_participants


def calculate_expected_rank(participant, participants):
    """
    Calculate the expected rank of a participant using the Elo formula.
    """
    Ri = participant.get('rating', 0)
    E = 0
    for other in participants:
        Rj = other.get('rating', 0)
        E += 1 / (1 + math.pow(10, (Rj - Ri) / 400))
    return E


def predict_rating_changes(contest_id, user_id):
    """
    Predict rating changes for a given contest for a specific user.
    """
    try:
        # Fetch contest data
        participants, contest = fetch_contest_data(contest_id)
        print(f"Contest: {contest['name']}")

        # Debug: Show the first few participants and their handles
        print("\nFirst few participants (handles):")
        for p in participants[:10]:
            print(p['party']['members'][0]['handle'])

        # Adjust ranks
        participants = adjust_ranks(participants)

        # Find the participant by user ID
        participant = next((p for p in participants if p['party']['members'][0]['handle'] == user_id), None)

        if participant is None:
            print(f"User with ID '{user_id}' not found in this contest.")
            return

        # Calculate expected rank and rating change
        current_rating = participant.get('rating', 0)
        expected_rank = calculate_expected_rank(participant, participants)
        actual_rank = participant['adjusted_rank']
        performance = len(participants) - actual_rank + 1
        rating_change = 40 * (performance - expected_rank)
        new_rating = current_rating + rating_change
        
        # Display the result for the specific user
        print(f"User: {user_id}")
        print(f"Old Rating: {current_rating}")
        print(f"New Rating: {round(new_rating)}")
        print(f"Rating Change: {round(rating_change)}")

    except Exception as e:
        print(f"Error: {e}")


# Example usage
if __name__ == "__main__":
    contest_id = input("Enter the Codeforces contest ID: ")
    user_id = input("Enter the user ID to predict: ")
    predict_rating_changes(contest_id, user_id)
