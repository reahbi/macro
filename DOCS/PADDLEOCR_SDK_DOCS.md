TITLE: Verifying Webhook Signature (Python)
DESCRIPTION: Demonstrates how to verify the signature of an incoming webhook notification using the Paddle Python SDK's Verifier class. It requires importing Secret and Verifier, initializing Verifier, and calling the verify method with the request object and the webhook secret key wrapped in a Secret object. The request object must match the paddle_billing.Notifications.Requests.Request protocol and supports frameworks like Flask and Django.
SOURCE: https://github.com/paddlehq/paddle-python-sdk/blob/main/README.md#_snippet_10

LANGUAGE: python
CODE:
```
from paddle_billing.Notifications import Secret, Verifier

integrity_check = Verifier().verify(request, Secret('WEBHOOK_SECRET_KEY'))
```

----------------------------------------

TITLE: Initializing Paddle Client with Environment Variable (Python)
DESCRIPTION: Initializes the Paddle Billing client by retrieving the API secret key from an environment variable using `os.getenv()`. This method is recommended for security best practices, avoiding hardcoding secrets directly in the code. Requires importing `getenv` and `Client`.
SOURCE: https://github.com/paddlehq/paddle-python-sdk/blob/main/README.md#_snippet_1

LANGUAGE: Python
CODE:
```
from os             import getenv
from paddle_billing import Client

paddle = Client(getenv('PADDLE_API_SECRET_KEY'))
```

----------------------------------------

TITLE: Listing Entities with Pagination (Python)
DESCRIPTION: Demonstrates how to list entities (e.g., products) using the `list()` method on a resource object. The method returns an iterable that automatically handles pagination, allowing iteration over all results without manual page management. Requires an initialized `Client`.
SOURCE: https://github.com/paddlehq/paddle-python-sdk/blob/main/README.md#_snippet_3

LANGUAGE: Python
CODE:
```
from paddle_billing import Client

paddle = Client('PADDLE_API_SECRET_KEY')

products = paddle.products.list()

# list() returns an iterable, so pagination is automatically handled
for product in products:
    print(f"Product's id: {product.id}")
```

----------------------------------------

TITLE: Creating a New Entity (Python)
DESCRIPTION: Illustrates how to create a new entity (e.g., a product) using the `create()` method. This method requires passing a corresponding `CreateOperation` object (like `CreateProduct`) which contains the entity's details. The method returns the newly created entity object. Requires an initialized `Client` and relevant operation/entity classes.
SOURCE: https://github.com/paddlehq/paddle-python-sdk/blob/main/README.md#_snippet_5

LANGUAGE: Python
CODE:
```
from paddle_billing                               import Client
from paddle_billing.Entities.Shared.TaxCategory   import TaxCategory
from paddle_billing.Resources.Products.Operations import CreateProduct

paddle = Client('PADDLE_API_SECRET_KEY')

created_product = paddle.products.create(CreateProduct(
    name         = 'My Product',
    tax_category = TaxCategory.Standard,
))
```

----------------------------------------

TITLE: Getting a Single Entity by ID (Python)
DESCRIPTION: Shows how to retrieve a specific entity (e.g., a product) by its unique ID using the `get()` method on the resource object. The method takes the entity's ID as an argument and returns the corresponding entity object. Requires an initialized `Client`.
SOURCE: https://github.com/paddlehq/paddle-python-sdk/blob/main/README.md#_snippet_4

LANGUAGE: Python
CODE:
```
from paddle_billing import Client

paddle = Client('PADDLE_API_SECRET_KEY')

product = paddle.products.get('PRODUCT_ID')
```

----------------------------------------

TITLE: Deleting an Entity (Python)
DESCRIPTION: Illustrates how to delete an entity, specifically a product, using the Paddle Python SDK. It shows initializing the client with an API key and then calling the delete method on the relevant resource (products) with the entity's ID. The deleted entity is returned.
SOURCE: https://github.com/paddlehq/paddle-python-sdk/blob/main/README.md#_snippet_9

LANGUAGE: python
CODE:
```
from paddle_billing import Client

paddle = Client('PADDLE_API_SECRET_KEY')

deleted_product = paddle.products.delete('PRODUCT_ID')
```

----------------------------------------

TITLE: Verifying Webhook Signature with Time Drift (Python)
DESCRIPTION: Shows how to verify a webhook signature while adjusting the maximum allowed time drift. It involves initializing the Verifier with the desired number of seconds for the time variance (represented by the 'seconds' variable) before calling the verify method. The default time drift variance is 5 seconds.
SOURCE: https://github.com/paddlehq/paddle-python-sdk/blob/main/README.md#_snippet_11

LANGUAGE: python
CODE:
```
integrity_check = Verifier(seconds).verify(request, Secret('WEBHOOK_SECRET_KEY'))
```

----------------------------------------

TITLE: Initializing Paddle Client with API Key (Python)
DESCRIPTION: Initializes the Paddle Billing client using a direct API secret key string. This requires importing the `Client` class from the `paddle_billing` package. The API key is passed as a string argument to the `Client` constructor.
SOURCE: https://github.com/paddlehq/paddle-python-sdk/blob/main/README.md#_snippet_0

LANGUAGE: Python
CODE:
```
from paddle_billing import Client

paddle = Client('PADDLE_API_SECRET_KEY')
```

----------------------------------------

