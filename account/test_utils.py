"""Use django's Test client to run file based graphql test."""
import json

from django.test import Client, TestCase

DEFAULT_GRAPHQL_URL = "/graphql/"


def file_graphql_query(
        query, op_name=None, input_data=None, variables=None,
        headers=None, files=None, client=None, graphql_url=None,
):
    """
    'Original: https://github.com/lmcgartland/graphene-file-upload'

    Based on: https://www.sam.today/blog/testing-graphql-with-graphene-django/

    Perform file based mutation.

    :param str query: GraphQL query to run
    :param str op_name: If the query is a mutation or named query, you must
        supply the op_name. For annon queries ("{ ... }"), should be None (default).
    :param dict input_data: If provided, the $input variable in GraphQL will be set
        to this value. If both ``input_data`` and ``variables``,
        are provided, the ``input`` field in the ``variables``
        dict will be overwritten with this value. Defaults to None.
    :param dict variables: If provided, the "variables" field in GraphQL will be
        set to this value. Defaults to None.
    :param dict headers: If provided, the headers in POST request to GRAPHQL_URL
        will be set to this value. Defaults to None
    :param dict files: Files to be sent via request.FILES. Defaults to None.
    :param django.test.Client client: Test client. Defaults to django.test.Client.
    :param str graphql_url: URL to graphql endpoint. Defaults to "/graphql"
    :return: Response object from client
    """

    if not files:
        raise ValueError('Missing required argument "files".')

    client = client or Client()
    headers = headers or {}
    variables = variables or {}
    graphql_url = graphql_url or DEFAULT_GRAPHQL_URL
    map_ = {}

    for key in files.keys():
        map_[key] = ['variables.{key}'.format(key=key)]
        if key not in variables:
            variables[key] = None

    body = {'query': query}
    if op_name:
        body['operationName'] = op_name
    if variables:
        body['variables'] = variables
    if input_data:
        if 'variables' in body:
            body['variables']['input'] = input_data
        else:
            body['variables'] = {'input': input_data}

    data = {
        'operations': json.dumps(body),
        'map': json.dumps(map_),
    }

    data.update(files)
    resp = client.post(graphql_url, data, headers=headers)

    return resp
