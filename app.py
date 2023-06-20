import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os
import json

app = Flask(__name__)
CORS(app, origins='*')
openai.api_key = os.environ['OPENAI_API_KEY']

# get city image from Google
google_maps_api_key = os.environ['GOOGLE_API_KEY']


def get_city_image(location):
    # Get photo reference
    get_place_details_url = f"https://maps.googleapis.com/maps/api/place/textsearch/json"

    get_place_id_params = {
        'key': google_maps_api_key,
        'query': location
    }
    response = requests.get(get_place_details_url, params=get_place_id_params)
    photo_reference = json.loads(response.text)['results'][0]['photos'][0]['photo_reference']
    # print('Photo ref:', photo_reference)

    image_url = f'https://maps.googleapis.com/maps/api/place/photo?photo_reference={photo_reference}&maxwidth=600&key={google_maps_api_key}'
    return image_url


@app.route('/', methods=["OPTIONS", "POST"])
def index():
    if request.method == "OPTIONS":
        # Handle CORS preflight request
        response = jsonify({"message": "CORS preflight request successful"})
        response.headers.add("Access-Control-Allow-Origin", "https://relocation-chatgpt.netlify.app")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type")
        response.headers.add("Access-Control-Allow-Methods", "POST")
        return response
    if request.method == "POST":
        form_data = request.get_json()
        location = form_data['location'][0:60]
        language = form_data['language'][0:60]
        affordability = form_data['affordability'] if form_data['affordability'] else "doesn't matter"
        good_weather = form_data['goodWeather'] if form_data['goodWeather'] else "doesn't matter"
        work_life_balance = form_data['workLifeBalance'] if form_data['workLifeBalance'] else "doesn't matter"
        proximity_to_nature = form_data['proximityToNature'] if form_data['proximityToNature'] else "doesn't matter"
        anything_else = form_data['anythingElse'][0:60]
        # print(form_data)

        query_content = f'I want to move to a new city.'\
                        f' Here are the things that matter to me:'\
                        f' location: {location},'\
                        f' language: {language},'\
                        f' affordability: {affordability},'\
                        f' good weather: {good_weather},'\
                        f' work-life balance: {work_life_balance},'\
                        f' proximity to nature: {proximity_to_nature},'\
                        f' additional info: {anything_else}.'\
                        f'Write the answer like a JSON object, like this:'\
                        f'{{'\
                        f'"city":[insert city name here],'\
                        f'"country": [insert country name here],'\
                        f'"reason" : [insert short reason here]'\
                        f'}}'
        # print(query_content)
        chat_completion = openai.ChatCompletion.create(model="gpt-3.5-turbo",
                                                       messages=[{"role": "user", "content": query_content}])
        location_data = chat_completion['choices'][0]['message']['content']
        # print(location_data)
        # location_data = '{"city": "Auckland","country": "New Zealand","reason": "Auckland offers a good balance of affordability, pleasant weather with mild winters and warm summers, and a strong emphasis on work-life balance. While it may not be focused on proximity to nature, it provides a diverse urban environment with a wide range of cultural and recreational opportunities."}'
        location_dict = json.loads(location_data)
        # print(location_dict)
        image_url = get_city_image(f"{location_dict['city']}, {location_dict['country']}")
        location_dict['photoReference'] = image_url
        print(location_dict)
        response = jsonify(destination=json.dumps(location_dict))
        return response


if __name__ == "__main__":
    # app.run(host="127.0.0.1", port=8080, debug=True)
    app.run()
