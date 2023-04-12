import requests
from flask import Flask, render_template
from flask_graphql import GraphQLView
import graphene

# Define the GraphQL schema
class Object(graphene.ObjectType):
    _id = graphene.Float()
    displayTitle = graphene.String()
    description = graphene.String()
    statement = graphene.String()
    category = graphene.String()
    images = graphene.List(graphene.String, width=graphene.Int(), height=graphene.Int())

class Query(graphene.ObjectType):
    objects = graphene.List(Object, limit=graphene.Int(), skip=graphene.Int())

    def resolve_objects(self, info, limit=None, skip=None):
        # Query the MAAS museum's GraphQL API
        query = '''
        {
          objects(limit: %s, skip: %s) {
            _id
            summary
            displayTitle
            description
            statement
            category
            images {
              url(width: %%s, height: %%s)
            }
          }
        }
        ''' % (limit, skip)
        response = requests.post('https://api.maas.museum/graphql', json={'query': query})
        data = response.json()['data']['objects']

        # Convert the response into a list of Object instances
        objects = []
        for item in data:
            images = []
            for image in item['images']:
                images.append(image['url'] % (info.variable_values['width'], info.variable_values['height']))
            objects.append(Object(_id=item['_id'], displayTitle=item['displayTitle'], description=item['description'], statement=item['statement'], category=item['category'], images=images))
        return objects

# Create a Flask app
app = Flask(__name__)

# Add a GraphQL endpoint to the app
app.add_url_rule('/graphql', view_func=GraphQLView.as_view('graphql', schema=graphene.Schema(query=Query), graphiql=True))

# Add a route for the homepage
@app.route('/')
def homepage():
    # Query the MAAS museum's GraphQL API for the first 5 objects
    query = '''
    {
      objects(limit: 5) {
        _id
        summary
        displayTitle
        description
        statement
        category
        images {
          url(width: 400, height: 400)
        }
      }
    }
    '''
    response = requests.post('https://api.maas.museum/graphql', json={'query': query})
    data = response.json()['data']['objects']

    # Render the homepage template with the list of objects
    return render_template('homepage.html', objects=data)

# Run the app
if __name__ == '__main__':
    app.run(debug=True, port=8080)
