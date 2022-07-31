import json
import boto3 #for the API
import logging
from custom_encoder import CustomEncoder

logger = logging.getLogger()
logger.setLevel(logging.INFO)

#def our table with dybamodb
dynamodbTableName = 'user-list'
dynamodb = boto3.resource('dynamodb') #dynamo clients
table = dynamodb.Table(dynamodbTableName)

#def of ours methods
getMethod = 'GET'
postMethod = 'POST'
patchMethod = 'PATCH'
deleteMethod = 'DELETE'
healthPath = '/health'
userPath = '/user'
usersPath = '/users'

#entry point for our lambda function, to get methods
def lambda_handler(event, context): 
    
    #def the function of our handler
    logger.info(event)  #log to the event requesto to see how the request looks like
    httpMethod = event['httpMethod'] #extract our http method from our obj event
    path = event['path'] #extract the path from our obj event
    
    #handling all the scenarios
    if httpMethod == getMethod and path == healthPath:
        response = buildResponse(200)
    elif httpMethod == getMethod and path == userPath: 
        response = getUserById(event['queryStringParameters']['userid']) #we want a single user
    elif httpMethod == getMethod and path == usersPath:
        response = getAllUsers()  #we want all the users
    elif httpMethod == postMethod and path == userPath:
        response = createUser(json.loads(event['body']))  #we want to create a new user
    elif httpMethod == patchMethod and path == userPath: 
        requestBody = json.loads(event['body']) #extract our request body
        response = modifyUser(requestBody['userid'], requestBody['updateKey'], requestBody['updateValue']) #we want to modify an user
    elif httpMethod == deleteMethod and path == userPath:
        requestBody = json.loads(event['body']) #extract our request body
        response = deleteUser(requestBody['userid']) #we want to delete an user
    else:
        response = buildResponse(404, 'Not found')
    
    return response
    
#method to get the user by the id   
def getUserById(userid):
    try: 
        response = table.get_item(
            Key={
                'userid': userid
            }
        )
        if 'Item' in response: 
            return buildResponse(200, response['Item'])
        else:
            return buildResponse(404, {'Message': 'UserId: %s not found' %userid})
    except:
        logger.exception('Error')
        
#method to get all the users 
def getAllUsers(): 
    try:
        response = table.scan()
        result = response['Items']
        
        while 'LastEveluatedKey' in response:
            response = table.scan(ExclusiveStartKey = response['LastEveluatedKey'])
            result.extend(response['Items'])
            
        body = {
            'Users: ': result
        }
        return buildResponse(200, body)
    except:
        logger.exception('Error')
    
 #method to create a new user  
def createUser(requestBody):
    try:
        table.put_item(Item=requestBody)
        body = {
             'Operation' : 'SAVE',
             'Message' : 'SUCCESS',
             'User' : requestBody
             
        }
        return buildResponse(200, body)
    except:
        logger.exception('Error')
        
 #method to modify an user
def modifyUser(userid, updateKey, updateValue):
    try:
        response = table.update_item(
            Key={
                 'userid': userid
            },
            UpdateExpression = 'set %s = :value' % updateKey,
            ExpressionAttributeValues={
                ':value': updateValue
            },
            ReturnValues='UPDATED_NEW'
        )
        
        body = {
            'Operation': 'UPDATE',
            'Message': 'SUCCESS',
            'UpdateExpression': response
        }
        return buildResponse(200, body)
    except:
        logger.exception('Error')     

#method to delete an user        
def deleteUser(userid):
    try:
        response = table.delete_item(
            Key={
                'userid': userid
            },
            ReturnValues='ALL_OLD'
        )
        body = {
            'Operation': 'DELETE',
            'Message': 'SUCCESS',
            'deletedUser': response
        }
        return buildResponse(200, body)
    except:
        logger.exception('Error')      

    
def buildResponse(statusCode, body=None):
    response = {
        'statusCode' : statusCode,
        'headers' : {
            'Content-Type' : 'application/json',
            'Access-Control-Allow-Origin': '*'  #integrate frontend that has different host name
        }
    }
    if body is not None:
        response['body'] = json.dumps(body, cls=CustomEncoder) #custom encoder
    return response
    
    
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
