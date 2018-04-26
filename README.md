# Olist Challenge

This is my take on the dev challenge for Olist. The goal was to implement an API that recorded Call Records and generated Bill Records based on those. The system needed to be flexible on receiving data due to the unclear communication flow of our clients. This project was developed trying to preserve HTTP REST paradigms while attending the requirements for the challenge, and for that some compromises had to be made.


## Project Setup

### Installing
```
# Clone the repository
git clone git@github.com:gerardon/work-at-olist.git

# Create a virtualenv
virtualenv work-at-olist

# Activate the virtualenv
cd work-at-olist
source bin/activate

# Install dependancies
pip install -r dev-requirements.txt

# Create Schema and load db with default data.
python manage.py migrate
python manage.py loaddata fixtures/initial_data.json
```

### Testing
```
# After installation.
python manage.py test
```

### Environment
I tried to minimize the requirements of this project, using as few libraries as possible.
This project was developed using:
`Thinkpad T430` running `Manjaro Linux`
`vim`
`zsh`
`Django 2.0`
`Python 3.6`
`djangorestframework 3.8.2`


## API Documentation

### Call Records List
This endpoint retrieves every Call Record stored.

#### HTTP Request
`GET https://olist-challenge.herokuapp.com/api/call/records/`

#### Example response
`Status Code: 200 OK`
```
[
    {
        "id": 141,
        "type": "start",
        "timestamp": 1513091233,
        "url": "https://olist-challenge.herokuapp.com/api/call/record/141/",
        "call_id": 71,
        "source": "99988526423",
        "destination": "9993468278"
    }
]
```


### Create a Call Record
This endpoint creates a Call Record. If a Call Record with the same unique `id` is already created, it updates that entry instead.

#### HTTP Request
`POST https://olist-challenge.herokuapp.com/api/call/records/`

#### Expected Body
For `start` Call Records:
```
    {
        "id": 141,
        "type": "start",
        "timestamp": 1513091233,
        "call_id": 71,
        "source": "99988526423",
        "destination": "9993468278"
    }
```

For `end` Call Records:
```
    {
        "id": 142,
        "type": "end",
        "timestamp": 1513092233,
        "call_id": 71,
    }
```

Attribute | Accepted Type | Description
--------- | ------------- | -----------
`id` | int | Must be unique, if its not, the endpoint will update the stored entry with that `id` instead.
`type` | str | Must be one of the choices: `"start"` or `"end"`.
`timestamp` | int | Must be a valid UNIX time stamp.
`call_id` | int | Must be unique. Each call can only have one `"start"` and one `"end"` Call Records.
`source` | int/str | Phone number that made the call. The accepted format is AAXXXXXXXXX, where AA is the area code and XXXXXXXXX is the phone number. The phone number is composed of 8 or 9 digits. This is **optional** if it's an `"end"` Call Record.
`destination` | int/str | Phone number that received the call. The accepted format is AAXXXXXXXXX, where AA is the area code and XXXXXXXXX is the phone number. The phone number is composed of 8 or 9 digits. This is **optional** if it's an `"end"` Call Record.

#### Example response
`Status Code: 201 CREATED`
```
    {
        "id": 141,
        "type": "start",
        "timestamp": 1513091233,
        "url": "https://olist-challenge.herokuapp.com/api/call/record/141/",
        "call_id": 71,
        "source": "99988526423",
        "destination": "9993468278"
    }
```

#### Other Responses
Status Code | Description
----------- | -----------
`400` | Bad Request. The request's body is malformated or missing data, inspect the response for further details.


### Retrieve a Call Record
This endpoint retrieves a specific Call Record given its `id`.

#### HTTP Request
`GET https://olist-challenge.herokuapp.com/api/call/record/<:id>/`

#### Example response
`Status Code: 200 OK`
```                                                                                    `
    {
        "id": 141,
        "type": "start",
        "timestamp": 1513091233,
        "url": "https://olist-challenge.herokuapp.com/api/call/record/141/",
        "call_id": 71,
        "source": "99988526423",
        "destination": "9993468278"
    }
```

#### Other Responses
Status Code | Description
----------- | -----------
`404` | Not Found. The requested entity was not found.


### Update a Call Record
This endpoint updates a specific Call Record given its `id`. This will **NOT** update its related Bill Record.

#### HTTP Request
` https://olist-challenge.herokuapp.com/api/call/record/<:id>/`

#### Expected Body
For `start` Call Records:
```
    {
        "id": 141,
        "type": "start",
        "timestamp": 1513091233,
        "url": "https://olist-challenge.herokuapp.com/api/call/record/141/",
        "call_id": 71,
        "source": "99988526423",
        "destination": "9993468278"
    }
```

For `end` Call Records:
```
    {
        "id": 142,
        "type": "end",
        "timestamp": 1513091233,
        "url": "https://olist-challenge.herokuapp.com/api/call/record/141/",
        "call_id": 71
    }

```

Attribute | Accepted Type | Description
--------- | ------------- | -----------
`type` | str | Must be one of the choices: `"start"` or `"end"`.
`timestamp` | int | Must be a valid UNIX time stamp.
`call_id` | int | Must be unique. Each call can only have one `"start"` and one `"end"` Call Records.
`source` | int/str | Phone number that made the call. The accepted format is AAXXXXXXXXX, where AA is the area code and XXXXXXXXX is the phone number. The phone number is composed of 8 or 9 digits. This is **optional** if it's an `"end"` Call Record.
`destination` | int/str | Phone number that received the call. The accepted format is AAXXXXXXXXX, where AA is the area code and XXXXXXXXX is the phone number. The phone number is composed of 8 or 9 digits. This is **optional** if it's an `"end"` Call Record.


#### Example response
`Status Code: 200 OK`
```
    {
        "type": "start",
        "timestamp": 1513091233,
        "url": "https://olist-challenge.herokuapp.com/api/call/record/141/",
        "call_id": 71,
        "source": "99988526423",
        "destination": "9993468278"
    }

```

#### Other Responses
Status Code | Description
----------- | -----------
`400` | Bad Request. The request's body is malformated or missing data, inspect the response for further details.
`404` | Not Found. The requested entity was not found.


### Subscriber Bill Records
This endpoint retrieves the Bill Records given a subscriber.

#### HTTP Request
`GET https://olist-challenge.herokuapp.com/api/bill/<:subscriber>/`


#### Query Parameters

Attribute | Accepted Type | Description
--------- | ------------- | -----------
`subscriber` | int/str | Subscriber phone number. The accepted format is AAXXXXXXXXX, where AA is the area code and XXXXXXXXX is the phone number. The phone number is composed of 8 or 9 digits.
`period` | date | Reference period for the Bill Records. The accepted format is MM/YYYY or `%m/%Y` in strptime. This defaults to the last closed month.


#### Example response
`Status Code: 200 OK`
```
{
    "subscriber": "99988526423",
    "period": "12/2017",
    "bill_records": [
        {
            "id": 6,
            "destination": "9993468278",
            "call_start_date": "12/12/2017",
            "call_start_time": "15:07:58",
            "call_duration": "00:04:58",
            "call_price": "0.72"
        }
    ]
}
```

#### Other Responses
Status Code | Description
----------- | -----------
`400` | Bad Request. The query parameters are malformated or missing data, inspect the response for further details.
