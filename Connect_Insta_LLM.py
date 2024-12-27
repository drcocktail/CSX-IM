import test2 as AI    # File name should not have spaces

def connector(user, query):    # user and query are strings
    response = AI.testQuery(user, query)
    return response    # response is a string
    # return "Testing"    #Delete this line after implementing the above commented lines