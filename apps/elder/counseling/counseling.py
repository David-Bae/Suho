from apps.elder import elder_bp as elder

@elder.route("/counseling", methods=['GET'])
def index_counseling():
    return "Hello, Counseling!"

