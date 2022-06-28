from flask import Flask, render_template, request, redirect, url_for, Response
from api import API
from utilities import loc_list_to_human
from boto3 import client
import random
app = Flask(__name__)
api = API()



def get_client():
    return client(
        's3',
        'us-east-2',
        aws_access_key_id='AKIAVUZTQORNYFEQD2FC',
        aws_secret_access_key='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'
    )


@app.route('/download')
def download_file():
    s3 = get_client()
    file = s3.get_object(Bucket='elasticbeanstalk-us-east-2-388265702491', Key='sky.jpeg')
    return Response(
        file['Body'].read(),
        mimetype='jpeg',
        headers={"Content-Disposition": "attachment;filename=sky.jpeg"}
    )


def get_dynamo(loc, min, max, humidity):
    dynamo = client('dynamodb',
                    'us-east-2',
                    aws_access_key_id='AKIAVUZTQORNYFEQD2FC',
                    aws_secret_access_key='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')

    insertion_flag = True
    while insertion_flag:
        try:
            dynamo.put_item(TableName='weatherdatabase',
                            Item={
                                "ID": {"N": str(random.randint(0, 100000000))},
                                "Location": {"S": str(loc)},
                                "Min": {'S': str(min)},
                                "Max": {'S': str(max)},
                                "Humidity": {'S': str(humidity)}})
            insertion_flag = False
        except Exception:
            continue


@app.route('/')
def index():
    return render_template("home_page.html", NotFound=False)


@app.route('/')
def not_found():
    return render_template("home_page.html", NotFound=True)


@app.route('/', methods=['POST'])
def user_input():
    text = request.form['text']
    api.__init__()
    if not api.get_loc(text):
        return redirect(url_for('not_found'))
    return redirect(url_for('search_loc', location=text))

@app.route('/loc/<location>')
def search_loc(location):
    location_list = api.loc_list
    location_list = enumerate(loc_list_to_human(location_list))
    return render_template("choose_location.html", loc_list=location_list)


@app.route('/loc/<location>', methods=['POST'])
def choose_loc(location):
    op = request.form['options']
    return redirect(url_for('weather_present', location=location, option=op))


@app.route('/weather/<location>/<option>')
def weather_present(location, option):
    option = int(option)
    if not api.choose_city(option):  # need to check the return status code
        return redirect(url_for('/'))
    country = api.loc_list[option][1]
    dist = api.loc_list[option][3]
    city = api.loc_list[option][0]
    state = api.loc_list[option][2]
    max_temp = api.max_temp
    min_temp = api.min_temp
    humidity = api.humidity
    status = api.status
    zipped = zip(max_temp.items(), min_temp.items(), humidity.items())
    print(list(zipped))

    print(country, min_temp, max_temp, humidity)
    get_dynamo(country, min_temp, max_temp, humidity)
    return render_template("playground.html",
                           Country=country, State=state, District=dist, City=city,
                           Max_Temp=max_temp, Min_Temp=min_temp, Humidity=humidity,
                           Status=status, ZippedItems=zipped)


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
