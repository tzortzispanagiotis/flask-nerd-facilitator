import requests as requests
from flask import Flask, Response, jsonify, request
from marshmallow import Schema, fields, ValidationError
from json import dumps, loads


class RequestSchema(Schema):
    text = fields.Str(required=True)

app = Flask(__name__)
REL_SERVICE_URL = "http://tzortzisails.hopto.org:5555/api"

WIKIPEDIA_TO_WIKIDATA_SERVICE_URI = "https://en.wikipedia.org/w/api.php?action=query&prop=pageprops&format=json&titles="

def rel_service_nerd(text_for_nerd):
    rel_request_payload = {"text": text_for_nerd}
    print(dumps(rel_request_payload))
    x = requests.post(REL_SERVICE_URL, json = rel_request_payload)
    return x.json()


@app.route('/nerd', methods=["POST"])
def nerd():
    request_data = request.json
    schema = RequestSchema()
    try:
        result = schema.load(request_data)
    except ValidationError as err:
        return jsonify(err.messages), 400

    # print(result)
    text_for_nerd = result['text']
    print(text_for_nerd)
    tmp = rel_service_nerd(text_for_nerd)

    wikipedia_to_wikidata = {}
    for disambiguated_element in tmp:
        wikipedia_service_response = requests.get(WIKIPEDIA_TO_WIKIDATA_SERVICE_URI+disambiguated_element[3]).json()
        response_dict =  wikipedia_service_response['query']['pages']
        for key in response_dict.keys():
            wikidata_uri = 'http://wikidata.org/entity/'+response_dict[key]['pageprops']['wikibase_item']
            wikipedia_to_wikidata[disambiguated_element[3]] = wikidata_uri


    final_response = {'disambiguated_entities': []}

    for element in tmp:
        temp = {}
        temp['segment_start_offset'] = element[0]
        temp['segment_length'] = element [1]
        temp['segment'] = element[2]
        temp['uri'] = wikipedia_to_wikidata[element[3]]
        temp['dismbiguation_confidence'] = element[4]
        temp['entity_recognition_confidence'] = element[5]
        temp['tag'] = element[6]
        final_response['disambiguated_entities'].append(temp)


    return Response(response = dumps(final_response), status = 200, mimetype="application/json")


if __name__ == '__main__':
    app.run()