TITLE: Updating a Customer Address (Python)
DESCRIPTION: Shows how to update a customer's address using the Paddle Python SDK. The addresses.update method requires both the customer ID and the address ID, followed by the update operation details (represented by 'operation_goes_here').
SOURCE: https://github.com/paddlehq/paddle-python-sdk/blob/main/README.md#_snippet_8

LANGUAGE: python
CODE:
```
updated_address = paddle.addresses.update(
    'CUSTOMER_ID',
    'ADDRESS_ID',
    operation_goes_here,
)
```

----------------------------------------

TITLE: Initializing Paddle Client for Sandbox Environment (Python)
DESCRIPTION: Initializes the Paddle Billing client specifically for the sandbox environment. This requires importing `Client`, `Environment`, and `Options`. The environment is set by passing an `Options` object with `Environment.SANDBOX` to the `options` parameter of the `Client` constructor.
SOURCE: https://github.com/paddlehq/paddle-python-sdk/blob/main/README.md#_snippet_2

LANGUAGE: Python
CODE:
```
from paddle_billing import Client, Environment, Options

paddle = Client('PADDLE_API_SECRET_KEY', options=Options(Environment.SANDBOX))
```

----------------------------------------

TITLE: Setting up Paddle Python SDK Development Environment (Bash)
DESCRIPTION: Clones the repository, changes into the directory, and installs the package with development dependencies using pip.
SOURCE: https://github.com/paddlehq/paddle-python-sdk/blob/main/CONTRIBUTING.md#_snippet_0

LANGUAGE: bash
CODE:
```
git clone https://github.com/PaddleHQ/paddle-python-sdk && \
cd paddle-python-sdk && \
pip install .[dev]
```

----------------------------------------

TITLE: Running a Specific Pytest Test Case (Bash)
DESCRIPTION: Runs a single, specific test case identified by its file path, class name, and method name, useful for debugging individual tests.
SOURCE: https://github.com/paddlehq/paddle-python-sdk/blob/main/CONTRIBUTING.md#_snippet_5

LANGUAGE: bash
CODE:
```
pytest tests/Unit/Notification/test_Verifier.py::TestVerifier::test_validate_paddle_signature_header_integrity
```

----------------------------------------

TITLE: Installing Pre-commit Hooks for Paddle Python SDK (Bash)
DESCRIPTION: Installs the configured pre-commit hooks after development dependencies have been installed, ensuring codestyle checks run automatically before commits.
SOURCE: https://github.com/paddlehq/paddle-python-sdk/blob/main/CONTRIBUTING.md#_snippet_1

LANGUAGE: bash
CODE:
```
pre-commit install
```

----------------------------------------

TITLE: Formatting Code with Black (Bash)
DESCRIPTION: Runs the Black formatter on the entire project directory (`.`) to automatically reformat code according to the project's codestyle guidelines.
SOURCE: https://github.com/paddlehq/paddle-python-sdk/blob/main/CONTRIBUTING.md#_snippet_6

LANGUAGE: bash
CODE:
```
black .
```

----------------------------------------

TITLE: Running Pytest Tests in a Specific Directory (Bash)
DESCRIPTION: Executes pytest tests only within the specified directory path, allowing for focused testing of a subset of the test suite.
SOURCE: https://github.com/paddlehq/paddle-python-sdk/blob/main/CONTRIBUTING.md#_snippet_4

LANGUAGE: bash
CODE:
```
pytest tests/Unit
```

----------------------------------------

TITLE: Running All Pytest Tests via Venv Activation (Bash)
DESCRIPTION: Changes into the project directory, activates the virtual environment, and then runs all pytest tests using the activated environment's pytest command.
SOURCE: https://github.com/paddlehq/paddle-python-sdk/blob/main/CONTRIBUTING.md#_snippet_3

LANGUAGE: bash
CODE:
```
cd paddle-python-sdk && \
source .venv/bin/activate && \
pytest
```

----------------------------------------

TITLE: Running All Pytest Tests via Venv Path (Bash)
DESCRIPTION: Changes into the project directory and runs all pytest tests using the Python interpreter directly from the virtual environment's bin directory.
SOURCE: https://github.com/paddlehq/paddle-python-sdk/blob/main/CONTRIBUTING.md#_snippet_2

LANGUAGE: bash
CODE:
```
cd paddle-python-sdk && .venv/bin/pytest
```

----------------------------------------

TITLE: Updating a Product Name (Python)
DESCRIPTION: Demonstrates how to update the name of a product using the Paddle Python SDK's products.update method. It requires the product ID and an UpdateProduct object specifying the fields to update.
SOURCE: https://github.com/paddlehq/paddle-python-sdk/blob/main/README.md#_snippet_7

LANGUAGE: python
CODE:
```
updated_product = paddle.products.update('PRODUCT_ID', UpdateProduct(
    name = 'My Improved Product'
))
```

----------------------------------------

TITLE: Updating an Existing Entity (Python)
DESCRIPTION: Shows the initial setup for updating an existing entity (e.g., a product) using the `update()` method. The method requires the entity's ID and a corresponding `UpdateOperation` object. The snippet is incomplete, showing only the imports and client initialization needed before calling `update()`. Requires an initialized `Client` and the relevant operation class.
SOURCE: https://github.com/paddlehq/paddle-python-sdk/blob/main/README.md#_snippet_6

LANGUAGE: Python
CODE:
```
from paddle_billing                        import Client
from paddle_billing.Resources.Products.Operations import UpdateProduct

paddle = Client('PADDLE_API_SECRET_KEY')

```