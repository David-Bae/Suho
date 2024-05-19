from apps.elder import elder_bp as elder

@elder.route("/counseling", methods=['GET'])
def counseling():
    return "Hello, Counseling!"